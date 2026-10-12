from __future__ import annotations

import json
from pathlib import Path

import yaml
from click.testing import CliRunner, Result
from devkit.workflow import Options, evaluate_definition, load_decisions, parse_definition, render_evaluation
from devkit.workflow.cli import cli
from devkit.workflow.unit.decisions import DecisionRecordError, Decisions, new_decision, parse_record, write_decision
from testsupport.workflow import WORKFLOW, write_config, write_unit

HUMAN_CHECK = """---
id: signoff
schema_version: 1
checks:
  - { name: design-signed, class: human, description: "the design owner signed off" }
stages:
  - id: design
    exit: [anchor-exists, design-signed]
    skills: [wf-design]
---
"""
TRIAGE = """---
id: triage
schema_version: 1
stages:
  - id: decide
    exit: [anchor-exists]
next:
  - { workflow: spec-driven, when: [file-exists(spec.md)], recommended: true }
  - { workflow: direct-delivery }
---
"""
SPEC_DRIVEN = """---
id: spec-driven
schema_version: 1
stages:
  - id: specify
    exit: [file-exists(spec.md)]
---
"""


def _run(*args: str) -> Result:
    return CliRunner().invoke(cli, list(args))


def _opts(root: Path, unit: Path, **kw: object) -> Options:
    base = {"workspace_root": root, "unit_dir": unit, "anchor": "task.md", "skip_lint": True}
    base.update(kw)
    return Options(**base)  # type: ignore[arg-type]


def _record(
    unit: Path,
    request: str,
    action: str,
    *,
    workflow: str = "direct-delivery",
    stage: str = "",
    value: object = None,
    note: str = "",
) -> str:
    decisions = load_decisions(unit)
    decision = new_decision(
        decisions,
        request,
        action,
        workflow=workflow,
        at="2026-10-12T09:30:00Z",
        stage=stage,
        value=value,
        note=note,
        by="t",
    )
    return write_decision(unit, decision).file


# --- records ---------------------------------------------------------------------


def test_record_round_trip_and_effective(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    first = _record(unit, "gate:integration", "decline", stage="integrate", note="rebase first")
    second = _record(unit, "gate:integration", "accept", stage="integrate")
    third = _record(unit, "gate:integration", "cancel", stage="integrate")
    assert (first, second, third) == (
        "decisions/01-gate-integration.yaml",
        "decisions/02-gate-integration.yaml",
        "decisions/03-gate-integration.yaml",
    )
    data = yaml.safe_load((unit / first).read_text())
    assert data == {
        "request": "gate:integration",
        "kind": "approve",
        "action": "decline",
        "workflow": "direct-delivery",
        "stage": "integrate",
        "note": "rebase first",
        "by": "t",
        "at": "2026-10-12T09:30:00Z",
    }
    decisions = load_decisions(unit)
    assert [d.seq for d in decisions.records] == [1, 2, 3] and decisions.errors == []
    effective = decisions.effective("gate:integration")
    assert effective is not None and effective.action == "accept"  # cancel does not supersede
    assert decisions.effective("handoff") is None
    assert decisions.next_sequence() == 4


def test_malformed_records_are_reported_not_fatal(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    (unit / "decisions").mkdir()
    (unit / "decisions/01-gate-x.yaml").write_text(
        "request: gate:x\nkind: approve\naction: maybe\nworkflow: direct-delivery\nstage: intent\nat: now\n"
    )
    (unit / "decisions/02-gate-x.yaml").write_text("- not a mapping\n")
    (unit / "decisions/notes.txt").write_text("ignored\n")
    decisions = load_decisions(unit)
    assert decisions.records == []
    assert [e.file for e in decisions.errors] == ["decisions/01-gate-x.yaml", "decisions/02-gate-x.yaml"]
    assert "action must be one of" in decisions.errors[0].message
    res = evaluate_definition(parse_definition(WORKFLOW), _opts(tmp_path, unit))
    assert [e.file for e in res.decision_errors] == ["decisions/01-gate-x.yaml", "decisions/02-gate-x.yaml"]
    assert "[DECISION_ERROR: decisions/01-gate-x.yaml" in render_evaluation(res)


def test_parse_record_validation() -> None:
    base = {
        "request": "gate:x",
        "kind": "approve",
        "action": "accept",
        "workflow": "w",
        "stage": "s",
        "at": "2026-10-12T00:00:00Z",
    }
    assert parse_record(base, "decisions/01-gate-x.yaml", 1).request == "gate:x"
    choose = {**base, "request": "handoff", "kind": "choose", "stage": None}
    for bad, reason in [
        ({**base, "request": "Bad Id"}, "invalid request id"),
        ({**base, "kind": "ask"}, "does not match request"),
        ({**base, "value": 3}, "takes no value"),
        ({**choose, "value": 3}, "value must be"),
        ({**base, "at": ""}, "at: expected"),
        ({**base, "extra": 1}, "unknown keys"),
        ({k: v for k, v in base.items() if k != "workflow"}, "missing keys"),
    ]:
        try:
            parse_record(
                bad, "decisions/01-gate-x.yaml" if bad["request"] != "handoff" else "decisions/01-handoff.yaml", 1
            )
        except DecisionRecordError as exc:
            assert reason in str(exc) and exc.code == "DECISION_RECORD_INVALID"
        else:
            raise AssertionError(reason)
    assert Decisions().next_sequence() == 1


# --- evaluation ---------------------------------------------------------------------


def test_gate_request_and_recorded_approval(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(parse_definition(WORKFLOW), _opts(tmp_path, unit))
    assert [r.id for r in res.requests] == ["gate:direction"]
    req = res.requests[0]
    assert (req.kind, req.title, req.target.to_dict()) == (
        "approve",
        "Approve direction",
        {"type": "gate", "name": "direction", "stage": "intent"},
    )
    assert req.declined is None and req.allow_note and not req.options
    text = render_evaluation(res)
    assert (
        '[REQUEST: id=gate:direction kind=approve title="Approve direction" target=gate:direction stage=intent note=allowed]'
        in text
    )

    _record(unit, "gate:direction", "decline", stage="intent", note="scope unclear")
    res = evaluate_definition(parse_definition(WORKFLOW), _opts(tmp_path, unit))
    assert res.stage is not None and res.stage.id == "intent"
    assert res.requests[0].declined is not None and res.requests[0].declined.note == "scope unclear"
    assert (
        '[DECLINED: id=gate:direction file=decisions/01-gate-direction.yaml note="scope unclear"]'
        in render_evaluation(res)
    )
    assert res.to_dict()["requests"][0]["declined"]["file"] == "decisions/01-gate-direction.yaml"

    _record(unit, "gate:direction", "accept", stage="intent")
    res = evaluate_definition(parse_definition(WORKFLOW), _opts(tmp_path, unit))
    assert res.done == ["intent"] and res.stage is not None and res.stage.id == "build-verify"
    assert all(r.id != "gate:direction" for r in res.requests)
    assert res.gate is None or res.gate.name != "direction"


def test_human_check_request_and_approval(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(parse_definition(HUMAN_CHECK), _opts(tmp_path, unit))
    assert [r.id for r in res.requests] == ["check:design-signed"]
    assert res.requests[0].target.to_dict() == {"type": "check", "name": "design-signed", "stage": "design"}
    _record(unit, "check:design-signed", "accept", workflow="signoff", stage="design")
    res = evaluate_definition(parse_definition(HUMAN_CHECK), _opts(tmp_path, unit))
    assert res.complete
    assert "accepted by decisions/01-check-design-signed.yaml" in str(res.done) or res.done == ["design"]


def test_given_still_satisfies_without_a_record(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(parse_definition(WORKFLOW), _opts(tmp_path, unit, given=("direction",)))
    assert res.done == ["intent"] and load_decisions(unit).records == []


def test_handoff_request_and_recorded_choice(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(parse_definition(TRIAGE), _opts(tmp_path, unit))
    assert res.complete and [r.id for r in res.requests] == ["handoff"]
    req = res.requests[0]
    assert req.kind == "choose"
    assert [(o.id, o.eligible, o.recommended) for o in req.options] == [
        ("spec-driven", False, True),
        ("direct-delivery", True, False),
    ]
    assert (
        '[REQUEST: id=handoff kind=choose title="Choose next workflow" options=spec-driven,direct-delivery '
        "eligible=direct-delivery recommended=-]"
    ) in render_evaluation(res)

    # An ineligible recorded choice is ignored; an eligible one sets chosen and closes the request.
    _record(unit, "handoff", "accept", workflow="triage", value="spec-driven")
    res = evaluate_definition(parse_definition(TRIAGE), _opts(tmp_path, unit))
    assert res.handoff is not None and res.handoff.chosen is None and res.requests
    # B8: the ignored choice is reported, not silently dropped.
    assert [e.file for e in res.decision_errors] == ["decisions/01-handoff.yaml"]
    assert "not an eligible candidate" in res.decision_errors[0].message
    assert res.decision_errors[0].code == "HANDOFF_CHOICE_IGNORED"
    _record(unit, "handoff", "accept", workflow="triage", value="direct-delivery")
    res = evaluate_definition(parse_definition(TRIAGE), _opts(tmp_path, unit))
    assert res.handoff is not None and res.handoff.chosen == "direct-delivery"
    assert res.handoff.decision is not None and res.handoff.decision.file == "decisions/02-handoff.yaml"
    assert res.requests == [] and res.waiting is None
    assert "chosen=direct-delivery decision=decisions/02-handoff.yaml]" in render_evaluation(res)

    # Under auto, a recorded eligible choice beats the first-eligible pick.
    (unit / "spec.md").write_text("x\n")
    res = evaluate_definition(parse_definition(TRIAGE), _opts(tmp_path, unit, approvals={"handoff": "auto"}))
    assert res.handoff is not None and res.handoff.chosen == "direct-delivery"


def test_no_requests_under_auto_or_off(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(parse_definition(WORKFLOW), _opts(tmp_path, unit, approvals={"direction": "auto"}))
    assert all(r.id != "gate:direction" for r in res.requests)
    (unit / "spec.md").write_text("x\n")
    res = evaluate_definition(parse_definition(TRIAGE), _opts(tmp_path, unit, approvals={"handoff": "auto"}))
    assert res.requests == [] and res.handoff is not None and res.handoff.chosen == "spec-driven"
    res = evaluate_definition(parse_definition(TRIAGE), _opts(tmp_path, unit, approvals={"handoff": "off"}))
    assert res.requests == []


# --- CLI --------------------------------------------------------------------------------


def _workspace(tmp_path: Path, default: str = "direct-delivery", handoff: str = "ask") -> Path:
    defs = tmp_path / ".devkit/workflows"
    defs.mkdir(parents=True)
    (defs / "direct-delivery.md").write_text(WORKFLOW)
    (defs / "triage.md").write_text(TRIAGE)
    (defs / "spec-driven.md").write_text(SPEC_DRIVEN)
    write_config(
        tmp_path, f'schema = 1\n[workflow]\ndefault = "{default}"\n[workflow.approvals]\nhandoff = "{handoff}"\n'
    )
    return tmp_path


def test_cli_requests_answer_and_next(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    _run("new", "-w", str(root), "login")
    unit = ".devkit/transient/work/login"

    listed = _run("requests", "-w", str(root), "--unit", unit, "--no-lint")
    assert listed.exit_code == 0 and listed.output.startswith("[REQUEST: id=gate:direction kind=approve")
    as_json = json.loads(_run("requests", "-w", str(root), "--unit", unit, "--no-lint", "--format", "json").stdout)
    assert [r["id"] for r in as_json["requests"]] == ["gate:direction"]

    unknown = _run(
        "answer", "-w", str(root), "--unit", unit, "--no-lint", "--request", "gate:integration", "--action", "accept"
    )
    assert (
        unknown.exit_code == 2
        and "(REQUEST_UNKNOWN)" in unknown.stderr
        and "[DETAIL] open: gate:direction" in unknown.stderr
    )
    with_value = _run(
        "answer",
        "-w",
        str(root),
        "--unit",
        unit,
        "--no-lint",
        "--request",
        "gate:direction",
        "--action",
        "accept",
        "--value",
        "x",
    )
    assert with_value.exit_code == 2 and "(DECISION_INVALID)" in with_value.stderr

    declined = _run(
        "answer",
        "-w",
        str(root),
        "--unit",
        unit,
        "--no-lint",
        "--request",
        "gate:direction",
        "--action",
        "decline",
        "--note",
        "not yet",
        "--by",
        "mj",
    )
    assert declined.exit_code == 0, declined.output
    assert (
        declined.output.strip()
        == "[DECISION: decisions/01-gate-direction.yaml request=gate:direction kind=approve action=decline]"
    )
    nxt = _run("next", "-w", str(root), "--unit", unit, "--no-lint")
    assert (
        "[STAGE: intent" in nxt.output
        and '[DECLINED: id=gate:direction file=decisions/01-gate-direction.yaml note="not yet"]' in nxt.output
    )

    accepted = _run(
        "answer",
        "-w",
        str(root),
        "--unit",
        unit,
        "--no-lint",
        "--request",
        "gate:direction",
        "--action",
        "accept",
        "--format",
        "json",
    )
    assert accepted.exit_code == 0 and json.loads(accepted.stdout)["file"] == "decisions/02-gate-direction.yaml"
    record = yaml.safe_load((root / unit / "decisions/02-gate-direction.yaml").read_text())
    assert record["action"] == "accept" and record["at"].endswith("Z") and "value" not in record
    nxt = _run("next", "-w", str(root), "--unit", unit, "--no-lint", "--format", "json")
    payload = json.loads(nxt.stdout)
    assert payload["done"] == ["intent"] and payload["requests"] == [] and payload["errors"] == []
    assert _run("requests", "-w", str(root), "--unit", unit, "--no-lint").output.strip() == "[REQUESTS: none]"

    feedback = _run(
        "answer",
        "-w",
        str(root),
        "--unit",
        unit,
        "--no-lint",
        "--request",
        "feedback:build-verify",
        "--action",
        "accept",
        "--value",
        "keep tests small",
    )
    assert feedback.exit_code == 0 and "kind=feedback" in feedback.output
    no_text = _run(
        "answer", "-w", str(root), "--unit", unit, "--no-lint", "--request", "feedback:x", "--action", "accept"
    )
    assert no_text.exit_code == 2 and "(DECISION_INVALID)" in no_text.stderr
    bad_id = _run(
        "answer", "-w", str(root), "--unit", unit, "--no-lint", "--request", "Not An Id", "--action", "accept"
    )
    assert bad_id.exit_code == 2 and "(REQUEST_UNKNOWN)" in bad_id.stderr


def test_cli_handoff_uses_recorded_choice(tmp_path: Path) -> None:
    root = _workspace(tmp_path, default="triage")
    _run("new", "-w", str(root), "login")
    unit = ".devkit/transient/work/login"
    required = _run("handoff", "-w", str(root), "--unit", unit, "--no-lint")
    assert (
        required.exit_code == 2
        and "(HANDOFF_CHOICE_REQUIRED)" in required.stderr
        and "answer --unit" in required.stderr
    )

    ineligible = _run(
        "answer",
        "-w",
        str(root),
        "--unit",
        unit,
        "--no-lint",
        "--request",
        "handoff",
        "--action",
        "accept",
        "--value",
        "spec-driven",
    )
    assert (
        ineligible.exit_code == 2 and "(DECISION_INVALID)" in ineligible.stderr and "not eligible" in ineligible.stderr
    )
    two = _run(
        "answer",
        "-w",
        str(root),
        "--unit",
        unit,
        "--no-lint",
        "--request",
        "handoff",
        "--action",
        "accept",
        "--value",
        "direct-delivery",
        "--value",
        "spec-driven",
    )
    assert two.exit_code == 2 and "exactly one --value" in two.stderr
    other = _run(
        "answer",
        "-w",
        str(root),
        "--unit",
        unit,
        "--no-lint",
        "--request",
        "handoff",
        "--action",
        "accept",
        "--value",
        "custom",
    )
    assert other.exit_code == 2 and "not an option" in other.stderr

    chosen = _run(
        "answer",
        "-w",
        str(root),
        "--unit",
        unit,
        "--no-lint",
        "--request",
        "handoff",
        "--action",
        "accept",
        "--value",
        "direct-delivery",
    )
    assert chosen.exit_code == 0
    nxt = _run("next", "-w", str(root), "--unit", unit, "--no-lint")
    assert "chosen=direct-delivery decision=decisions/01-handoff.yaml]" in nxt.output and "[WAITING" not in nxt.output
    done = _run("handoff", "-w", str(root), "--unit", unit, "--no-lint", "--format", "json")
    assert done.exit_code == 0, done.output
    payload = json.loads(done.stdout)
    assert payload["to"] == "direct-delivery" and payload["decision"] == "decisions/01-handoff.yaml"
    assert "[WORKFLOW: direct-delivery" in _run("next", "-w", str(root), "--unit", unit, "--no-lint").output
