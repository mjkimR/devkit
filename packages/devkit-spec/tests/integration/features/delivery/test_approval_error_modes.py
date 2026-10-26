"""The composed acceptance's refusals render the directive their table rows document (``CAP-DLV-proposal-incubation``).

An unmet Planning or worktree prerequisite is ``BLOCKED``, a mode or effort the caller corrects is ``INPUT_ERROR``,
and only a changed source, base or acceptance delta stays a ``MAINTENANCE`` stop.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from devkit_spec.features.delivery.usecases.native_plan_accept import (
    PlanAcceptUseCase,
    ProposalApprovalNotReadyError,
    ProposalApprovalReplyError,
    ProposalApprovalStaleError,
)


# AC-01
@pytest.mark.parametrize(
    "message",
    [
        "Planning has unmet checks, problems, questions or decomposition",
        "proposal is not ready for plan-accept",
        "dev_effort must be low, medium or high",
        "run the service from the retained base checkout",
    ],
)
def test_an_unmet_approval_prerequisite_is_blocked(message: str) -> None:
    advisory = ProposalApprovalNotReadyError(message).to_dict()["advisory"]
    assert advisory["code"] == "PROPOSAL_APPROVAL_NOT_READY"
    assert advisory["mode"] == "BLOCKED"
    assert advisory["guardrail"] is True


# AC-02
def test_an_invalid_approval_reply_is_an_input_error() -> None:
    advisory = ProposalApprovalReplyError("choose a valid mode and Development effort").to_dict()["advisory"]
    assert advisory["code"] == "PROPOSAL_APPROVAL_REPLY_INVALID"
    assert advisory["mode"] == "INPUT_ERROR"
    assert advisory["input_error"] is True
    for word in ("accept_only", "accept_and_handoff", "low", "medium", "high"):
        assert word in advisory["fix"]


# AC-02
@pytest.mark.parametrize(("mode", "effort"), [("accept_later", "medium"), ("accept_and_handoff", None)])
def test_the_cli_use_case_refuses_an_invalid_mode_or_effort_as_input(
    tmp_path: Path, mode: str, effort: str | None
) -> None:
    with pytest.raises(ProposalApprovalReplyError) as caught:
        PlanAcceptUseCase(tmp_path).execute("demo", mode=mode, effort=effort)
    assert caught.value.to_dict()["advisory"]["mode"] == "INPUT_ERROR"


# AC-03
def test_a_stale_approval_stays_maintenance() -> None:
    advisory = ProposalApprovalStaleError("source, base, configuration or execution environment changed").to_dict()[
        "advisory"
    ]
    assert advisory["code"] == "PROPOSAL_APPROVAL_STALE"
    assert advisory["mode"] == "MAINTENANCE"
