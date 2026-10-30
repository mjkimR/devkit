"""The composed acceptance's refusals render the directive their table rows document (``CAP-DLV-proposal-planning``).

Planning that is not ready for plan-accept and a changed source, base or acceptance delta are the user's to review
(``INTERACTION``); a mode or effort the caller corrects, a checkout off the retained base and a refused acceptance
commit are ``INPUT_ERROR``; ``--by policy`` without owning ``plan-accept=auto`` is ``BLOCKED``. Every code is a
``SPEC_`` code of ``devkit_spec.base.errors``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from devkit_spec.base.errors import (
    ProposalAcceptCommitRefusedError,
    ProposalApprovalNotReadyError,
    ProposalApprovalReplyError,
    ProposalApprovalStaleError,
    ProposalPolicyNotAutoError,
)
from devkit_spec.features.delivery.usecases.native_plan_accept import PlanAcceptUseCase


# AC-01
def test_planning_not_ready_for_plan_accept_asks_the_user() -> None:
    advisory = ProposalApprovalNotReadyError("Planning of PROP-x is not ready", "unmet: x").to_dict()["advisory"]
    assert advisory["code"] == "SPEC_PROPOSAL_APPROVAL_NOT_READY"
    assert advisory["mode"] == "INTERACTION"
    assert "[DETAIL]" in advisory["what_to_report"]


# AC-02
def test_an_invalid_approval_reply_is_an_input_error() -> None:
    advisory = ProposalApprovalReplyError("choose a valid mode and Development effort").to_dict()["advisory"]
    assert advisory["code"] == "SPEC_PROPOSAL_APPROVAL_REPLY_INVALID"
    assert advisory["mode"] == "INPUT_ERROR"
    assert advisory["target_files"] == ["--mode", "--effort"]
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
def test_a_stale_approval_asks_the_user() -> None:
    advisory = ProposalApprovalStaleError("source, base, configuration or execution environment changed").to_dict()[
        "advisory"
    ]
    assert advisory["code"] == "SPEC_PROPOSAL_APPROVAL_STALE"
    assert advisory["mode"] == "INTERACTION"


def test_a_refused_acceptance_commit_and_a_policy_refusal() -> None:
    commit = ProposalAcceptCommitRefusedError("refused", target_files=["plan-x"]).to_dict()["advisory"]
    assert (commit["code"], commit["mode"]) == ("SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED", "INPUT_ERROR")
    policy = ProposalPolicyNotAutoError("--by policy").to_dict()["advisory"]
    assert (policy["code"], policy["mode"]) == ("SPEC_PROPOSAL_POLICY_NOT_AUTO", "BLOCKED")
    assert "fix" not in policy
