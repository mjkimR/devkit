"""Errors and warnings of ``devkit.worktree``: ``AdvisoryError`` subclasses, one class per code.

Every refusal leaves the repository as it was before the refused step; the
earlier steps of ``finish`` stay done, so rerunning the same command resumes.
A refusal raised after ``finish`` changed something carries the partial
``FinishResult`` as ``result``; a Git failure there is one of its own codes
(``WORKTREE_REMOVE_FAILED``, ``WORKTREE_BRANCH_DELETE_FAILED``), except that
unsetting the marker of a kept branch is ``GIT_FAILED`` (the rerun resumes
and unsets it). Before that,
``devkit.core`` errors pass through unchanged: a failed Git command is
``GitError`` (``GIT_FAILED``), an unreadable ``.devkit/config.toml``
``ConfigError`` (``CONFIG_INVALID``).
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
    """``finish --merge`` under ``[worktree] pull_request = "required"`` (``BLOCKED``): integration is a PR."""

    code = "WORKTREE_PR_POLICY"
    fix = "Merge the pull request, then run finish without --merge"


class UnsupportedLayoutError(_Guardrail):
    """A bare repository or a Git directory outside its work tree (``BLOCKED``)."""

    code = "WORKTREE_UNSUPPORTED_LAYOUT"
    fix = "Use a plain (non-bare) repository checkout whose .git directory sits in its work tree"


class ConflictError(_Interaction):
    """The slug's path or branch is not a task worktree ``start`` can reuse or ``finish`` can remove (``INTERACTION``).

    ``start``: the path is a worktree on another branch, with uncommitted changes or with its directory missing, or
    it exists and is not a worktree. ``finish``: the worktree is detached or on another branch, or the slug's branch
    is the base checkout's. The ``[FIX]`` names the step for each.
    """

    code = "WORKTREE_CONFLICT"
    fix = "Finish or clean up that worktree, or choose another slug"


class BranchExistsError(_Interaction):
    """A branch named after the slug already exists or is checked out elsewhere (``INTERACTION``)."""

    code = "WORKTREE_BRANCH_EXISTS"
    fix = "Delete or rename that branch, or choose another slug"


class NotFoundError(_Interaction):
    """No worktree has the slug's path or branch (``INTERACTION``).

    For ``finish``, also when the slug's merged branch lacks the marker ``start`` records (or a finish already
    completed for it): nothing runs, merges, pushes or is deleted for that branch, and with ``delete_branch`` the
    ``[FIX]`` deletes it only once the user agrees.
    """

    code = "WORKTREE_NOT_FOUND"
    fix = "Check `devkit worktree status` or `git worktree list` for the slug"


class LockedError(_Interaction):
    """``finish`` found the slug's worktree locked (``git worktree lock``, ``INTERACTION``); nothing changed."""

    code = "WORKTREE_LOCKED"
    fix = "Unlock the worktree (git worktree unlock <path>) once the user agrees, then rerun"


class BaseDetachedError(_Interaction):
    """``finish --merge`` found the base checkout on a detached HEAD (``INTERACTION``); nothing changed.

    A fast-forward would move no branch and the push would be skipped, leaving the task's commits on no branch
    once the slug's branch is deleted.
    """

    code = "WORKTREE_BASE_DETACHED"
    fix = "Check out the branch the task integrates into in the base checkout (git switch <branch>), then rerun"


class BaseBehindError(_Interaction):
    """``finish --merge`` fetched the base branch's upstream and it has commits the base lacks (``INTERACTION``).

    The push after the merge would be rejected; nothing changed. The ``[FIX]`` brings the base up to date.
    """

    code = "WORKTREE_BASE_BEHIND"
    fix = "Fast-forward the base onto its upstream (git pull --ff-only), integrate the base into the branch, then rerun"


class BranchUnpushedError(_Interaction):
    """The slug's branch has an upstream that lacks its commits, so ``git branch -d`` would refuse it (``INTERACTION``).

    Raised before any change; the ``[FIX]`` pushes the branch to that upstream.
    """

    code = "WORKTREE_BRANCH_UNPUSHED"
    fix = "Push the branch to its upstream, then rerun"


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
        "Merge the branch first (its pull request, or `finish --merge` unless pull requests are required); a "
        "squash or rebase merge leaves the branch unmerged, so remove that worktree and branch only with the user's "
        "authorization"
    )


class DirtyError(_Interaction):
    """The worktree has uncommitted changes (``INTERACTION``); it is never removed by force."""

    code = "WORKTREE_DIRTY"
    fix = "Commit or discard the changes in the worktree, then rerun"


class RemoveFailedError(_Interaction):
    """``git worktree remove`` failed for a reason other than uncommitted changes (``INTERACTION``).

    Raised with the partial ``result`` (after the merge, under ``--merge``); rerunning the same command resumes.
    """

    code = "WORKTREE_REMOVE_FAILED"
    fix = "Resolve the cause Git reports, then rerun the same command; the steps already done are skipped"


class AddFailedError(_Interaction):
    """``git worktree add`` or the branch marker failed, or the add timed out, in ``start`` (``INTERACTION``).

    ``start`` removes what the failed call created (the registered worktree and its directory, and the branch); the
    ``[FIX]`` names what it could not remove, so a rerun does not stop at ``WORKTREE_CONFLICT`` or
    ``WORKTREE_BRANCH_EXISTS``.
    """

    code = "WORKTREE_ADD_FAILED"
    fix = "Resolve the cause Git reports, then rerun the same command; nothing of the failed attempt remains"


class BranchDeleteFailedError(_Interaction):
    """``git branch -d`` refused the slug's branch after the worktree was removed (``INTERACTION``).

    Raised with the partial ``result``; rerunning the same command finds the merged branch without its worktree
    and deletes it.
    """

    code = "WORKTREE_BRANCH_DELETE_FAILED"
    fix = "Resolve the cause Git reports, then rerun the same command; the steps already done are skipped"


class WorktreeConfigError(WorktreeError, ConfigError):
    """The ``[worktree]`` table of ``.devkit/config.toml`` is malformed (``INPUT_ERROR``, as ``CONFIG_INVALID``)."""

    code = "WORKTREE_CONFIG_INVALID"
    target_files = ()
    fix = "Correct the [worktree] table in .devkit/config.toml"


class PushFailedWarning(WorktreeError):
    """``finish --merge`` merged and cleaned up, but the base branch did not reach its upstream (``WARNING``)."""

    code = "WORKTREE_PUSH_FAILED"
    level = Level.WARNING


class PushRejectedWarning(WorktreeError):
    """``finish --merge`` merged and cleaned up, but the upstream moved on and rejected the push (``WARNING``).

    The ``[FIX]`` integrates the upstream into the base, then pushes; rerunning the push alone fails identically.
    """

    code = "WORKTREE_PUSH_REJECTED"
    level = Level.WARNING


class SetupFailedWarning(WorktreeError):
    """``start`` created the worktree, but its ``setup`` command failed or timed out (``WARNING``)."""

    code = "WORKTREE_SETUP_FAILED"
    level = Level.WARNING


class SyncFailedWarning(WorktreeError):
    """``start`` created the worktree, but ``devkit sync --locked`` could not restore its managed files
    (``WARNING``)."""

    code = "WORKTREE_SYNC_FAILED"
    level = Level.WARNING


class PostFinishNotice(WorktreeError):
    """A line a ``devkit.post_finish`` extension returned; its package owns its meaning (``NOTICE``, ``brief``)."""

    code = "POST_FINISH_NOTICE"
    level = Level.NOTICE
    brief = True


class PostFinishExtensionFailedNotice(WorktreeError):
    """A ``devkit.post_finish`` extension raised or returned something other than a list; the finish itself succeeded
    (``WARNING``)."""

    code = "POST_FINISH_EXTENSION_FAILED"
    level = Level.WARNING
