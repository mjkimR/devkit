from __future__ import annotations

import json
from pathlib import Path

import devkit_agt.features.workflow.usecases.handoff as handoff_module
import pytest
from click.testing import CliRunner, Result
from devkit_agt.features.workflow import (
    Binding,
    HistoryEntry,
    Options,
    evaluate_definition,
    parse_definition,
    read_binding,
    validate_definition,
    write_binding,
)
from devkit_agt.features.workflow.cli import cli
from devkit_agt.features.workflow.cli.render import render_document, render_evaluation
from devkit_agt.features.workflow.models.checks import CheckClass
from testsupport.workflow import SIMPLE, SIMPLE_UNIT, WORKFLOW, write_config, write_unit

FIRST = """---
id: triage
schema_version: 1
stages:
  - id: decide
    exit: [anchor-exists]
    skills: [wf-decide]
next:
  - { workflow: spec-driven, when: [file-exists(spec.md)], recommended: true }
  - { workflow: hotfix, when: [frontmatter(task.md kind hotfix)] }
  - { workflow: direct-delivery }
---
"""
SPEC_DRIVEN = """---
id: spec-driven
schema_version: 1
stages:
  - id: specify
    exit: [file-exists(spec.md), frontmatter(spec.md status approved)]
    skills: [wf-specify]
---
"""
HOTFIX = SPEC_DRIVEN.replace("id: spec-driven", "id: hotfix").replace("specify", "patch")


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def _opts(root: Path, unit: Path, **kw: object) -> Options:
    base = {"workspace_root": root, "unit_dir": unit, "anchor": "task.md", "skip_lint": True}
    base.update(kw)
    return Options(**base)  # type: ignore[arg-type]


# --- definition ------------------------------------------------------------------


def test_parse_and_validate_next_candidates() -> None:
    doc = parse_definition(FIRST)
    assert [c.workflow for c in doc.next] == ["spec-driven", "hotfix", "direct-delivery"]
    assert doc.next[0].when == ("file-exists(spec.md)",) and doc.next[0].recommended is True
    assert doc.next[2].when == () and doc.next[2].recommended is False
    assert doc.to_dict()["next"][1] == {
        "workflow": "hotfix",
        "when": ["frontmatter(task.md kind hotfix)"],
        "recommended": False,
    }
    assert validate_definition(doc, "task.md") == []
    assert validate_definition(doc, "task.md", known_ids={"triage", "spec-driven", "hotfix", "direct-delivery"}) == []
    problems = {str(p) for p in validate_definition(doc, "task.md", known_ids={"triage", "spec-driven"})}
    assert problems == {
        "next[1].workflow: unknown workflow 'hotfix'",
        "next[2].workflow: unknown workflow 'direct-delivery'",
    }
    assert "[NEXT: spec-driven recommended=yes when=file-exists(spec.md)]" in render_document(doc)


def test_validate_rejects_bad_candidates() -> None:
    text = """---
id: a
schema_version: 1
stages:
  - id: s
    human_gate: handoff
    exit: [anchor-exists]
next:
  - { workflow: a }
  - { workflow: Bad_Name, when: [nope] }
  - { workflow: b }
  - { workflow: b }
---
"""
    problems = {str(p) for p in validate_definition(parse_definition(text), "task.md")}
    for fragment in [
        "s.human_gate: 'handoff' is reserved",
        "next[0].workflow: a workflow cannot hand off to itself",
        "next[1].workflow: 'Bad_Name' must match",
        "next[1].when: unregistered check 'nope'",
        "next[3].workflow: duplicate candidate 'b'",
    ]:
        assert any(fragment in p for p in problems), fragment


# --- binding history ---------------------------------------------------------------


def test_binding_history_round_trip(tmp_path: Path) -> None:
    anchor = tmp_path / "task.md"
    anchor.write_text("---\nid: a\nstatus: planned\n---\n# a\n")
    history = (HistoryEntry("triage", "2026-10-12"),)
    write_binding(anchor, Binding("spec-driven", history))
    assert read_binding(anchor) == Binding("spec-driven", history)
    text = anchor.read_text()
    assert text.count("workflow_history") == 1 and text.endswith("---\n# a\n")
    write_binding(anchor, Binding("hotfix", (*history, HistoryEntry("spec-driven", "2026-10-13"))))
    binding = read_binding(anchor)
    assert [h.workflow for h in binding.history] == ["triage", "spec-driven"]
    assert anchor.read_text().count("workflow_history") == 1
    assert binding.to_dict()["workflow_history"][1] == {
        "workflow": "spec-driven",
        "completed": "2026-10-13",
        "last_decision": 0,
    }


# --- evaluation ----------------------------------------------------------------


def test_handoff_ask_lists_candidates_and_waits(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a", extra="kind: hotfix\n")
    res = evaluate_definition(parse_definition(FIRST), _opts(tmp_path, unit))
    assert res.complete and res.handoff is not None
    h = res.handoff
    assert h.policy == "ask" and h.chosen is None
    assert [(c.workflow, c.eligible) for c in h.candidates] == [
        ("spec-driven", False),
        ("hotfix", True),
        ("direct-delivery", True),
    ]
    assert h.eligible == ("hotfix", "direct-delivery") and h.recommended == ()
    assert res.waiting is not None and res.waiting.class_ == CheckClass.HUMAN and res.waiting.checks == ("handoff",)
    text = render_evaluation(res)
    assert "[STAGE: - complete=true]" in text
    assert (
        "[HANDOFF: policy=ask candidates=spec-driven hotfix direct-delivery eligible=hotfix direct-delivery recommended=- chosen=-]"
        in text
    )
    assert "[CANDIDATE: spec-driven eligible=no recommended=yes when=file-exists(spec.md)=false]" in text
    assert "[CANDIDATE: direct-delivery eligible=yes recommended=no when=-]" in text
    assert "[WAITING: human handoff]" in text
    assert res.to_dict()["handoff"]["eligible"] == ["hotfix", "direct-delivery"]


def test_handoff_auto_picks_first_eligible_and_off_disables(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "spec.md").write_text("---\nstatus: draft\n---\n")
    res = evaluate_definition(parse_definition(FIRST), _opts(tmp_path, unit, approvals={"handoff": "auto"}))
    assert res.handoff is not None and res.handoff.chosen == "spec-driven" and res.waiting is None
    assert res.handoff.recommended == ("spec-driven",)
    assert "chosen=spec-driven]" in render_evaluation(res)

    res = evaluate_definition(parse_definition(FIRST), _opts(tmp_path, unit, approvals={"handoff": "off"}))
    assert res.complete and res.handoff is None and res.waiting is None
    assert "[HANDOFF" not in render_evaluation(res)


def test_handoff_auto_without_eligible_candidate_waits(tmp_path: Path) -> None:
    only_spec = FIRST.replace("  - { workflow: hotfix, when: [frontmatter(task.md kind hotfix)] }\n", "").replace(
        "  - { workflow: direct-delivery }\n", ""
    )
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(parse_definition(only_spec), _opts(tmp_path, unit, approvals={"handoff": "auto"}))
    assert res.handoff is not None and res.handoff.chosen is None and res.handoff.policy == "auto"
    assert res.waiting is not None and res.waiting.checks == ("handoff",)


def test_no_handoff_before_completion_or_without_candidates(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(parse_definition(WORKFLOW), _opts(tmp_path, unit))
    assert not res.complete and res.handoff is None
    res = evaluate_definition(parse_definition(SPEC_DRIVEN), _opts(tmp_path, unit))
    assert not res.complete and res.handoff is None


# --- CLI -----------------------------------------------------------------------


def _chain_workspace(tmp_path: Path, policy: str = "ask") -> Path:
    defs = tmp_path / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "triage.md").write_text(FIRST)
    (defs / "spec-driven.md").write_text(SPEC_DRIVEN)
    (defs / "hotfix.md").write_text(HOTFIX)
    (defs / "direct-delivery.md").write_text(WORKFLOW)
    write_config(tmp_path, f'schema = 1\n[workflow]\ndefault = "triage"\n[workflow.approvals]\nhandoff = "{policy}"\n')
    return tmp_path


def test_cli_handoff_ask_flow(tmp_path: Path) -> None:
    root = _chain_workspace(tmp_path)
    assert _run("new", "-w", str(root), "login", "--date", "2026-10-12").exit_code == 0
    unit = ".devkit/transient/work/login"

    nxt = _run("next", "-w", str(root), "--unit", unit, "--no-lint")
    assert nxt.exit_code == 0, nxt.output
    assert "[HANDOFF: policy=ask" in nxt.output and "[WAITING: human handoff]" in nxt.output

    undecided = _run("handoff", "-w", str(root), "--unit", unit, "--no-lint")
    assert undecided.exit_code == 2 and "(HANDOFF_CHOICE_REQUIRED)" in undecided.stderr
    assert "[ACTION] INTERACTION" in undecided.stderr
    assert "[DETAIL] spec-driven: eligible=false recommended=true" in undecided.stderr

    bad = _run("handoff", "-w", str(root), "--unit", unit, "--no-lint", "--workflow", "nope")
    assert bad.exit_code == 2 and "(HANDOFF_INVALID)" in bad.stderr
    ineligible = _run("handoff", "-w", str(root), "--unit", unit, "--no-lint", "--workflow", "spec-driven")
    assert ineligible.exit_code == 2 and "(HANDOFF_INELIGIBLE)" in ineligible.stderr

    (root / unit / "spec.md").write_text("---\nstatus: draft\n---\n")
    done = _run(
        "handoff", "-w", str(root), "--unit", unit, "--no-lint", "--workflow", "spec-driven", "--date", "2026-10-13"
    )
    assert done.exit_code == 0, done.output
    assert done.output.startswith("[HANDOFF: from=triage to=spec-driven policy=")
    # An explicit choice is recorded as the handoff decision.
    assert "policy=ask decision=decisions/01-handoff.yaml]" in done.output
    assert "[HISTORY: triage]" in done.output
    anchor = (root / unit / "task.md").read_text()
    assert "workflow: spec-driven" in anchor and "workflow_history: [{workflow: triage, completed:" in anchor
    assert "completed: '2026-10-13'" in anchor and anchor.endswith("---\n# login\n")

    # The unit now follows spec-driven from its first stage; triage is history, not re-evaluated.
    nxt = _run("next", "-w", str(root), "--unit", unit, "--no-lint")
    assert "[WORKFLOW: spec-driven" in nxt.output and "[STAGE: specify" in nxt.output and "[HANDOFF" not in nxt.output
    listed = json.loads(_run("list", "-w", str(root), "--format", "json").stdout)["units"]
    assert listed[0]["workflow"] == "spec-driven" and listed[0]["history"] == "triage"

    # Completing spec-driven: no candidates, so no handoff and HANDOFF_NONE on request.
    (root / unit / "spec.md").write_text("---\nstatus: approved\n---\n")
    nxt = _run("next", "-w", str(root), "--unit", unit, "--no-lint")
    assert "[STAGE: - complete=true]" in nxt.output and "[HANDOFF" not in nxt.output
    none = _run("handoff", "-w", str(root), "--unit", unit, "--no-lint")
    assert none.exit_code == 2 and "(HANDOFF_NONE)" in none.stderr


def test_cli_handoff_auto_and_not_ready_and_off(tmp_path: Path) -> None:
    root = _chain_workspace(tmp_path, policy="auto")
    _run("new", "-w", str(root), "login")
    unit = ".devkit/transient/work/login"
    (root / unit / "spec.md").write_text("---\nstatus: draft\n---\n")
    nxt = _run("next", "-w", str(root), "--unit", unit, "--no-lint", "--format", "json")
    assert json.loads(nxt.stdout)["handoff"]["chosen"] == "spec-driven"

    done = _run("handoff", "-w", str(root), "--unit", unit, "--no-lint", "--format", "json")
    assert done.exit_code == 0, done.output
    payload = json.loads(done.stdout)
    assert (payload["from"], payload["to"], payload["policy"]) == ("triage", "spec-driven", "auto")
    assert payload["history"][0]["workflow"] == "triage"

    not_ready = _run("handoff", "-w", str(root), "--unit", unit, "--no-lint")
    assert (
        not_ready.exit_code == 2
        and "(HANDOFF_NOT_READY)" in not_ready.stderr
        and "stage specify is current" in not_ready.stderr
    )

    write_config(root, 'schema = 1\n[workflow]\ndefault = "triage"\n[workflow.approvals]\nhandoff = "off"\n')
    _run("new", "-w", str(root), "other")
    off = _run("handoff", "-w", str(root), "--unit", ".devkit/transient/work/other", "--no-lint")
    assert off.exit_code == 2 and "(HANDOFF_OFF)" in off.stderr


def test_cli_handoff_auto_undecided(tmp_path: Path) -> None:
    root = _chain_workspace(tmp_path, policy="auto")
    (root / ".devkit/workflows/triage.md").write_text(
        FIRST.replace("  - { workflow: hotfix, when: [frontmatter(task.md kind hotfix)] }\n", "").replace(
            "  - { workflow: direct-delivery }\n", ""
        )
    )
    _run("new", "-w", str(root), "login")
    undecided = _run("handoff", "-w", str(root), "--unit", ".devkit/transient/work/login", "--no-lint")
    assert undecided.exit_code == 2 and "(HANDOFF_UNDECIDED)" in undecided.stderr


def test_cli_validate_reports_unknown_candidate(tmp_path: Path) -> None:
    root = _chain_workspace(tmp_path)
    (root / ".devkit/workflows/hotfix.md").unlink()
    result = _run("validate", "-w", str(root))
    assert result.exit_code == 1 and "next[1].workflow: unknown workflow 'hotfix'" in result.output
    show = _run("show", "-w", str(root), "triage")
    assert show.exit_code == 1 and "[NEXT: hotfix recommended=no" in show.output and "[PROBLEM: next[1]" in show.output


@pytest.mark.parametrize("failure", [OSError("disk full"), KeyboardInterrupt()])
def test_a_failed_explicit_handoff_removes_the_record_it_wrote(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: BaseException
) -> None:
    defs = tmp_path / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "a.md").write_text(SIMPLE.format(id="a", check="anchor-exists")[:-4] + "next:\n  - { workflow: b }\n---\n")
    (defs / "b.md").write_text(SIMPLE.format(id="b", check="anchor-exists"))
    write_config(tmp_path, '[workflow]\ndefault = "a"\n')
    assert _run("new", "-w", str(tmp_path), "u").exit_code == 0
    anchor = (tmp_path / SIMPLE_UNIT / "task.md").read_text()
    written: list[str] = []

    def rewrite_fails(*_: object) -> None:
        # The decision record is already written when the anchor rewrite fails.
        written.extend(p.name for p in (tmp_path / SIMPLE_UNIT / "decisions").iterdir())
        raise failure

    monkeypatch.setattr(handoff_module, "replace_text", rewrite_fails)
    result = _run("handoff", "-w", str(tmp_path), "--unit", SIMPLE_UNIT, "--workflow", "b", "--no-lint")
    assert result.exit_code != 0
    assert written == ["01-handoff.yaml"]
    assert (tmp_path / SIMPLE_UNIT / "task.md").read_text() == anchor
    assert list((tmp_path / SIMPLE_UNIT / "decisions").iterdir()) == []
