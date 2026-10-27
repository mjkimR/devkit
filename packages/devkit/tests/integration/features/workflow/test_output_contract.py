"""The agent output contract of ``devkit workflow`` (ARCH-08-1, CAP-ADV §8): runnable fixes, each advisory once,
documented sentinels with one meaning each, and targets on input errors."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner, Result
from devkit_agt.features.workflow.cli import cli
from testsupport.workflow import SIMPLE_UNIT, simple_workspace, write_config, write_record, write_unit

PLACEHOLDER = re.compile(r"<[a-z][a-z|_ -]*>")

TRIAGE = """---
id: triage
schema_version: 1
stages:
  - id: decide
    exit: [anchor-exists]
next:
  - { workflow: spec-driven, when: [file-exists(spec.md)], recommended: true }
  - { workflow: hotfix }
  - { workflow: direct-delivery }
---
"""
TARGET = "---\nid: {id}\nschema_version: 1\nstages:\n  - id: s\n    exit: [file-exists(never.md)]\n---\n"
GATED = """---
id: w
schema_version: 1
stages:
  - id: build
    exit: [anchor-exists]
  - id: accept
    human_gate: accept
    exit: [anchor-exists]
---
"""
QUESTIONS = """\
- id: q1
  title: Storage format
  prompt: Which format should settings use?
  options:
    - { id: a, description: Keep TOML, recommended: true }
    - { id: b, description: Switch to JSON }
"""


def _run(*args: str, stdin: str | None = None) -> Result:
    return CliRunner().invoke(cli, list(args), input=stdin)


def _fix(stderr: str) -> str:
    """The ``[FIX]`` text of the (last) advisory block, continuation lines joined."""
    lines = stderr.splitlines()
    out: list[str] = []
    for i, line in enumerate(lines):
        if line.startswith("[FIX]"):
            out = [line[len("[FIX]") :].strip()]
            for more in lines[i + 1 :]:
                if not more.startswith(" " * 9):
                    break
                out.append(more.strip())
    return " ".join(out)


def _lines(stderr: str, sentinel: str) -> list[str]:
    return [line[len(sentinel) :].strip() for line in stderr.splitlines() if line.startswith(sentinel)]


def _runnable(fix: str) -> None:
    assert fix and not PLACEHOLDER.search(fix), fix


def _chain(root: Path, policy: str = "ask") -> str:
    defs = root / ".devkit/workflows"
    defs.mkdir(parents=True, exist_ok=True)
    (defs / "triage.md").write_text(TRIAGE)
    for wid in ("spec-driven", "hotfix", "direct-delivery"):
        (defs / f"{wid}.md").write_text(TARGET.format(id=wid))
    write_config(root, f'schema = 1\n[workflow]\ndefault = "triage"\n[workflow.approvals]\nhandoff = "{policy}"\n')
    assert _run("new", "-w", str(root), "login").exit_code == 0
    return ".devkit/transient/work/login"


def _gated(root: Path) -> str:
    defs = root / ".devkit/workflows"
    defs.mkdir(parents=True, exist_ok=True)
    (defs / "w.md").write_text(GATED)
    write_config(root, 'schema = 1\n[workflow]\ndefault = "w"\n')
    assert _run("new", "-w", str(root), "u").exit_code == 0
    return SIMPLE_UNIT


# -- 1. runnable fixes ---------------------------------------------------------------------------------------------------


def test_show_unknown_workflow_names_the_discovered_ids(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    result = _run("show", "-w", str(root), "nope")
    assert result.exit_code == 2 and "(WORKFLOW_NOT_FOUND)" in result.stderr
    fix = _fix(result.stderr)
    _runnable(fix)
    assert ("--workflow" not in fix and "w" in fix.split()[-1]) or "(w)" in fix


def test_request_unknown_names_the_unit_and_targets_the_flag(tmp_path: Path) -> None:
    unit = _gated(tmp_path)
    for request in ("nope", "gate:other"):
        result = _run("answer", "-w", str(tmp_path), "--unit", unit, "--request", request, "--action", "accept")
        assert result.exit_code == 2 and "(REQUEST_UNKNOWN)" in result.stderr
        assert _fix(result.stderr) == f"uv run devkit workflow next --view requests --unit {unit}"
        assert _lines(result.stderr, "[TARGET]") == ["--request"]


def test_handoff_choice_required_lists_one_command_per_eligible_candidate(tmp_path: Path) -> None:
    unit = _chain(tmp_path)
    result = _run("handoff", "-w", str(tmp_path), "--unit", unit, "--no-lint")
    assert result.exit_code == 2 and "(HANDOFF_CHOICE_REQUIRED)" in result.stderr
    _runnable(_fix(result.stderr))
    details = _lines(result.stderr, "[DETAIL]")
    assert details == [
        f"uv run devkit workflow answer --unit {unit} --request handoff --action accept --value {wid}"
        for wid in ("hotfix", "direct-delivery")
    ]


def test_handoff_ignored_choice_and_undecided_fixes_name_the_unit(tmp_path: Path) -> None:
    unit = _chain(tmp_path)
    write_record(tmp_path / unit, "01-handoff.yaml", request="handoff", kind="choose", action="accept", value="nope", workflow="triage")  # fmt: skip
    data = json.loads(_run("next", "-w", str(tmp_path), "--unit", unit, "--no-lint", "--format", "json").stdout)
    ignored = next(e for e in data["errors"] if e["code"] == "HANDOFF_CHOICE_IGNORED")
    _runnable(ignored["advisory"]["fix"])
    assert f"--unit {unit}" in ignored["advisory"]["fix"]

    other = tmp_path / "auto"
    unit = _chain(other, policy="auto")
    (other / ".devkit/workflows/triage.md").write_text(TRIAGE.split("  - { workflow: hotfix }")[0] + "---\n")
    result = _run("handoff", "-w", str(other), "--unit", unit, "--no-lint")
    assert "(HANDOFF_UNDECIDED)" in result.stderr
    fix = _fix(result.stderr)
    _runnable(fix)
    assert f"uv run devkit workflow handoff --unit {unit}" in fix


def test_reverify_out_of_range_lists_the_carried_findings(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    _run("new", "-w", str(root), "u")
    findings = "- { issue: first, evidence: a.py:1 }\n- { issue: second, evidence: b.py:2 }\n"
    review = _run("envelope", "review", "-w", str(root), "--unit", SIMPLE_UNIT, "--summary", "s", "--findings-file", "-", stdin=findings)  # fmt: skip
    assert review.exit_code == 0, review.stderr
    result = _run("envelope", "reverify", "-w", str(root), "--unit", SIMPLE_UNIT, "--from", "latest", "--resolve", "9")
    assert result.exit_code == 2 and "(ENVELOPE_FLAG_INVALID)" in result.stderr
    _runnable(_fix(result.stderr))
    assert "envelope check" not in _fix(result.stderr)
    assert _lines(result.stderr, "[DETAIL]") == ['1: open "first"', '2: open "second"']
    assert _lines(result.stderr, "[TARGET]") == ["--resolve"]


def test_reference_and_question_fixes_are_per_command(tmp_path: Path) -> None:
    unit = _gated(tmp_path)
    asked = _run("envelope", "worker", "-w", str(tmp_path), "--unit", unit, "--stage", "accept", "--summary", "q", "--questions-file", "-", stdin=QUESTIONS)  # fmt: skip
    assert asked.exit_code == 0, asked.stderr
    answer = _run("envelope", "answer", "-w", str(tmp_path), "--unit", unit, "--answers-to", "worker-09.yaml", "--settle", "1=x")  # fmt: skip
    assert "(ENVELOPE_REFERENCE_INVALID)" in answer.stderr
    assert "--resolves" not in _fix(answer.stderr) and _lines(answer.stderr, "[TARGET]") == ["--answers-to"]
    assert _lines(answer.stderr, "[DETAIL]") == ["--answers-to worker-01.yaml"]
    resolution = _run("envelope", "resolution", "-w", str(tmp_path), "--unit", unit, "--resolves", "worker-01.yaml", "--summary", "x")  # fmt: skip
    assert "(ENVELOPE_REFERENCE_INVALID)" in resolution.stderr
    assert "--answers-to" not in _fix(resolution.stderr) and _lines(resolution.stderr, "[TARGET]") == ["--resolves"]

    question = _run("answer", "-w", str(tmp_path), "--unit", unit, "--request", "question:worker-01.q1", "--action", "accept", "--value", "a")  # fmt: skip
    assert "(DECISION_INVALID)" in question.stderr
    fix = _fix(question.stderr)
    _runnable(fix)
    assert fix.endswith(f"envelope answer --unit {unit} --answers-to worker-01.yaml --answers-file -")
    assert _lines(question.stderr, "[TARGET]") == ["--request"]


def test_malformed_envelope_fix_names_the_unit_not_a_repository_document(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    _run("new", "-w", str(root), "u")
    (root / SIMPLE_UNIT / "envelopes/review-01.yaml").write_text("kind: review\n")
    result = _run("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert result.exit_code == 1 and "(ENVELOPE_INVALID)" in result.stderr
    fix = _fix(result.stderr)
    _runnable(fix)
    assert "docs/" not in fix and f"--unit {SIMPLE_UNIT}" in fix


def test_other_fixes_carry_no_placeholders(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    _run("new", "-w", str(root), "u")
    missing = _run("next", "-w", str(root), "--unit", "nowhere")
    assert "(UNIT_NOT_FOUND)" in missing.stderr
    _runnable(_fix(missing.stderr))

    (root / ".devkit/workflows/p.md").write_text(
        "---\nid: p\nschema_version: 1\nlayout:\n  anchor: proposal.md\nstages:\n  - id: s\n    exit: [anchor-exists]\n---\n"
    )
    (root / SIMPLE_UNIT / "proposal.md").write_text("---\nid: u\nworkflow: p\n---\n")
    ambiguous = _run("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint")
    assert "(ANCHOR_AMBIGUOUS)" in ambiguous.stderr
    _runnable(_fix(ambiguous.stderr))
    assert _lines(ambiguous.stderr, "[DETAIL]") == [
        f"uv run devkit workflow next -w {root} --unit {SIMPLE_UNIT} --no-lint --anchor {anchor}"
        for anchor in ("task.md", "proposal.md")
    ]

    settle = _run("envelope", "answer", "-w", str(root), "--unit", SIMPLE_UNIT, "--anchor", "task.md", "--answers-to", "worker-01.yaml", "--settle", "x")  # fmt: skip
    assert "(ENVELOPE_FLAG_INVALID)" in settle.stderr and "TOML" not in settle.stderr
    assert _lines(settle.stderr, "[TARGET]") == ["--settle"]
    tried = _run("envelope", "worker", "-w", str(root), "--unit", SIMPLE_UNIT, "--anchor", "task.md", "--stage", "s", "--tried", "x")  # fmt: skip
    assert "(ENVELOPE_FLAG_INVALID)" in tried.stderr
    _runnable(_fix(tried.stderr))
    feedback = _run("answer", "-w", str(root), "--unit", SIMPLE_UNIT, "--anchor", "task.md", "--request", "feedback:x", "--action", "accept")  # fmt: skip
    assert "(DECISION_INVALID)" in feedback.stderr
    _runnable(_fix(feedback.stderr))
    assert _lines(feedback.stderr, "[TARGET]") == ["--value"]


# -- 2. each advisory once -------------------------------------------------------------------------------------------------


def test_a_failed_lint_run_is_reported_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import devkit_agt.features.rules

    def broken(*_: object, **__: object) -> None:
        raise RuntimeError("rule exploded")

    root = simple_workspace(tmp_path, check="lint-clean")
    _run("new", "-w", str(root), "u")
    monkeypatch.setattr(devkit_agt.features.rules, "run_project_rules", broken)
    result = _run("next", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert result.exit_code == 2
    assert "rule exploded" not in result.stdout and "[LINT_ERROR" not in result.stdout
    assert '[CHECK: lint-clean class=lint evaluated=yes detail="lint failed: UNEXPECTED_ERROR"]' in result.stdout
    assert result.stderr.count("rule exploded") == 1
    requests = _run("next", "--view", "requests", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert requests.stdout.splitlines() == ["[OK: no open requests]"] and requests.exit_code == 2


def test_envelope_check_reports_a_malformed_file_on_stderr_only(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    _run("new", "-w", str(root), "u")
    (root / SIMPLE_UNIT / "envelopes/review-01.yaml").write_text("kind: review\n")
    result = _run("envelope", "check", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert result.exit_code == 1 and "ENVELOPE_ERROR" not in result.stdout
    assert result.stderr.count("(ENVELOPE_INVALID)") == 1
    assert _lines(result.stderr, "[TARGET]") == [f"{SIMPLE_UNIT}/envelopes/review-01.yaml"]


# -- 4. one name, one meaning; one path base ------------------------------------------------------------------------------


def test_handoff_prints_its_own_kind(tmp_path: Path) -> None:
    unit = _chain(tmp_path)
    result = _run("handoff", "-w", str(tmp_path), "--unit", unit, "--no-lint", "--workflow", "hotfix", "--date", "2026-10-13")  # fmt: skip
    assert result.exit_code == 0, result.stderr
    assert result.stdout.splitlines() == [
        "[HANDED_OFF: from=triage to=hotfix policy=ask decision=decisions/01-handoff.yaml]",
        "[HISTORY: triage]",
    ]


def test_show_marks_a_stage_off_as_skipped(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    write_config(root, '[workflow]\ndefault = "w"\n[workflow.stages]\ns = "off"\n')
    result = _run("show", "-w", str(root), "w")
    assert "[SKIPPED: s reason=stages.s=off]" in result.stdout and "[SKIP:" not in result.stdout


def test_authoring_prints_unit_relative_paths(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    _run("new", "-w", str(root), "u")
    skeleton = _run("envelope", "review", "-w", str(root), "--unit", SIMPLE_UNIT)
    assert (
        skeleton.stdout.strip()
        == "[ENVELOPE: envelopes/review-01.yaml kind=review seq=01 status=needs_input skeleton=yes]"
    )
    data = json.loads(_run("envelope", "review", "-w", str(root), "--unit", SIMPLE_UNIT, "--summary", "s", "--format", "json").stdout)  # fmt: skip
    assert data["file"] == "envelopes/review-02.yaml" and data["unit"] == SIMPLE_UNIT and data["skeleton"] is False
    worker = _run("envelope", "worker", "-w", str(root), "--unit", SIMPLE_UNIT, "--stage", "s", "--summary", "done")
    assert worker.stdout.strip() == "[ENVELOPE: envelopes/worker-01.yaml kind=worker seq=01 status=completed]"
    review = _run("envelope", "review", "-w", str(root), "--unit", SIMPLE_UNIT, "--summary", "s")
    assert review.stdout.strip().endswith("status=completed open_findings=0]")


# -- 5. formatting -------------------------------------------------------------------------------------------------------


def test_empty_list_and_booleans_use_ok_and_yes_no(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    write_config(root, '[workflow]\ndefault = "w"\nwork_dir = "my work, here"\n')
    empty = _run("list", "-w", str(root))
    assert empty.stdout.strip() == '[OK: no units dirs="my work, here"]'
    write_config(root, '[workflow]\ndefault = "w"\n')
    _run("new", "-w", str(root), "u")
    done = _run("next", "-w", str(root), "--unit", SIMPLE_UNIT, "--no-lint")
    assert "[STAGE: - complete=yes]" in done.stdout

    unit = _chain(tmp_path / "chain")
    nxt = _run("next", "-w", str(tmp_path / "chain"), "--unit", unit, "--no-lint").stdout
    assert "[CANDIDATE: spec-driven eligible=no recommended=yes" in nxt


# -- 6. modes and targets ----------------------------------------------------------------------------------------------------


def test_handoff_preconditions_ask_the_user(tmp_path: Path) -> None:
    unit = _gated(tmp_path)
    not_ready = _run("handoff", "-w", str(tmp_path), "--unit", unit, "--no-lint")
    assert "(HANDOFF_NOT_READY)" in not_ready.stderr and "[ACTION] INTERACTION" in not_ready.stderr
    assert _fix(not_ready.stderr) == f"uv run devkit workflow next --unit {unit}"

    unit = _chain(tmp_path / "held")
    (tmp_path / "held" / unit / "envelopes").mkdir(exist_ok=True)
    (tmp_path / "held" / unit / "envelopes/worker-01.yaml").write_text(
        yaml.safe_dump(
            {
                "kind": "worker",
                "stage": "decide",
                "status": "failed",
                "summary": "x",
                "problem": {"cause": "c", "recovery": "r"},
            }
        )
    )
    held = _run("handoff", "-w", str(tmp_path / "held"), "--unit", unit, "--no-lint", "--workflow", "hotfix")
    assert held.exit_code == 1 and "(HANDOFF_HELD)" in held.stderr and "[ACTION] INTERACTION" in held.stderr


def test_input_errors_target_their_flag(tmp_path: Path) -> None:
    unit = _gated(tmp_path)
    ws = ("-w", str(tmp_path), "--unit", unit)
    cases = {
        ("return", *ws, "--to", "nope"): ("RETURN_INVALID", "--to"),
        ("next", *ws, "--given", "nope"): ("GIVEN_INVALID", "--given"),
        ("envelope", "reverify", *ws, "--from", "nope.yaml"): ("ENVELOPE_FROM_INVALID", "--from"),
        ("envelope", "review", *ws, "--findings-file", "-", "--summary", "s"): (
            "ENVELOPE_FLAG_INVALID",
            "--findings-file",
        ),
    }
    for args, (code, target) in cases.items():
        result = _run(*args, stdin="")
        assert f"({code})" in result.stderr, (args, result.stderr)
        assert _lines(result.stderr, "[TARGET]") == [target], (args, result.stderr)
        _runnable(_fix(result.stderr))
    assert not (tmp_path / unit / "envelopes/review-01.yaml").exists()
    chain = _chain(tmp_path / "chain")
    invalid = _run("handoff", "-w", str(tmp_path / "chain"), "--unit", chain, "--no-lint", "--workflow", "nope")
    assert "(HANDOFF_INVALID)" in invalid.stderr and _lines(invalid.stderr, "[TARGET]") == ["--workflow"]


# -- 7.-9. list errors, per-kind options, context -----------------------------------------------------------------------------


def test_list_reports_a_broken_anchor_briefly_and_under_errors(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    write_unit(root, ".devkit/transient/work/bad").joinpath("task.md").write_text("---\nstatus: [x\n---\n")
    text = _run("list", "-w", str(root)).stdout
    assert "\\n" not in text and "(ANCHOR_INVALID)" not in text and 'error="' in text
    data = json.loads(_run("list", "-w", str(root), "--format", "json").stdout)
    assert [e["code"] for e in data["errors"]] == ["ANCHOR_INVALID"]
    assert data["units"][0]["error"]["code"] == "ANCHOR_INVALID"


def test_answer_and_resolution_offer_only_their_fields(tmp_path: Path) -> None:
    for kind in ("answer", "resolution"):
        help_text = _run("envelope", kind, "--help").stdout
        for option in ("--status", "--check", "--base", "--head"):
            assert option not in help_text, (kind, option)
        assert "--stage" in help_text and "--summary" in help_text


def test_a_pending_gate_is_reported_without_a_redundant_check_line(tmp_path: Path) -> None:
    unit = _gated(tmp_path)
    out = _run("next", "-w", str(tmp_path), "--unit", unit, "--no-lint").stdout
    assert "[GATE: accept policy=ask satisfied=no source=-]" in out and "[WAITING: human gate:accept]" in out
    assert "[CHECK: gate:accept" not in out and "[UNMET: gate:accept]" in out
