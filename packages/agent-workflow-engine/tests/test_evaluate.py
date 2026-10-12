from __future__ import annotations

from pathlib import Path

import pytest
from agent_workflow_engine import Options, UnitNotFoundError, evaluate, parse, render_result, schema_hash
from agent_workflow_engine.checks import CheckClass
from conftest import WORKFLOW, write_unit

DOC = parse(WORKFLOW)


def _opts(root: Path, unit: Path, **kw: object) -> Options:
    base = {"workspace_root": root, "unit_dir": unit, "anchor": "task.md", "skip_lint": True}
    base.update(kw)
    return Options(**base)  # type: ignore[arg-type]


def _write_env(unit: Path, name: str, body: str) -> None:
    (unit / "envelopes").mkdir(exist_ok=True)
    (unit / "envelopes" / name).write_text(body)


def test_missing_anchor_raises(tmp_path: Path) -> None:
    with pytest.raises(UnitNotFoundError):
        evaluate(DOC, _opts(tmp_path, tmp_path / "nope"))


def test_gate_ask_blocks_until_given(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate(DOC, _opts(tmp_path, unit))
    assert res.stage is not None and res.stage.id == "intent"
    assert [u.name for u in res.unmet] == ["gate:direction"]
    assert res.gate is not None and (res.gate.name, res.gate.policy, res.gate.given) == ("direction", "ask", False)
    assert res.waiting is not None and res.waiting.class_ == CheckClass.HUMAN
    assert res.next_skill == "wf-intent"
    text = render_result(res)
    assert "[GATE: direction policy=ask given=no]" in text
    assert "[WAITING: human gate:direction]" in text

    res = evaluate(DOC, _opts(tmp_path, unit, given=("direction",)))
    assert res.done == ["intent"] and res.stage is not None and res.stage.id == "build-verify"


def test_gate_auto_passes_and_off_skips(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate(DOC, _opts(tmp_path, unit, approvals={"direction": "auto"}))
    assert res.done == ["intent"]
    res = evaluate(DOC, _opts(tmp_path, unit, approvals={"direction": "off"}))
    assert res.done == [] and [(s.id, s.reason) for s in res.skipped] == [("intent", "approvals.direction=off")]
    assert "[SKIPPED: intent reason=approvals.direction=off]" in render_result(res)


def test_stage_policy_off_skips_ungated_stage(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "tasks.md").write_text("- [ ] one\n")
    res = evaluate(DOC, _opts(tmp_path, unit, approvals={"direction": "auto"}, stages={"build-verify": "off"}))
    assert res.done == ["intent"] and res.stage is not None and res.stage.id == "review"
    assert [(s.id, s.reason) for s in res.skipped] == [("build-verify", "stages.build-verify=off")]
    assert "[SKIPPED: build-verify reason=stages.build-verify=off]" in render_result(res)
    assert res.to_dict()["skipped"] == [{"id": "build-verify", "reason": "stages.build-verify=off"}]
    # a stage policy wins over a gate policy and never blocks completion
    res = evaluate(
        DOC,
        _opts(
            tmp_path,
            unit,
            approvals={"direction": "ask"},
            stages={"intent": "off", "build-verify": "off", "review": "off", "integrate": "off"},
        ),
    )
    assert res.complete and res.done == [] and len(res.skipped) == 4


def test_full_progression_to_complete(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    approvals = {"direction": "auto"}

    # build-verify: tasks must all be checked
    (unit / "tasks.md").write_text("- [ ] one\n- [x] two\n")
    res = evaluate(DOC, _opts(tmp_path, unit, approvals=approvals))
    assert res.stage is not None and res.stage.id == "build-verify"
    assert res.unmet[0].name == "tasks-all-checked" and res.unmet[0].detail == "1/2 checked"
    assert res.waiting is None
    assert "[RETURNS: intent when=new requirements]" in render_result(res)

    # review: delegate to reviewer, no envelope yet
    (unit / "tasks.md").write_text("- [x] one\n- [x] two\n")
    res = evaluate(DOC, _opts(tmp_path, unit, approvals=approvals))
    assert res.stage is not None and res.stage.id == "review"
    assert res.delegate is not None and (res.delegate.role, res.delegate.isolation) == ("reviewer", "preferred")
    assert res.unmet[0].detail == "no review envelope"
    assert res.next_skill == "wf-review"

    # review with open finding stays; reverify closes it
    _write_env(unit, "review-01.yaml", "kind: review\nstatus: completed\nfindings:\n  - {issue: a}\n")
    res = evaluate(DOC, _opts(tmp_path, unit, approvals=approvals))
    assert res.stage is not None and res.stage.id == "review" and "open_findings=1" in res.unmet[0].detail
    _write_env(unit, "reverify-01.yaml", "kind: reverify\nstatus: completed\nreview: review-01.yaml\n")

    # integrate: gated, plus a declared runner check
    res = evaluate(DOC, _opts(tmp_path, unit, approvals=approvals))
    assert res.stage is not None and res.stage.id == "integrate"
    assert [u.name for u in res.unmet] == ["anchor-status-completed", "ci-passed", "gate:integration"]
    assert res.unmet[1].detail == "declared for runner; not evaluated"
    assert res.waiting is not None and res.waiting.class_ == CheckClass.HUMAN

    write_unit(tmp_path, "work/a", status="completed")
    res = evaluate(DOC, _opts(tmp_path, unit, approvals=approvals, given=("ci-passed", "integration")))
    assert res.complete and res.stage is None
    assert res.done == ["intent", "build-verify", "review", "integrate"]
    assert "[STAGE: - complete=true]" in render_result(res)


def test_runner_only_unmet_reports_runner_waiting(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a", status="completed")
    (unit / "tasks.md").write_text("- [x] one\n")
    _write_env(unit, "review-01.yaml", "kind: review\nstatus: completed\n")
    res = evaluate(DOC, _opts(tmp_path, unit, approvals={"direction": "auto", "integration": "auto"}))
    assert res.stage is not None and res.stage.id == "integrate"
    assert res.waiting is not None and (res.waiting.class_, res.waiting.checks) == (CheckClass.RUNNER, ("ci-passed",))
    assert "[GATE: integration policy=auto given=no]" in render_result(res)


def test_optional_and_exception_stages(tmp_path: Path) -> None:
    doc = parse(
        """---
id: w
schema_version: 1
stages:
  - id: a
    exit: [anchor-exists]
  - id: opt
    optional: true
    exit: [file-exists(never.md)]
  - id: exc
    exception: true
    exit: [file-exists(never.md)]
  - id: b
    exit: [file-exists(b.md)]
---
"""
    )
    unit = write_unit(tmp_path, "work/a")
    res = evaluate(doc, _opts(tmp_path, unit))
    assert res.done == ["a"] and res.stage is not None and res.stage.id == "b"


def test_lint_check_uses_callback_and_reports_errors(tmp_path: Path) -> None:
    doc = parse("---\nid: w\nschema_version: 1\nstages:\n  - id: a\n    exit: [lint-clean]\n---\n")
    unit = write_unit(tmp_path, "work/a")
    seen: list[list[str]] = []

    def lint(root: Path, files: list[str]) -> list[str]:
        seen.append(files)
        return ["work/a/task.md:1 RULE-x boom"]

    res = evaluate(doc, _opts(tmp_path, unit, skip_lint=False, lint=lint))
    assert seen == [["work/a/task.md"]]
    assert res.unmet[0].detail == "1 violation(s): work/a/task.md:1 RULE-x boom"

    def failing(root: Path, files: list[str]) -> list[str]:
        raise RuntimeError("rule crashed")

    res = evaluate(doc, _opts(tmp_path, unit, skip_lint=False, lint=failing))
    assert res.lint_error == "rule crashed" and "lint failed" in res.unmet[0].detail

    res = evaluate(doc, _opts(tmp_path, unit, skip_lint=True))
    assert res.complete


def test_revision_ancestor_check(tmp_path: Path) -> None:
    doc = parse(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: a\n    exit: [revision-ancestor(review final-report)]\n---\n"
    )
    unit = write_unit(tmp_path, "work/a")
    res = evaluate(doc, _opts(tmp_path, unit))
    assert res.unmet[0].detail == "no review envelope"
    _write_env(unit, "review-01.yaml", "kind: review\nstatus: completed\ndiff_scope: {head: abc1234}\n")
    _write_env(unit, "final-report-01.yaml", "kind: final-report\nstatus: completed\ndiff_scope: {head: not-a-sha}\n")
    res = evaluate(doc, _opts(tmp_path, unit))
    assert "is not a revision" in res.unmet[0].detail
    _write_env(unit, "final-report-01.yaml", "kind: final-report\nstatus: completed\ndiff_scope: {head: def5678}\n")
    calls: list[tuple[str, str]] = []

    def ancestor(root: Path, a: str, b: str) -> bool:
        calls.append((a, b))
        return True

    res = evaluate(doc, _opts(tmp_path, unit, ancestor=ancestor))
    assert res.complete and calls == [("abc1234", "def5678")]


def test_not_skeleton_and_envelope_check_pass(tmp_path: Path) -> None:
    doc = parse(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: a\n    exit: [not-skeleton(plan.md), envelope-check-pass(final-report tests)]\n---\n"
    )
    unit = write_unit(tmp_path, "work/a")
    (unit / "plan.md").write_text("# plan\n<!-- devkit:skeleton -->\n")
    res = evaluate(doc, _opts(tmp_path, unit))
    assert [u.detail for u in res.unmet] == ["plan.md is a handoff skeleton", "no final-report envelope"]
    (unit / "plan.md").write_text("# plan\nreal content\n")
    _write_env(unit, "final-report-01.yaml", 'kind: final-report\nstatus: completed\nchecks: {tests: "PASS 1/1"}\n')
    assert evaluate(doc, _opts(tmp_path, unit)).complete


def test_drift_is_reported_on_result(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a", extra="workflow: direct-delivery\nworkflow_hash: sha256:old\n")
    res = evaluate(DOC, _opts(tmp_path, unit))
    assert res.binding.bound and res.drift is not None
    assert res.drift.recorded == "sha256:old" and res.drift.current == schema_hash(DOC)
    assert "[DRIFT: recorded=sha256:old" in render_result(res)


def test_envelope_errors_are_surfaced_not_fatal(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    _write_env(unit, "review-01.yaml", "status: completed\n")
    res = evaluate(DOC, _opts(tmp_path, unit, approvals={"direction": "auto"}))
    assert res.envelope_errors[0].reason == "missing required key kind"
    assert "[ENVELOPE_ERROR: envelopes/review-01.yaml missing required key kind]" in render_result(res)
    assert res.to_dict()["envelope_errors"][0]["file"] == "envelopes/review-01.yaml"
