from __future__ import annotations

import json
from pathlib import Path

import pytest
from devkit.advisory import AdvisoryError
from devkit.workflow import (
    Options,
    UnitNotFoundError,
    evaluate_definition,
    parse_definition,
    render_evaluation,
)
from devkit.workflow.definition.checks import CheckClass
from testsupport.workflow import SIMPLE, WORKFLOW, run_cli, simple_workspace, write_record, write_unit

DOC = parse_definition(WORKFLOW)


def _opts(root: Path, unit: Path, **kw: object) -> Options:
    base = {"workspace_root": root, "unit_dir": unit, "anchor": "task.md", "skip_lint": True}
    base.update(kw)
    return Options(**base)  # type: ignore[arg-type]


def _write_env(unit: Path, name: str, body: str) -> None:
    (unit / "envelopes").mkdir(exist_ok=True)
    (unit / "envelopes" / name).write_text(body)


def test_missing_anchor_raises(tmp_path: Path) -> None:
    with pytest.raises(UnitNotFoundError):
        evaluate_definition(DOC, _opts(tmp_path, tmp_path / "nope"))


def test_gate_ask_blocks_until_given(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(DOC, _opts(tmp_path, unit))
    assert res.stage is not None and res.stage.id == "intent"
    assert [u.name for u in res.unmet] == ["gate:direction"]
    assert res.gate is not None and (res.gate.name, res.gate.policy, res.gate.satisfied) == ("direction", "ask", False)
    assert res.waiting is not None and res.waiting.class_ == CheckClass.HUMAN
    assert res.next_skill == "wf-intent"
    text = render_evaluation(res)
    assert "[GATE: direction policy=ask satisfied=no source=-]" in text
    assert "[WAITING: human gate:direction]" in text

    res = evaluate_definition(DOC, _opts(tmp_path, unit, given=("direction",)))
    assert res.done == ["intent"] and res.stage is not None and res.stage.id == "build-verify"


def test_gate_auto_passes_and_off_skips(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(DOC, _opts(tmp_path, unit, approvals={"direction": "auto"}))
    assert res.done == ["intent"]
    res = evaluate_definition(DOC, _opts(tmp_path, unit, approvals={"direction": "off"}))
    assert res.done == [] and [(s.id, s.reason) for s in res.skipped] == [("intent", "approvals.direction=off")]
    assert "[SKIPPED: intent reason=approvals.direction=off]" in render_evaluation(res)


def test_stage_policy_off_skips_ungated_stage(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "tasks.md").write_text("- [ ] one\n")
    res = evaluate_definition(
        DOC, _opts(tmp_path, unit, approvals={"direction": "auto"}, stages={"build-verify": "off"})
    )
    assert res.done == ["intent"] and res.stage is not None and res.stage.id == "review"
    assert [(s.id, s.reason) for s in res.skipped] == [("build-verify", "stages.build-verify=off")]
    assert "[SKIPPED: build-verify reason=stages.build-verify=off]" in render_evaluation(res)
    assert res.to_dict()["skipped"] == [{"id": "build-verify", "reason": "stages.build-verify=off"}]
    # a stage policy wins over a gate policy and never blocks completion
    res = evaluate_definition(
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
    res = evaluate_definition(DOC, _opts(tmp_path, unit, approvals=approvals))
    assert res.stage is not None and res.stage.id == "build-verify"
    assert res.unmet[0].name == "tasks-all-checked" and res.unmet[0].detail == "1/2 checked"
    assert res.waiting is None
    assert '[RETURNS: intent when="new requirements"]' in render_evaluation(res)

    # review: delegate to reviewer, no envelope yet
    (unit / "tasks.md").write_text("- [x] one\n- [x] two\n")
    res = evaluate_definition(DOC, _opts(tmp_path, unit, approvals=approvals))
    assert res.stage is not None and res.stage.id == "review"
    assert res.delegate is not None and (res.delegate.role, res.delegate.isolation) == ("reviewer", "preferred")
    assert res.unmet[0].detail == "no review envelope"
    assert res.next_skill == "wf-review"

    # review with open finding stays; reverify closes it
    _write_env(unit, "review-01.yaml", "kind: review\nstatus: completed\nfindings:\n  - {issue: a}\n")
    res = evaluate_definition(DOC, _opts(tmp_path, unit, approvals=approvals))
    assert res.stage is not None and res.stage.id == "review" and "open_findings=1" in res.unmet[0].detail
    _write_env(unit, "reverify-01.yaml", "kind: reverify\nstatus: completed\nreview: review-01.yaml\n")

    # integrate: gated, plus a declared runner check
    res = evaluate_definition(DOC, _opts(tmp_path, unit, approvals=approvals))
    assert res.stage is not None and res.stage.id == "integrate"
    # B3: the gate is not asked while the stage's own exit checks are unmet.
    assert [u.name for u in res.unmet] == ["anchor-status-completed", "ci-passed"]
    assert res.unmet[1].detail == "declared for runner; not evaluated"
    assert res.waiting is None and res.requests == []
    assert res.gate is not None and not res.gate.satisfied

    write_unit(tmp_path, "work/a", status="completed")
    res = evaluate_definition(DOC, _opts(tmp_path, unit, approvals=approvals, given=("ci-passed", "integration")))
    assert res.complete and res.stage is None
    assert res.done == ["intent", "build-verify", "review", "integrate"]
    assert "[STAGE: - complete=true]" in render_evaluation(res)


def test_runner_only_unmet_reports_runner_waiting(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a", status="completed")
    (unit / "tasks.md").write_text("- [x] one\n")
    _write_env(unit, "review-01.yaml", "kind: review\nstatus: completed\n")
    res = evaluate_definition(DOC, _opts(tmp_path, unit, approvals={"direction": "auto", "integration": "auto"}))
    assert res.stage is not None and res.stage.id == "integrate"
    assert res.waiting is not None and (res.waiting.class_, res.waiting.checks) == (CheckClass.RUNNER, ("ci-passed",))
    assert "[GATE: integration policy=auto satisfied=yes source=policy]" in render_evaluation(res)


def test_optional_and_exception_stages(tmp_path: Path) -> None:
    doc = parse_definition(
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
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert res.done == ["a"] and res.stage is not None and res.stage.id == "b"


def test_lint_check_uses_callback_and_reports_errors(tmp_path: Path) -> None:
    doc = parse_definition("---\nid: w\nschema_version: 1\nstages:\n  - id: a\n    exit: [lint-clean]\n---\n")
    unit = write_unit(tmp_path, "work/a")
    seen: list[list[str]] = []

    def lint(root: Path, files: list[str]) -> list[str]:
        seen.append(files)
        return ["work/a/task.md:1 RULE-x boom"]

    res = evaluate_definition(doc, _opts(tmp_path, unit, skip_lint=False, lint=lint))
    assert seen == [["work/a/task.md"]]
    assert res.unmet[0].detail == "1 violation(s): work/a/task.md:1 RULE-x boom"

    many = [f"work/a/task.md:{n} RULE-x boom" for n in range(1, 6)]
    res = evaluate_definition(doc, _opts(tmp_path, unit, skip_lint=False, lint=lambda root, files: many))
    assert res.unmet[0].detail == (
        "5 violation(s): work/a/task.md:1 RULE-x boom; work/a/task.md:2 RULE-x boom; work/a/task.md:3 RULE-x boom;"
        " 2 more (devkit rules check work/a)"
    )

    def failing(root: Path, files: list[str]) -> list[str]:
        raise RuntimeError("rule crashed")

    res = evaluate_definition(doc, _opts(tmp_path, unit, skip_lint=False, lint=failing))
    assert res.lint_error is not None and res.lint_error.message == "RuntimeError: rule crashed"
    assert res.lint_error.code == "UNEXPECTED_ERROR" and "lint failed" in res.unmet[0].detail
    assert res.to_dict()["errors"][-1]["code"] == "UNEXPECTED_ERROR"

    refusal = AdvisoryError("rules could not run", code="RULES_RUN_FAILED")

    def refusing(root: Path, files: list[str]) -> list[str]:
        raise refusal

    res = evaluate_definition(doc, _opts(tmp_path, unit, skip_lint=False, lint=refusing))
    assert res.lint_error is refusal  # an advisory error passes through unchanged, code and all

    res = evaluate_definition(doc, _opts(tmp_path, unit, skip_lint=True))
    assert res.complete


def test_revision_ancestor_check(tmp_path: Path) -> None:
    doc = parse_definition(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: a\n    exit: [revision-ancestor(review final-report)]\n---\n"
    )
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert res.unmet[0].detail == "no review envelope"
    _write_env(unit, "review-01.yaml", "kind: review\nstatus: completed\ndiff_scope: {head: abc1234}\n")
    _write_env(unit, "final-report-01.yaml", "kind: final-report\nstatus: completed\ndiff_scope: {head: not-a-sha}\n")
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert "is not a revision" in res.unmet[0].detail
    _write_env(unit, "final-report-01.yaml", "kind: final-report\nstatus: completed\ndiff_scope: {head: def5678}\n")
    calls: list[tuple[str, str]] = []

    def ancestor(root: Path, a: str, b: str) -> bool:
        calls.append((a, b))
        return True

    res = evaluate_definition(doc, _opts(tmp_path, unit, ancestor=ancestor))
    assert res.complete and calls == [("abc1234", "def5678")]


def test_not_skeleton_and_envelope_check_pass(tmp_path: Path) -> None:
    doc = parse_definition(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: a\n    exit: [not-skeleton(plan.md), envelope-check-pass(final-report tests)]\n---\n"
    )
    unit = write_unit(tmp_path, "work/a")
    (unit / "plan.md").write_text("# plan\n<!-- devkit:skeleton -->\n")
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert [u.detail for u in res.unmet] == ["plan.md is a handoff skeleton", "no final-report envelope"]
    (unit / "plan.md").write_text("# plan\nreal content\n")
    _write_env(unit, "final-report-01.yaml", 'kind: final-report\nstatus: completed\nchecks: {tests: "PASS 1/1"}\n')
    assert evaluate_definition(doc, _opts(tmp_path, unit)).complete


def test_workflow_id_alone_is_a_binding(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a", extra="workflow: direct-delivery\n")
    res = evaluate_definition(DOC, _opts(tmp_path, unit))
    assert res.binding.bound and res.binding.workflow == "direct-delivery"
    assert "drift" not in res.to_dict()


def test_envelope_errors_are_surfaced_not_fatal(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    _write_env(unit, "review-01.yaml", "status: completed\n")
    res = evaluate_definition(DOC, _opts(tmp_path, unit, approvals={"direction": "auto"}))
    assert res.envelope_errors[0].message == "missing required key kind"
    assert '[ENVELOPE_ERROR: envelopes/review-01.yaml "missing required key kind"]' in render_evaluation(res)
    [error] = res.to_dict()["errors"]
    assert (error["code"], error["file"]) == ("ENVELOPE_INVALID", "envelopes/review-01.yaml")


REVIEWED = parse_definition("""---
id: reviewed
schema_version: 1
stages:
  - id: build
    exit: [file-exists(built.txt)]
  - id: review
    exit: [envelope-review-passed]
  - id: report
    exit: [file-exists(reported.txt)]
---
""")
PASSED_REVIEW = "kind: review\nstatus: completed\nstage: review\ncreated_at: '{at}'\n"


def test_a_return_voids_envelopes_recorded_before_it(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "built.txt").write_text("x")
    _write_env(unit, "review-01.yaml", PASSED_REVIEW.format(at="2026-10-12T09:00:00Z"))
    assert evaluate_definition(REVIEWED, _opts(tmp_path, unit)).stage.id == "report"  # type: ignore[union-attr]

    returned = {"kind": "return", "action": "accept", "workflow": "reviewed", "stage": "build"}
    write_record(unit, "01-return-build.yaml", request="return:build", at="2026-10-12T09:30:00Z", **returned)
    res = evaluate_definition(REVIEWED, _opts(tmp_path, unit))
    assert res.stage is not None and res.stage.id == "review"
    assert [u.name for u in res.unmet] == ["envelope-review-passed"]

    # A review recorded after the return counts again.
    _write_env(unit, "review-02.yaml", PASSED_REVIEW.format(at="2026-10-12T10:00:00Z"))
    assert evaluate_definition(REVIEWED, _opts(tmp_path, unit)).stage.id == "report"  # type: ignore[union-attr]


def test_a_return_to_a_later_stage_or_an_unplaced_envelope_voids_nothing(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "built.txt").write_text("x")
    # Without a stage the envelope cannot be placed in the definition, so no return voids it.
    _write_env(unit, "review-01.yaml", "kind: review\nstatus: completed\ncreated_at: '2026-10-12T09:00:00Z'\n")
    returned = {"kind": "return", "action": "accept", "workflow": "reviewed", "stage": "build"}
    write_record(unit, "01-return-build.yaml", request="return:build", at="2026-10-12T09:30:00Z", **returned)
    assert evaluate_definition(REVIEWED, _opts(tmp_path, unit)).stage.id == "report"  # type: ignore[union-attr]
    # A review placed at its stage survives a return to a later stage.
    _write_env(unit, "review-01.yaml", PASSED_REVIEW.format(at="2026-10-12T09:00:00Z"))
    (unit / "decisions" / "01-return-build.yaml").unlink()
    later = {"kind": "return", "action": "accept", "workflow": "reviewed", "stage": "report"}
    write_record(unit, "01-return-report.yaml", request="return:report", at="2026-10-12T09:30:00Z", **later)
    assert evaluate_definition(REVIEWED, _opts(tmp_path, unit)).stage.id == "report"  # type: ignore[union-attr]


RETURNED = {"kind": "return", "action": "accept", "workflow": "reviewed", "stage": "build"}


@pytest.mark.parametrize("written", ["2026-10-12T09:30:00Z", "2026-10-12T09:30:00.900000+00:00"])
def test_a_return_voids_an_envelope_from_the_same_second(tmp_path: Path, written: str) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "built.txt").write_text("x")
    _write_env(unit, "review-01.yaml", PASSED_REVIEW.format(at=written))
    assert evaluate_definition(REVIEWED, _opts(tmp_path, unit)).stage.id == "report"  # type: ignore[union-attr]
    # The return names only its second, so it may have been written after the envelope.
    write_record(unit, "01-return-build.yaml", request="return:build", at="2026-10-12T09:30:00Z", **RETURNED)
    res = evaluate_definition(REVIEWED, _opts(tmp_path, unit))
    assert res.stage is not None and res.stage.id == "review"
    assert [u.name for u in res.unmet] == ["envelope-review-passed"]


@pytest.mark.parametrize(
    ("written", "counts"),
    [
        ("2026-10-12T09:30:00.400000Z", False),  # before the return
        ("2026-10-12T09:30:00.500000Z", False),  # the same microsecond: the order is unknown
        ("2026-10-12T09:30:00.500001Z", True),
        ("2026-10-12T09:30:01Z", True),
        ("2026-10-12T09:30:00Z", False),  # a whole second that contains the return
    ],
)
def test_sub_second_times_order_an_envelope_and_a_return(tmp_path: Path, written: str, counts: bool) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "built.txt").write_text("x")
    write_record(unit, "01-return-build.yaml", request="return:build", at="2026-10-12T09:30:00.500000Z", **RETURNED)
    _write_env(unit, "review-01.yaml", PASSED_REVIEW.format(at=written))
    stage = evaluate_definition(REVIEWED, _opts(tmp_path, unit)).stage
    assert stage is not None and stage.id == ("report" if counts else "review")


# --- lint-clean -------------------------------------------------------------------------------


def test_lint_clean_on_a_unit_outside_the_root_is_a_reported_error(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path / "project", check="lint-clean")
    outside = write_unit(tmp_path, "outside/u")
    result = run_cli("next", "-w", str(root), "--unit", str(outside), "--format", "json")
    assert result.exit_code == 2, result.output
    [error] = json.loads(result.stdout)["errors"]
    assert error["code"] == "PATH_UNSAFE" and "outside the workspace root" in error["message"]

    # A unit reached through a symbolic link that leaves the root is the same unit.
    (root / "linked").symlink_to(outside, target_is_directory=True)
    text = run_cli("next", "-w", str(root), "--unit", "linked")
    assert text.exit_code == 2 and "[LINT_ERROR: " in text.stdout and "(PATH_UNSAFE)" in text.stderr


def test_the_lint_detail_names_a_unit_outside_the_root_as_given(tmp_path: Path) -> None:
    doc = parse_definition(SIMPLE.format(id="w", check="lint-clean"))
    unit = write_unit(tmp_path, "outside/u")

    def lint(_root: Path, _files: list[str]) -> list[str]:
        return [f"v{i}" for i in range(5)]

    res = evaluate_definition(doc, _opts(tmp_path / "work", unit, lint=lint, skip_lint=False))
    assert res.unit == unit.as_posix() and res.lint_error is not None
    assert res.lint_error.code == "PATH_UNSAFE"
    # Inside the root, the detail names the unit relative to it.
    res = evaluate_definition(doc, _opts(tmp_path, unit, lint=lint, skip_lint=False))
    assert "2 more (devkit rules check outside/u)" in res.unmet[0].detail


def test_lint_clean_skips_the_temporary_files_of_writes_in_progress(tmp_path: Path) -> None:
    doc = parse_definition(SIMPLE.format(id="w", check="lint-clean"))
    unit = write_unit(tmp_path, "u")
    (unit / "decisions").mkdir()
    (unit / "decisions/.01-gate-a.yaml.0123456789ab.tmp").write_text("partial")
    (unit / ".task.md.0123456789ab.tmp").write_text("partial")
    (unit / ".notes.tmp").write_text("not a write in progress")
    linted: list[str] = []

    def lint(_root: Path, files: list[str]) -> list[str]:
        linted.extend(files)
        return []

    assert evaluate_definition(doc, _opts(tmp_path, unit, lint=lint, skip_lint=False)).complete
    assert linted == ["u/.notes.tmp", "u/task.md"]


# AC-02 (SPEC-envelope-record-gaps)
def test_challenger_state_follows_its_reverify_and_review_state_ignores_it(tmp_path: Path) -> None:
    doc = parse_definition(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: a\n"
        "    exit: [envelope-completed(challenger), envelope-review-passed]\n---\n"
    )
    unit = write_unit(tmp_path, "work/a")
    finding = "findings: [{issue: x, evidence: y, severity: P2}]\n"
    _write_env(unit, "review-01.yaml", "kind: review\nstatus: completed\n" + finding)
    _write_env(unit, "challenger-01.yaml", "kind: challenger\nstatus: completed\n" + finding)
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert [u.detail for u in res.unmet] == [
        "envelopes/challenger-01.yaml status=completed open_findings=1",
        "envelopes/review-01.yaml status=completed open_findings=1",
    ]
    _write_env(
        unit,
        "reverify-01.yaml",
        "kind: reverify\nstatus: completed\nreview: challenger-01.yaml\n"
        "findings: [{issue: x, evidence: y, severity: P2, resolution: resolved}]\n",
    )
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert [u.detail for u in res.unmet] == ["envelopes/review-01.yaml status=completed open_findings=1"]
