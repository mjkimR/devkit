"""The proposal unit's workflow records at handoff: dropped, and its plan-intent and plan-accept carried by name."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from devkit_agt.features.workflow import Workspace, load_decisions
from devkit_core.core import run_git
from spec_support.proposals import (
    CHARACTERIZE,
    GATED,
    MONTH,
    PROPOSAL_WORKFLOW,
    STAMP,
    TODAY,
    accept,
    spec_dir,
    write_workflow,
)
from spec_support.types import Write

from devkit_spec.base.errors import ProposalAcceptanceUnrecordedError
from devkit_spec.features.proposals import CarriedGate, create_proposal, handoff_proposal
from devkit_spec.features.proposals.usecases import handoff as handoff_module
from devkit_spec.features.proposals.usecases.scaffold import CreateProposalDecisionUseCase

UNIT = "docs/proposals/PROP-{slug}"


def _proposal(root: Path, slug: str) -> Path:
    """A bundle bound to ``sdd-proposal`` whose spec follows the gated ``sdd-spec-feature``; returns its
    proposal.md."""
    write_workflow(root, "sdd-proposal", PROPOSAL_WORKFLOW)
    write_workflow(root, "sdd-spec-feature", GATED.format(id="sdd-spec-feature", middle=""))
    write_workflow(root, "sdd-spec-bugfix", GATED.format(id="sdd-spec-bugfix", middle=CHARACTERIZE))
    created = create_proposal(root, slug, today=TODAY)
    return root / created.path


def _record(root: Path, slug: str, name: str, **fields: object) -> None:
    """A decision record of the proposal unit: an ``accept`` of ``plan-accept`` in ``sdd-proposal`` unless
    ``fields`` say otherwise."""
    data = {
        "request": "gate:plan-accept",
        "kind": "approve",
        "action": "accept",
        "workflow": "sdd-proposal",
        "stage": "direction-handoff",
        "at": "2026-10-13T00:00:00Z",
    }
    data |= fields
    path = root / UNIT.format(slug=slug) / "decisions" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _answered(root: Path, slug: str, *, by: str = "user") -> None:
    _record(root, slug, "01-gate-plan-intent.yaml", request="gate:plan-intent", stage="intent-proposal", by="user")
    _record(root, slug, "02-gate-plan-accept.yaml", request="gate:plan-accept", stage="direction-handoff", by=by)


def _spec_records(root: Path, slug: str) -> list[dict[str, object]]:
    directory = spec_dir(root, slug) / "decisions"
    if not directory.is_dir():
        return []
    return [yaml.safe_load(path.read_text(encoding="utf-8")) for path in sorted(directory.iterdir())]


def test_drops_the_unit_records_and_carries_the_rest(workspace: Path, write: Write) -> None:
    proposal = _proposal(workspace, "records")
    unit = UNIT.format(slug="records")
    _answered(workspace, "records")
    write(f"{unit}/decisions/03-broken.yaml", "request: [\n")
    write(f"{unit}/decisions/notes.yaml", "kept: true\n")
    write(f"{unit}/envelopes/scout-01.yaml", "kind: scout\n")
    write(f"{unit}/notes.md", "# Notes\n")
    CreateProposalDecisionUseCase().execute(workspace, "records", "Use records")
    accept(proposal)

    result = handoff_proposal(workspace, "records", today=TODAY)

    assert result.dropped_records == [
        f"{unit}/decisions/01-gate-plan-intent.yaml",
        f"{unit}/decisions/02-gate-plan-accept.yaml",
        f"{unit}/decisions/03-broken.yaml",
        f"{unit}/envelopes/scout-01.yaml",
    ]
    materials = workspace / f"docs/materials/{MONTH}/{STAMP}-records"
    assert sorted(path.relative_to(materials).as_posix() for path in materials.rglob("*") if path.is_file()) == [
        "decisions/notes.yaml",
        "notes.md",
    ]
    assert [decision.padr for decision in result.decisions] == ["PADR-use-records"]
    assert not (workspace / unit).exists()
    assert not (spec_dir(workspace, "records") / "envelopes").exists()


def test_records_alone_create_no_materials_directory(workspace: Path) -> None:
    proposal = _proposal(workspace, "bare")
    _answered(workspace, "bare")
    accept(proposal)
    result = handoff_proposal(workspace, "bare", today=TODAY)
    assert result.materials is None
    assert not (workspace / "docs/materials").exists()
    assert len(result.dropped_records) == 2


def test_carries_plan_intent_and_plan_accept_under_their_names(workspace: Path) -> None:
    accept(_proposal(workspace, "carry"))
    _answered(workspace, "carry")

    result = handoff_proposal(workspace, "carry", today=TODAY)

    spec = f"specs/{MONTH}/{STAMP}-carry"
    assert result.carried_gates == [
        CarriedGate("gate:plan-intent", f"{spec}/decisions/01-gate-plan-intent.yaml"),
        CarriedGate("gate:plan-accept", f"{spec}/decisions/02-gate-plan-accept.yaml"),
    ]
    records = _spec_records(workspace, "carry")
    assert [(r["request"], r["action"], r["by"], r["note"], r["workflow"], r["stage"]) for r in records] == [
        ("gate:plan-intent", "accept", "user", "PROP-carry", "sdd-spec-feature", "intent"),
        ("gate:plan-accept", "accept", "user", "PROP-carry", "sdd-spec-feature", "direction-handoff"),
    ]
    assert result.notices == []
    ws = Workspace(workspace, lint=None, ancestor=None)
    evaluation = ws.evaluate_unit(ws.resolve_unit(spec), lint=False)
    # plan-intent opens the spec; plan-accept is kept for the audit trail and asks nothing.
    assert evaluation.to_dict()["done"] == ["intent"]
    assert evaluation.requests == [] and evaluation.decision_errors == []


def test_a_bugfix_spec_carries_both_records(workspace: Path) -> None:
    accept(_proposal(workspace, "defect"), "\ntask_kind: bugfix")
    _answered(workspace, "defect")
    result = handoff_proposal(workspace, "defect", today=TODAY)
    assert result.workflow == "sdd-spec-bugfix"
    assert [gate.request for gate in result.carried_gates] == ["gate:plan-intent", "gate:plan-accept"]


def test_keeps_who_answered(workspace: Path) -> None:
    accept(_proposal(workspace, "remote"))
    _answered(workspace, "remote", by="autohub")
    handoff_proposal(workspace, "remote", today=TODAY)
    assert [record["by"] for record in _spec_records(workspace, "remote")] == ["user", "autohub"]


@pytest.mark.parametrize(
    "records",
    [
        [],
        [("02-gate-plan-accept.yaml", {"by": "user", "action": "decline"})],
        [("02-gate-plan-accept.yaml", {"by": "user", "action": "cancel"})],
        [
            ("02-gate-plan-accept.yaml", {"by": "user"}),
            ("03-gate-plan-accept.yaml", {"by": "user", "action": "decline"}),
            ("04-gate-plan-accept.yaml", {"by": "user", "action": "cancel"}),
        ],
        [
            ("02-gate-plan-accept.yaml", {"by": "user"}),
            ("03-return-spike.yaml", {"request": "return:spike", "kind": "return", "stage": "spike", "by": "user"}),
        ],
        [("02-gate-plan-accept.yaml", {"by": "user", "workflow": "other"})],
    ],
    ids=["none", "declined", "cancelled", "declined-after-accept", "returned", "other-workflow"],
)
def test_a_bound_proposal_without_an_accepted_record_is_not_handed_off(
    workspace: Path, records: list[tuple[str, dict[str, object]]]
) -> None:
    proposal = _proposal(workspace, "ask")
    accept(proposal)
    for name, fields in records:
        _record(workspace, "ask", name, **fields)
    assert load_decisions(workspace / UNIT.format(slug="ask")).errors == []
    with pytest.raises(ProposalAcceptanceUnrecordedError) as raised:
        handoff_proposal(workspace, "ask", today=TODAY)
    assert raised.value.code == "SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED" and raised.value.actor == "USER"
    assert raised.value.fix is not None and "--direct" in raised.value.fix and "never record" in raised.value.fix
    assert proposal.is_file() and not (workspace / "specs").exists()


def test_an_unbound_or_single_file_proposal_hands_off_on_its_status(workspace: Path) -> None:
    write_workflow(workspace, "sdd-spec-feature", GATED.format(id="sdd-spec-feature", middle=""))
    accept(workspace / create_proposal(workspace, "bare", today=TODAY).path)  # sdd-proposal unavailable: unbound
    single = workspace / "docs/proposals/PROP-solo.md"
    single.write_text("---\nid: PROP-solo\nstatus: accepted\n---\n\n# Solo\n", encoding="utf-8")
    assert handoff_proposal(workspace, "bare", today=TODAY).carried_gates == []
    assert handoff_proposal(workspace, "solo", today=TODAY).carried_gates == []


def test_a_proposal_bound_to_another_workflow_hands_off_on_its_status(workspace: Path) -> None:
    proposal = _proposal(workspace, "custom")
    write_workflow(workspace, "custom-proposal", PROPOSAL_WORKFLOW.replace("id: sdd-proposal", "id: custom-proposal"))
    text = proposal.read_text(encoding="utf-8").replace("workflow: sdd-proposal", "workflow: custom-proposal")
    proposal.write_text(text, encoding="utf-8")
    accept(proposal)
    assert handoff_proposal(workspace, "custom", today=TODAY).carried_gates == []


def test_the_carried_acceptance_keeps_the_proposals_note(workspace: Path) -> None:
    accept(_proposal(workspace, "noted"))
    note = "direct acceptance, Planning skipped: X; task_kind feature confirmed"
    _record(
        workspace, "noted", "01-gate-plan-intent.yaml", request="gate:plan-intent", stage="intent-proposal", by="user"
    )
    _record(workspace, "noted", "02-gate-plan-accept.yaml", by="user", note=note)
    handoff_proposal(workspace, "noted", today=TODAY)
    assert [record["note"] for record in _spec_records(workspace, "noted")] == [
        "PROP-noted",
        f"PROP-noted: {note}",
    ]


def test_a_cancel_after_the_users_accept_changes_nothing(workspace: Path) -> None:
    accept(_proposal(workspace, "cancel"))
    _answered(workspace, "cancel")
    _record(workspace, "cancel", "03-gate-plan-accept.yaml", by="user", action="cancel")
    result = handoff_proposal(workspace, "cancel", today=TODAY)
    assert [gate.request for gate in result.carried_gates] == ["gate:plan-intent", "gate:plan-accept"]


def test_records_nothing_for_an_unbound_spec(workspace: Path) -> None:
    write_workflow(workspace, "sdd-proposal", PROPOSAL_WORKFLOW)
    accept(workspace / create_proposal(workspace, "loose", today=TODAY).path)
    _answered(workspace, "loose")
    result = handoff_proposal(workspace, "loose", today=TODAY)
    assert result.workflow is None and result.carried_gates == []
    assert _spec_records(workspace, "loose") == []


def test_a_recording_failure_is_a_warning(workspace: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    accept(_proposal(workspace, "fails"))
    _answered(workspace, "fails")

    def write_decision(*args: object, **kwargs: object) -> object:
        raise OSError("disk full")

    monkeypatch.setattr(handoff_module, "write_decision", write_decision)
    result = handoff_proposal(workspace, "fails", today=TODAY)

    assert [gate.request for gate in result.carried_gates] == ["gate:plan-intent"]
    assert [record["request"] for record in _spec_records(workspace, "fails")] == ["gate:plan-intent"]
    [notice] = result.notices
    assert notice.code == "SPEC_PROPOSAL_GATE_NOT_CARRIED"
    assert "gate:plan-accept" in notice.message and "disk full" in notice.details
    spec = f"specs/{MONTH}/{STAMP}-fails"
    assert notice.fix is not None and f"uv run devkit workflow next --unit {spec}" in notice.fix
    assert not (workspace / UNIT.format(slug="fails")).exists()


@pytest.mark.parametrize("history", ["committed", "dirty", "untracked", "no-git"])
def test_historical_record_citations(workspace: Path, write: Write, history: str) -> None:
    proposal = _proposal(workspace, "history")
    _answered(workspace, "history")
    accept(proposal)
    CreateProposalDecisionUseCase().execute(workspace, "history", "Record evidence")
    record = write("docs/proposals/PROP-history/envelopes/answer-01.yaml", "kind: answer\n")
    padr = proposal.parent / "decisions/PADR-record-evidence.md"
    padr.write_text(
        padr.read_text() + "\nAnswer `envelopes/answer-01.yaml`. "
        "[answer](../envelopes/answer-01.yaml).\n\n```text\n`envelopes/answer-01.yaml`\n```\n"
    )
    outside = write("docs/evidence.md", "[answer](proposals/PROP-history/envelopes/answer-01.yaml)\n")
    head = ""
    if history != "no-git":
        run_git(workspace, "init", "-b", "dev-history")
        run_git(workspace, "add", ".")
        if history == "untracked":
            run_git(workspace, "rm", "--cached", record.relative_to(workspace).as_posix())
        run_git(
            workspace,
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "-c",
            "core.hooksPath=/dev/null",
            "commit",
            "-m",
            "Evidence",
        )
        head = run_git(workspace, "rev-parse", "HEAD").decode().strip()
        if history == "dirty":
            record.write_text("kind: answer\nsummary: changed\n")

    result = handoff_proposal(workspace, "history", today=TODAY)

    adr = (workspace / f"docs/decisions/{MONTH}/{STAMP}-record-evidence.md").read_text()
    assert not record.exists()
    assert "```text\n`envelopes/answer-01.yaml`\n```" in adr
    if history == "committed":
        pin = f"{head}:docs/proposals/PROP-history/envelopes/answer-01.yaml"
        assert f"historical Git `{pin}`" in adr
        assert adr.count(pin) == 2
        assert f"historical Git `{pin}`" in outside.read_text()
        assert run_git(workspace, "show", pin) == b"kind: answer\n"
        assert len([item for item in result.rewritten if pin in item.new]) == 3
        assert not result.unresolved
    else:
        assert "Answer `envelopes/answer-01.yaml`." in adr
        assert "historical Git" not in adr + outside.read_text()
        assert len([item for item in result.unresolved if "answer-01.yaml" in item.target]) == 3
