"""Regressions: ``--given`` on answer/return/handoff, reverify after a return, quoted ids and spaced anchors."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner, Result
from devkit_agt.features.workflow.cli import cli
from devkit_agt.features.workflow.models.checks import Registry
from testsupport.workflow import write_config

UNIT = ".devkit/transient/work/u"

RUNNER_GATE = """---
id: w
schema_version: 1
checks:
  - { name: ci-passed, class: runner, description: "CI green" }
stages:
  - id: integrate
    human_gate: integration
    exit: [anchor-exists, ci-passed]
---
"""
GIVEN_GATE = """---
id: w
schema_version: 1
gates:
  dev-integration: { answer: given }
checks:
  - { name: merged, class: runner, description: "merged" }
stages:
  - id: approval
    human_gate: dev-integration
    exit: []
  - id: integrate
    exit: [anchor-status-completed]
  - id: merge
    exit: [merged]
next:
  - { workflow: w2 }
---
"""
REVIEW = """---
id: w
schema_version: 1
stages:
  - id: build
    exit: [anchor-exists]
  - id: review
    exit: [envelope-review-passed]
---
"""
SIMPLE = "---\nid: {id}\nschema_version: 1\nstages:\n  - id: s\n    exit: [anchor-exists]\n---\n"


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def _workspace(root: Path, docs: dict[str, str], config: str = "") -> Path:
    defs = root / ".devkit/workflows"
    defs.mkdir(parents=True, exist_ok=True)
    for name, text in docs.items():
        (defs / f"{name}.md").write_text(text)
    write_config(root, f'[workflow]\ndefault = "w"\n{config}')
    assert _run("new", "-w", str(root), "u").exit_code == 0
    return root


def _unit(root: Path, command: str, *extra: str) -> Result:
    """Run ``command`` (space-separated words) on the unit; lint is skipped where the command evaluates."""
    lint = ("--no-lint",) if command in {"next", "answer", "return", "handoff"} else ()
    return _run(*command.split(), "-w", str(root), "--unit", UNIT, *lint, *extra)


# --- --given on answer, return and handoff ------------------------------------------------


def test_answer_given_reaches_the_gate_request_behind_runner_checks(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"w": RUNNER_GATE})
    assert "gate:integration" in _unit(root, "next", "--given", "ci-passed", "--view", "requests").output
    without = _unit(root, "answer", "--request", "gate:integration", "--action", "accept")
    assert without.exit_code == 2 and "(REQUEST_UNKNOWN)" in without.stderr
    given = _unit(root, "answer", "--request", "gate:integration", "--action", "accept", "--given", "ci-passed")
    assert given.exit_code == 0, given.output + given.stderr
    assert "request=gate:integration" in given.output


def test_return_and_handoff_given_match_next_given(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"w": GIVEN_GATE, "w2": SIMPLE.format(id="w2")})
    assert "[STAGE: integrate" in _unit(root, "next", "--given", "dev-integration").output
    refused = _unit(root, "return", "--to", "integrate")
    assert refused.exit_code == 2 and "(RETURN_INVALID)" in refused.stderr
    back = _unit(root, "return", "--to", "integrate", "--given", "dev-integration")
    assert back.exit_code == 0, back.output + back.stderr
    assert "to=integrate" in back.output
    anchor = root / UNIT / "task.md"
    anchor.write_text(anchor.read_text().replace("status: planned", "status: completed"))
    blocked = _unit(root, "handoff")
    assert blocked.exit_code == 2 and "(HANDOFF_NOT_READY)" in blocked.stderr
    done = _unit(root, "handoff", "--workflow", "w2", "--given", "dev-integration", "--given", "merged")
    assert done.exit_code == 0, done.output + done.stderr
    assert "[HANDED_OFF: from=w to=w2" in done.output


# --- reverify --from latest after a return -----------------------------------------------


def test_reverify_from_latest_refuses_a_round_a_return_reopened(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"w": REVIEW})
    findings = tmp_path / "f.yaml"
    findings.write_text("- issue: x\n  evidence: y\n")
    review = _unit(root, "envelope review", "--stage", "review", "--summary", "s", "--findings-file", str(findings))
    assert review.exit_code == 0, review.output + review.stderr
    assert _unit(root, "return", "--to", "build").exit_code == 0
    reverify = _unit(
        root, "envelope reverify", "--stage", "review", "--from", "latest", "--resolve", "all", "--summary", "f"
    )
    assert reverify.exit_code == 2 and "(ENVELOPE_FROM_INVALID)" in reverify.stderr
    assert not (root / UNIT / "envelopes/reverify-01.yaml").exists()


def test_reverify_from_latest_still_closes_a_round_after_an_earlier_return(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"w": REVIEW})
    assert _unit(root, "return", "--to", "build").exit_code == 0
    findings = tmp_path / "f.yaml"
    findings.write_text("- issue: x\n  evidence: y\n")
    review = _unit(root, "envelope review", "--stage", "review", "--summary", "s", "--findings-file", str(findings))
    assert review.exit_code == 0, review.output + review.stderr
    reverify = _unit(
        root, "envelope reverify", "--stage", "review", "--from", "latest", "--resolve", "all", "--summary", "f"
    )
    assert reverify.exit_code == 0, reverify.output + reverify.stderr
    assert "[DONE: build review]" in _unit(root, "next").output


# --- a workflow id that YAML reads as another type ----------------------------------------


def test_bind_quotes_an_id_yaml_would_read_as_a_boolean(tmp_path: Path) -> None:
    root = _workspace(tmp_path, {"w": SIMPLE.format(id="w"), "off": SIMPLE.format(id='"off"')})
    bound = _unit(root, "bind", "--workflow", "off")
    assert bound.exit_code == 0, bound.output + bound.stderr
    assert "workflow: 'off'" in (root / UNIT / "task.md").read_text()
    nxt = _unit(root, "next")
    assert nxt.exit_code == 0, nxt.output + nxt.stderr
    assert "[DONE: s]" in nxt.output


# --- an anchor name with spaces or parentheses --------------------------------------------


def test_anchor_aliases_keep_a_spaced_anchor_name_whole(tmp_path: Path) -> None:
    registry = Registry.build("my (task).md")
    inv, check = registry.resolve_name("anchor-status-completed")
    assert check.name == "frontmatter" and inv.args == ("my (task).md", "status", "completed")
    root = tmp_path
    _workspace(root, {"w": SIMPLE.format(id="w")}, 'anchor = "my task.md"\n')
    nxt = _unit(root, "next")
    assert nxt.exit_code == 0, nxt.output + nxt.stderr
    assert "[DONE: s]" in nxt.output
