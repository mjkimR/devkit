from __future__ import annotations

import errno
import fcntl
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner, Result
from devkit.core import LockHeldError, LockUnsupportedError
from devkit.core.errors import UnsafePathError
from devkit.workflow import (
    DecisionInvalidError,
    DefinitionError,
    Options,
    Workspace,
    create_unit,
    evaluate_definition,
    load_decisions,
    load_envelopes,
    parse_definition,
    record_answer,
    render_document,
    render_evaluation,
)
from devkit.workflow.cli import cli
from devkit.workflow.unit import records
from devkit.workflow.unit.decisions import (
    Decision,
    DecisionRecordError,
    Decisions,
    new_decision,
    parse_record,
    record_instant,
    utc_timestamp,
    write_decision,
)
from testsupport.workflow import WORKFLOW, simple_workspace, write_config, write_record, write_unit

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


SHARED_GATE = """---
id: shared
schema_version: 1
checks:
  - { name: owner-ok, class: human, description: "the owner agreed" }
stages:
  - id: intent
    human_gate: signoff
    exit: [file-exists(a.txt), owner-ok]
  - id: build
    exit: [file-exists(b.txt)]
  - id: integrate
    human_gate: signoff
    exit: [file-exists(c.txt), owner-ok]
---
"""


def test_shared_gate_and_human_check_are_answered_per_stage(tmp_path: Path) -> None:
    doc = parse_definition(SHARED_GATE)
    unit = write_unit(tmp_path, "work/a")
    for name in ("a.txt", "b.txt", "c.txt"):
        (unit / name).write_text("x\n")
    _record(unit, "check:owner-ok", "accept", workflow="shared", stage="intent")
    _record(unit, "gate:signoff", "accept", workflow="shared", stage="intent")
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    # The approvals given at intent do not answer the same gate and check at integrate.
    assert res.done == ["intent", "build"] and res.stage is not None and res.stage.id == "integrate"
    assert [u.name for u in res.unmet] == ["owner-ok"]
    assert [(r.id, r.target.stage) for r in res.requests] == [("check:owner-ok", "integrate")]

    # A decline at integrate is shown there and leaves the intent approval alone.
    _record(unit, "check:owner-ok", "decline", workflow="shared", stage="integrate", note="not yet")
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert res.done == ["intent", "build"] and res.requests[0].declined is not None

    _record(unit, "check:owner-ok", "accept", workflow="shared", stage="integrate")
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert [(r.id, r.target.stage) for r in res.requests] == [("gate:signoff", "integrate")]
    _record(unit, "gate:signoff", "accept", workflow="shared", stage="integrate")
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert res.complete

    # A return to integrate voids only the integrate approvals; the intent ones still count.
    _record(unit, "return:integrate", "accept", workflow="shared", stage="integrate")
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert res.done == ["intent", "build"] and [r.id for r in res.requests] == ["check:owner-ok"]
    assert res.stale_approvals == []


def test_stale_approval_is_matched_to_its_own_stage(tmp_path: Path) -> None:
    doc = parse_definition(SHARED_GATE)
    unit = write_unit(tmp_path, "work/a")
    for name in ("a.txt", "b.txt", "c.txt"):
        (unit / name).write_text("x\n")
    for stage in ("intent", "integrate"):
        _record(unit, "check:owner-ok", "accept", workflow="shared", stage=stage)
        _record(unit, "gate:signoff", "accept", workflow="shared", stage=stage)
    (unit / "b.txt").unlink()
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert res.stage is not None and res.stage.id == "build"
    assert sorted((r.request, r.stage) for r in res.stale_approvals) == [
        ("check:owner-ok", "integrate"),
        ("gate:signoff", "integrate"),
    ]


def test_given_still_satisfies_without_a_record(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(parse_definition(WORKFLOW), _opts(tmp_path, unit, given=("direction",)))
    assert res.done == ["intent"] and load_decisions(unit).records == []


def _with_gates(gates: str) -> str:
    """``WORKFLOW`` with a top-level ``gates`` value."""
    return WORKFLOW.replace("schema_version: 1\n", f"schema_version: 1\ngates: {gates}\n", 1)


def test_a_given_gate_says_so_in_its_request_and_needs_no_record(tmp_path: Path) -> None:
    doc = parse_definition(_with_gates("{ direction: { answer: given } }"))
    assert doc.gate_answer("direction") == "given" and doc.to_dict()["gates"] == {"direction": {"answer": "given"}}
    assert "[GATE: direction policy=ask answer=given]" in render_document(doc)
    unit = write_unit(tmp_path, "work/a")
    res = evaluate_definition(doc, _opts(tmp_path, unit))
    assert res.requests[0].answer == "given" and res.to_dict()["requests"][0]["answer"] == "given"
    assert (
        '[REQUEST: id=gate:direction kind=approve title="Approve direction" target=gate:direction stage=intent '
        "note=allowed answer=given]" in render_evaluation(res)
    )
    res = evaluate_definition(doc, _opts(tmp_path, unit, given=("direction",)))
    assert res.done == ["intent"] and load_decisions(unit).records == []


def test_a_recorded_gate_keeps_its_request_unchanged(tmp_path: Path) -> None:
    doc = parse_definition(_with_gates("{ direction: { answer: record } }"))
    assert doc.gate_answers == () and doc.gate_answer("direction") == "record"
    res = evaluate_definition(doc, _opts(tmp_path, write_unit(tmp_path, "work/a")))
    assert res.requests[0].answer == "record" and "answer=" not in render_evaluation(res)


@pytest.mark.parametrize(
    ("gates", "message"),
    [
        ("[direction]", "gates: expected a mapping"),
        ("{ release: { answer: given } }", "gates.release: not the human_gate of any stage"),
        ("{ direction: given }", "gates.direction: expected a mapping with answer"),
        ("{ direction: { answer: given, note: x } }", "gates.direction: unknown keys ['note']"),
        ("{ direction: { answer: never } }", "gates.direction.answer: expected one of ['record', 'given']"),
    ],
)
def test_gate_settings_are_validated(gates: str, message: str) -> None:
    with pytest.raises(DefinitionError, match=re.escape(message)):
        parse_definition(_with_gates(gates))


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


# --- feedback ---------------------------------------------------------------------------------


def test_feedback_answers_validate_the_action(tmp_path: Path) -> None:
    root = simple_workspace(tmp_path)
    ws = Workspace(root)
    unit = create_unit(ws, "u")
    with pytest.raises(DecisionInvalidError):
        record_answer(ws, unit, "feedback:x", "approve", ["text"])
    assert not (unit.dir / "decisions").exists()


# --- numbered record files --------------------------------------------------------------------


def _leftovers(directory: Path) -> list[str]:
    return sorted(p.name for p in directory.iterdir() if records.is_temporary(p.name))


def _gate(stale: Decisions, name: str = "a") -> Decision:
    return new_decision(stale, f"gate:{name}", "accept", workflow="w", stage="s")


def test_a_sequence_is_unique_across_requests(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "u")
    stale = load_decisions(unit)
    first = write_decision(unit, _gate(stale))
    # A concurrent writer computed the same next sequence for another request.
    second = write_decision(unit, new_decision(stale, "return:s", "accept", workflow="w"))
    assert (first.seq, second.seq) == (1, 2)
    assert second.file == "decisions/02-return-s.yaml"
    assert [r.seq for r in load_decisions(unit).records] == [1, 2]


def test_a_sequence_is_never_below_a_taken_one(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "u")
    stale = load_decisions(unit)
    write_record(unit, "05-gate-a.yaml", request="gate:a", kind="approve", action="accept", workflow="w", stage="s")
    # Sequence 1 is free, but a record written now must order after record 5.
    assert write_decision(unit, _gate(stale, "b")).seq == 6


def test_concurrent_writers_get_distinct_sequences(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "u")
    stale = load_decisions(unit)

    def write(i: int) -> int:
        return write_decision(unit, _gate(stale, f"g{i}")).seq

    with ThreadPoolExecutor(max_workers=8) as pool:
        seqs = list(pool.map(write, range(24)))
    assert sorted(seqs) == list(range(1, 25))
    assert len(load_decisions(unit).records) == 24 and _leftovers(unit / "decisions") == []


def test_a_failed_write_leaves_no_record_and_no_temporary_file(tmp_path: Path) -> None:
    directory = tmp_path / "decisions"

    def write(body: str) -> tuple[Path, int]:
        return records.write_numbered(directory, 1, lambda n: f"{n:02d}-gate-a.yaml", lambda _: None, body)

    with pytest.raises(UnicodeEncodeError):
        write("request: \udc80\n")  # cannot be encoded: the write fails part-way
    assert list(directory.iterdir()) == []
    assert write("request: gate:a\n") == (directory / "01-gate-a.yaml", 1)


def test_records_are_written_whole_without_hard_links(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def no_links(*_: object) -> None:
        raise OSError(errno.ENOTSUP, "Operation not supported")

    monkeypatch.setattr(records.os, "link", no_links)
    unit = write_unit(tmp_path, "u")
    stale = load_decisions(unit)
    assert [write_decision(unit, _gate(stale, name)).seq for name in ("a", "b")] == [1, 2]
    assert [r.request for r in load_decisions(unit).records] == ["gate:a", "gate:b"]
    assert records.write_new_file(unit / "task.md", "replaced") is False
    assert (unit / "task.md").read_text().startswith("---\nid: x") and _leftovers(unit) == []


def test_a_writer_waits_for_the_lock_a_bounded_time(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    unit = write_unit(tmp_path, "u")
    (unit / "decisions").mkdir()
    monkeypatch.setattr(records, "LOCK_TIMEOUT", 0.05)
    holder = os.open(unit / "decisions", os.O_RDONLY)
    try:
        fcntl.flock(holder, fcntl.LOCK_EX)
        with pytest.raises(LockHeldError) as raised:
            write_decision(unit, _gate(load_decisions(unit)))
        assert raised.value.code == "LOCK_HELD"
    finally:
        os.close(holder)
    assert write_decision(unit, _gate(load_decisions(unit))).seq == 1


def test_writing_records_needs_flock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    unit = write_unit(tmp_path, "u")
    monkeypatch.setitem(sys.modules, "fcntl", None)  # `import fcntl` raises ImportError
    with pytest.raises(LockUnsupportedError) as raised:
        write_decision(unit, _gate(load_decisions(unit)))
    assert raised.value.code == "LOCK_UNSUPPORTED"


def test_records_are_never_written_through_a_symbolic_link(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "u")
    (tmp_path / "elsewhere").mkdir()
    (unit / "decisions").symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    with pytest.raises(UnsafePathError):
        write_decision(unit, _gate(load_decisions(unit)))
    assert list((tmp_path / "elsewhere").iterdir()) == []


def test_loaders_skip_temporary_files(tmp_path: Path) -> None:
    unit = write_unit(tmp_path, "u")
    for directory, name in (("decisions", "01-gate-a.yaml"), ("envelopes", "review-01.yaml")):
        (unit / directory).mkdir()
        (unit / directory / f".{name}.0123456789ab.tmp").write_text("partial: [")
    decisions, envelopes = load_decisions(unit), load_envelopes(unit)
    assert (decisions.records, decisions.errors, decisions.max_seq) == ([], [], 0)
    assert (envelopes.by_kind, envelopes.errors) == ({}, [])


def test_a_concurrent_return_voids_an_approval_given_from_the_same_state(tmp_path: Path) -> None:
    doc = parse_definition(
        "---\nid: w\nschema_version: 1\nstages:\n  - id: s\n    human_gate: g\n    exit: [anchor-exists]\n---\n"
    )
    unit = write_unit(tmp_path, "u")
    stale = load_decisions(unit)
    write_decision(unit, _gate(stale, "g"))
    write_decision(unit, new_decision(stale, "return:s", "accept", workflow="w"))
    res = evaluate_definition(doc, Options(workspace_root=tmp_path, unit_dir=unit, anchor="task.md", skip_lint=True))
    assert res.stage is not None and [u.name for u in res.unmet] == ["gate:g"]


# --- timestamps -------------------------------------------------------------------------------


def test_timestamps_are_written_to_the_microsecond() -> None:
    moment = datetime(2026, 10, 12, 9, 30, 0, 250000, tzinfo=UTC)
    assert utc_timestamp(moment) == "2026-10-12T09:30:00.250000Z"
    # A whole second is written without a fraction, which reads back as the whole second.
    assert utc_timestamp(moment.replace(microsecond=0)) == "2026-10-12T09:30:00Z"
    later = moment + timedelta(seconds=1)
    assert utc_timestamp(moment, after=later) == "2026-10-12T09:30:01.250000Z"
    assert utc_timestamp(later, after=moment) == "2026-10-12T09:30:01.250000Z"


@pytest.mark.parametrize(
    ("text", "width"),
    [
        ("2026-10-12T09:30:00Z", timedelta(seconds=1)),
        ("2026-10-12T09:30:00.250000Z", timedelta(microseconds=1)),
        ("2026-10-12 09:30:00.25+00:00", timedelta(milliseconds=10)),
        ("2026-10-12T11:30+02:00", timedelta(minutes=1)),
    ],
)
def test_an_instant_spans_the_precision_of_its_timestamp(text: str, width: timedelta) -> None:
    instant = record_instant(text)
    assert instant is not None and instant.end - instant.start == width
    assert instant.start == datetime.fromisoformat(text)


@pytest.mark.parametrize("text", ["", "2026-10-12", "2026-10-12T09:30:00", "yesterday"])
def test_a_timestamp_without_a_zone_or_time_has_no_instant(text: str) -> None:
    assert record_instant(text) is None
