"""The composed handoff's refusals render the directive their table rows document (``CAP-DLV-proposal-planning``).

Each condition has its own code: a proposal that is not ready, a dirty base, a Development worktree devkit cannot
reuse and a changed base or worktree are the user's to decide (``INTERACTION``); an effort the caller corrects is
``INPUT_ERROR``. No fix asks for a published report: acceptance and handoff take none.
"""

from __future__ import annotations

import pytest

from devkit_spec.base.errors import (
    HandoffBaseDirtyError,
    HandoffNotReadyError,
    HandoffReplyError,
    HandoffStaleError,
    HandoffWorktreeConflictError,
    ProposalApprovalNotReadyError,
    ProposalApprovalStaleError,
    SpecError,
)


# AC-01
@pytest.mark.parametrize(
    ("error", "code"),
    [
        (HandoffNotReadyError, "SPEC_HANDOFF_NOT_READY"),
        (HandoffBaseDirtyError, "SPEC_HANDOFF_BASE_DIRTY"),
        (HandoffWorktreeConflictError, "SPEC_HANDOFF_WORKTREE_CONFLICT"),
        (HandoffStaleError, "SPEC_HANDOFF_STALE"),
    ],
)
def test_an_unmet_handoff_prerequisite_asks_the_user(error: type[SpecError], code: str) -> None:
    advisory = error("not ready").to_dict()["advisory"]
    assert advisory["code"] == code
    assert advisory["mode"] == "INTERACTION"
    assert advisory["what_to_report"]
    assert "report" not in advisory.get("fix", "")


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
    assert advisory["target_files"] == ["--effort"]


# AC-03
@pytest.mark.parametrize("error", [HandoffStaleError, ProposalApprovalStaleError, ProposalApprovalNotReadyError])
def test_no_fix_asks_to_publish_a_report(error: type[SpecError]) -> None:
    fix = error("changed").to_dict()["advisory"].get("fix", "")
    assert "report" not in fix


def test_fixes_name_no_placeholder_choices() -> None:
    from devkit_spec.base.errors import acceptance_unrecorded_fix
    from devkit_spec.features.delivery.usecases.native_handoff import _handoff_command

    assert "<" not in acceptance_unrecorded_fix("idea")
    assert "`uv run devkit spec proposal accept idea --by user --direct --note`" in acceptance_unrecorded_fix("idea")
    assert (
        _handoff_command("idea", None) == "`uv run devkit spec proposal handoff idea --effort` with low, medium or high"
    )
    assert _handoff_command("idea", "high") == "`uv run devkit spec proposal handoff idea --effort high`"


# SPEC-git-operator-result-readiness AC-02
def test_a_refused_handoff_commit_is_an_input_error_whose_fix_commits_in_the_worktree(tmp_path, monkeypatch) -> None:
    from devkit_spec.base.errors import HandoffCommitRefusedError
    from devkit_spec.features.delivery.usecases import native_handoff

    def refuse(root, *args, **kwargs):
        if args[:1] == ("commit",):
            raise native_handoff.GitError("git commit failed", stderr="hook said no\n")
        return {"rev-parse": "f" * 40}.get(args[0], "")

    monkeypatch.setattr(native_handoff, "run_git_text", refuse)
    monkeypatch.setattr(native_handoff, "_dirty_paths", lambda root: ["specs/x/spec.md"])
    monkeypatch.setattr(native_handoff, "guard_execution", lambda: None)
    with pytest.raises(HandoffCommitRefusedError) as caught:
        native_handoff._commit_handoff(tmp_path, "idea", "f" * 40)
    advisory = caught.value.to_dict()["advisory"]
    assert advisory["code"] == "SPEC_HANDOFF_COMMIT_REFUSED" and advisory["mode"] == "INPUT_ERROR"
    assert advisory["details"] == ["hook said no"] and advisory["target_files"] == ["specs/x/spec.md"]
    assert f"git -C {tmp_path} commit" in advisory["fix"] and "do not rerun" in advisory["fix"]
    assert "<" not in advisory["fix"] and "report" not in advisory["fix"]
