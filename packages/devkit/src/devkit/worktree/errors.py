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


class BaseOnBranchError(WorktreeError):
    """``finish`` or ``finish --discard`` ran while the base checkout is on the ``--no-worktree`` branch it finishes
    (``AUTO``): switching back to the recorded ``devkitBase`` is the routine step, so ``[FIX]`` is that switch."""

    code = "WORKTREE_BASE_ON_BRANCH"
    actor = Actor.TOOL


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
    fix = "Use integration_integrate with route=pull-request for native approval, or merge the PR under existing authority and run finish without --merge"


class UnsupportedLayoutError(_Guardrail):
    """A bare repository or a Git directory outside its work tree (``BLOCKED``)."""

    code = "WORKTREE_UNSUPPORTED_LAYOUT"
    fix = "Use a plain (non-bare) repository checkout whose .git directory sits in its work tree"


class ConflictError(_Interaction):
    """The activity branch or its path is not a task worktree ``start`` can reuse or ``finish`` can remove (``INTERACTION``).

    ``start``: the path is a worktree on another branch, with uncommitted changes or with its directory missing, or
    it exists and is not a worktree. ``finish``: the worktree is detached or on another branch, or the branch
    is the base checkout's. The ``[FIX]`` names the step for each.
    """

    code = "WORKTREE_CONFLICT"
    fix = "Finish or clean up that worktree, or choose another slug"


class BranchExistsError(_Interaction):
    """The activity branch already exists locally or on a remote, or is checked out elsewhere (``INTERACTION``).

    A new ``start`` never takes over an existing branch; the ``[FIX]`` names the ``--existing-branch`` path that
    attaches it explicitly.
    """

    code = "WORKTREE_BRANCH_EXISTS"
    fix = "Continue the existing branch with --existing-branch <branch> --unit <dir>, or choose another slug"


class BranchOutOfSyncError(_Interaction):
    """``start --existing-branch``: the local branch lacks commits of its remote-tracking branch (``INTERACTION``).

    devkit never merges or resets to reconcile them; nothing changed. A local branch ahead of the remote is attached.
    """

    code = "WORKTREE_BRANCH_OUT_OF_SYNC"
    fix = "Bring the local branch up to date with the remote branch, then rerun"


class UnitInvalidError(WorktreeError):
    """``start --existing-branch``: ``--unit`` is not a directory of the branch's tree (``INPUT_ERROR``)."""

    code = "WORKTREE_UNIT_INVALID"
    input_error = True
    fix = "Pass --unit as the unit directory relative to the devkit project, as it exists on the branch"


class AttachRefusedError(_Interaction):
    """A ``devkit.attach_check`` extension found that the branch and the unit do not belong together (``INTERACTION``).

    Each reason is a detail; nothing changed.
    """

    code = "WORKTREE_ATTACH_REFUSED"
    fix = "Pass the unit that belongs to this activity branch, or the branch that belongs to this unit"


class AttachCheckFailedError(WorktreeError):
    """A ``devkit.attach_check`` extension raised or returned something other than a list of strings
    (``MAINTENANCE``); the attach is refused, since the correspondence was not verified."""

    code = "WORKTREE_ATTACH_CHECK_FAILED"
    fix = "Repair or uninstall the package that registers the failing extension, then rerun"


class BlockedError(_Interaction):
    """A ``devkit.finish_guard`` extension refused to integrate the branch, ``finish --merge`` (``INTERACTION``).

    Each reason is a detail (for example an unresolved problem envelope); nothing changed.
    """

    code = "WORKTREE_BLOCKED"
    fix = "Resolve what each detail names on the branch, commit it, then rerun"


class GuardFailedError(WorktreeError):
    """A ``devkit.finish_guard`` extension raised or returned something other than a list of strings
    (``MAINTENANCE``); ``finish --merge`` is refused, since the branch was not verified. Nothing changed."""

    code = "WORKTREE_GUARD_FAILED"
    fix = "Repair or uninstall the package that registers the failing extension, then rerun"


class NotFoundError(_Interaction):
    """No worktree has the branch or its path (``INTERACTION``).

    For ``finish``, also when the merged branch lacks the marker ``start`` records (or a finish already
    completed for it): nothing runs, merges, pushes or is deleted for that branch, and with ``delete_branch`` the
    ``[FIX]`` deletes it only once the user agrees.
    """

    code = "WORKTREE_NOT_FOUND"
    fix = "Check `devkit worktree status` or `git worktree list` for the branch"


class LockedError(_Interaction):
    """``finish`` found the branch's worktree locked (``git worktree lock``, ``INTERACTION``); nothing changed."""

    code = "WORKTREE_LOCKED"
    fix = "Unlock the worktree (git worktree unlock <path>) once the user agrees, then rerun"


class BaseDetachedError(_Interaction):
    """``finish --merge`` found the base checkout on a detached HEAD (``INTERACTION``); nothing changed.

    A fast-forward would move no branch and the push would be skipped, leaving the task's commits on no branch
    once the branch is deleted.
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
    """The branch has an upstream that lacks its commits, so ``git branch -d`` would refuse it (``INTERACTION``).

    Raised before any change; the ``[FIX]`` pushes the branch to that upstream.
    """

    code = "WORKTREE_BRANCH_UNPUSHED"
    fix = "Push the branch to its upstream, then rerun"


class BaseDirtyError(_Interaction):
    """``finish --merge`` found uncommitted changes in the base checkout (``INTERACTION``)."""

    code = "WORKTREE_BASE_DIRTY"
    fix = "Commit or stash the base checkout's changes, then rerun"


_MERGE_TARGET_FIX = (
    "Merge the target branch into the task branch in its worktree (git merge with a message the commit-msg gate"
    " accepts; never rebase, which rewrites the SHAs the task's records cite), re-verify, then rerun or prepare again"
)


class MergeNotFastForwardError(_Interaction):
    """The base moved on since the branch was created and the merge may not absorb it (``INTERACTION``).

    ``finish --merge`` lands only a branch that contains the base HEAD; the integration service absorbs later target
    commits only under ``merge = "no-ff"`` and only after its approval.
    """

    code = "WORKTREE_MERGE_NOT_FF"
    fix = _MERGE_TARGET_FIX


class MergeConflictError(_Interaction):
    """Merging the advanced target with the task branch conflicts (``INTERACTION``); nothing changed on the target."""

    code = "WORKTREE_MERGE_CONFLICT"
    fix = _MERGE_TARGET_FIX


class GitUnsupportedError(_Interaction):
    """Building a merge onto an advanced target needs ``git merge-tree --write-tree`` (Git 2.38 or later)."""

    code = "WORKTREE_GIT_UNSUPPORTED"
    fix = "Install Git 2.38 or later, or merge the target into the task branch in its worktree and prepare again"


class CommitFailedError(_Interaction):
    """The merge commit could not be created (identity, signing, timeout); nothing changed on the target."""

    code = "WORKTREE_COMMIT_FAILED"
    fix = (
        "Configure user.name and user.email (and a working, non-interactive signing setup when commit.gpgSign is on)"
        " for the repository, then rerun or prepare again"
    )


class MergeFailedError(WorktreeError):
    """An otherwise eligible local merge failed; inspect state before retrying the approved operation."""

    code = "WORKTREE_MERGE_FAILED"
    fix = "Inspect Git state and the reported failure, restore host access to the base/common Git directory, then resume only the remaining approved scope"


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
    """``git branch -d`` refused the branch after the worktree was removed (``INTERACTION``).

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


class BranchAheadNotice(WorktreeError):
    """``--existing-branch``: the local branch has commits its remote-tracking ref lacks (``NOTICE``); it is attached
    as it is, and the remote is synchronized only by a push."""

    code = "WORKTREE_BRANCH_AHEAD"
    level = Level.NOTICE


class RemoteUncheckedWarning(WorktreeError):
    """``start`` could not ask a remote whether it has the branch (unreachable, timed out; ``WARNING``).

    The remote-tracking refs fetched before stood in for it; the branch was created when none of them had it.
    """

    code = "WORKTREE_REMOTE_UNCHECKED"
    level = Level.WARNING


class StaleBranchWarning(WorktreeError):
    """An activity branch has had no commit and no pull request activity for ``[worktree] stale_after``
    (``WARNING``); the ``[FIX]`` names how to resume it, and how to discard it once the user decides."""

    code = "WORKTREE_STALE_BRANCH"
    level = Level.WARNING


class StaleSkippedNotice(WorktreeError):
    """The stale-branch check did not run: ``gh auth status`` failed or ``gh`` is missing (``NOTICE``)."""

    code = "WORKTREE_STALE_SKIPPED"
    level = Level.NOTICE


class StalePullRequestsUnknownNotice(WorktreeError):
    """``gh pr list`` failed, so stale branches were judged by their last commit alone (``NOTICE``)."""

    code = "WORKTREE_STALE_PR_UNKNOWN"
    level = Level.NOTICE


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


class LocalCopyError(WorktreeError):
    """The checkout exists, but its initial preference copy failed before setup."""

    code = "WORKTREE_LOCAL_CONFIG_COPY_FAILED"
