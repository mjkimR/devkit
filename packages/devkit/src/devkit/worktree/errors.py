"""Errors and warnings of ``devkit.worktree``: ``AdvisoryError`` subclasses, one class per code.

Every refusal leaves the repository as it was before the refused step; the
earlier steps of ``finish`` stay done, so rerunning the same command resumes.
A refusal raised after ``finish`` changed something carries the partial
``FinishResult`` as ``result``. ``devkit.core`` errors pass through unchanged:
a failed Git command is ``GitError`` (``GIT_FAILED``), an unreadable
``.devkit/config.toml`` ``ConfigError`` (``CONFIG_INVALID``).
"""

from __future__ import annotations

from typing import Any

from devkit.advisory import Actor, AdvisoryError, Level, Retry
from devkit.core.errors import ConfigError


class WorktreeError(AdvisoryError):
    """Base class of every error raised by ``devkit.worktree``; on its own an internal defect (``MAINTENANCE``)."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    result: Any = None  # the partial FinishResult when finish stopped after changing something


class _Interaction(WorktreeError):
    actor = Actor.USER


class _Guardrail(WorktreeError):
    guardrail = True


class NestedError(_Guardrail):
    """``start`` ran inside a linked worktree (``BLOCKED``); task worktrees are created from the base checkout."""

    code = "WORKTREE_NESTED"
    fix = "Run the command from the base checkout, or keep working in this worktree"


class RunFromBaseError(_Guardrail):
    """``finish`` ran inside a linked worktree (``BLOCKED``): it would remove the checkout it runs in."""

    code = "WORKTREE_RUN_FROM_BASE"
    fix = "cd to the base checkout and rerun there"


class PullRequestPolicyError(_Guardrail):
    """``finish --merge`` under ``[worktree] pull_request = true`` (``BLOCKED``): integration goes through a PR."""

    code = "WORKTREE_PR_POLICY"
    fix = "Merge the pull request, then run finish without --merge"


class UnsupportedLayoutError(_Guardrail):
    """A bare repository or a Git directory outside its work tree (``BLOCKED``)."""

    code = "WORKTREE_UNSUPPORTED_LAYOUT"
    fix = "Use a plain (non-bare) repository checkout whose .git directory sits in its work tree"


class ConflictError(_Interaction):
    """The slug's worktree path holds another branch, has uncommitted changes or is not a worktree (``INTERACTION``)."""

    code = "WORKTREE_CONFLICT"
    fix = "Finish or clean up that worktree, or choose another slug"


class BranchExistsError(_Interaction):
    """A branch named after the slug already exists or is checked out elsewhere (``INTERACTION``)."""

    code = "WORKTREE_BRANCH_EXISTS"
    fix = "Delete or rename that branch, or choose another slug"


class NotFoundError(_Interaction):
    """No worktree has the slug's path or branch (``INTERACTION``)."""

    code = "WORKTREE_NOT_FOUND"
    fix = "Check `devkit worktree status` or `git worktree list` for the slug"


class BaseDirtyError(_Interaction):
    """``finish --merge`` found uncommitted changes in the base checkout (``INTERACTION``)."""

    code = "WORKTREE_BASE_DIRTY"
    fix = "Commit or stash the base checkout's changes, then rerun"


class MergeNotFastForwardError(_Interaction):
    """The base moved on since the branch was created, so ``--merge`` cannot fast-forward it (``INTERACTION``)."""

    code = "WORKTREE_MERGE_NOT_FF"
    fix = "Integrate the base into the branch first (rebase or merge it in the worktree), then rerun"


class UnmergedError(_Interaction):
    """``finish`` without ``--merge`` found the branch not merged into the base (``INTERACTION``); nothing changed."""

    code = "WORKTREE_UNMERGED"
    fix = (
        "Merge the branch first (its pull request, or `finish --merge` without the PR policy); a squash or rebase "
        "merge leaves the branch unmerged, so remove that worktree and branch only with the user's authorization"
    )


class DirtyError(_Interaction):
    """The worktree has uncommitted changes (``INTERACTION``); it is never removed by force."""

    code = "WORKTREE_DIRTY"
    fix = "Commit or discard the changes in the worktree, then rerun"


class WorktreeConfigError(WorktreeError, ConfigError):
    """The ``[worktree]`` table of ``.devkit/config.toml`` is malformed (``MAINTENANCE``)."""

    code = "WORKTREE_CONFIG_INVALID"
    target_files = ()
    fix = "Correct the [worktree] table in .devkit/config.toml"


class PushFailedWarning(WorktreeError):
    """``finish --merge`` merged and cleaned up, but the base branch did not reach its upstream (``WARNING``)."""

    code = "WORKTREE_PUSH_FAILED"
    level = Level.WARNING


class SetupFailedWarning(WorktreeError):
    """``start`` created the worktree, but its ``setup`` command failed or timed out (``WARNING``)."""

    code = "WORKTREE_SETUP_FAILED"
    level = Level.WARNING


class SyncFailedWarning(WorktreeError):
    """``start`` created the worktree, but ``devkit sync`` could not restore its managed files (``WARNING``)."""

    code = "WORKTREE_SYNC_FAILED"
    level = Level.WARNING
