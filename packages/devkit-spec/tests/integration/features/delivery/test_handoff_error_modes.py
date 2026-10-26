"""The composed handoff's refusals render the directive their table rows document (``CAP-DLV-proposal-incubation``).

A prerequisite the user or Host resolves is ``BLOCKED`` and an effort the caller corrects is ``INPUT_ERROR``; only a
changed base or worktree stays a ``MAINTENANCE`` stop. No fix asks for a published report: acceptance and handoff
take none.
"""

from __future__ import annotations

import pytest

from devkit_spec.base.errors import HandoffNotReadyError, HandoffReplyError, HandoffStaleError, SpecError
from devkit_spec.features.delivery.usecases.native_plan_accept import (
    ProposalApprovalNotReadyError,
    ProposalApprovalStaleError,
)


# AC-01
@pytest.mark.parametrize(
    "message",
    [
        "the base checkout has uncommitted changes; commit or resolve them before review",
        "the proposal must be accepted and must not need decomposition",
        "existing Development worktree provenance or clean source differs",
        "proposal-handoff policy must be ask or auto",
    ],
)
def test_an_unmet_handoff_prerequisite_is_blocked(message: str) -> None:
    advisory = HandoffNotReadyError(message).to_dict()["advisory"]
    assert advisory["code"] == "SPEC_HANDOFF_NOT_READY"
    assert advisory["mode"] == "BLOCKED"
    assert advisory["guardrail"] is True
    assert "report" not in advisory["fix"]


# AC-02
@pytest.mark.parametrize(
    "message",
    [
        "choose low, medium or high Development effort",
        "automatic handoff must use the proposal's declared dev_effort",
        "Host approval must include a Development effort of low, medium or high",
    ],
)
def test_an_invalid_handoff_effort_is_an_input_error(message: str) -> None:
    advisory = HandoffReplyError(message).to_dict()["advisory"]
    assert advisory["code"] == "SPEC_HANDOFF_REPLY_INVALID"
    assert advisory["mode"] == "INPUT_ERROR"
    assert advisory["input_error"] is True


# AC-03
def test_a_stale_handoff_stays_maintenance() -> None:
    advisory = HandoffStaleError("the base, accepted plan or policy changed after review").to_dict()["advisory"]
    assert advisory["code"] == "SPEC_HANDOFF_STALE"
    assert advisory["mode"] == "MAINTENANCE"


# AC-03
@pytest.mark.parametrize("error", [HandoffStaleError, ProposalApprovalStaleError, ProposalApprovalNotReadyError])
def test_no_fix_asks_to_publish_a_report(error: type[SpecError]) -> None:
    fix = error("changed").to_dict()["advisory"]["fix"]
    assert "report" not in fix
