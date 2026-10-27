"""Immutable local finish scope and identity checks, shared by approval services and library callers."""

from __future__ import annotations

from pathlib import Path

from devkit_core.core.git import run_git_text

from devkit_agt.features.worktree.models.errors import (
    BaseDetachedError,
    BaseDirtyError,
    BranchUnpushedError,
    ConflictError,
    DirtyError,
    MergeNotFastForwardError,
    NotFoundError,
    PullRequestPolicyError,
    RunFromBaseError,
    from_base_error,
    pull_request_policy_fix,
)
from devkit_agt.features.worktree.models.lifecycle import Position
from devkit_agt.features.worktree.models.planning import FinishPlan as FinishPlan
from devkit_agt.features.worktree.services.merging import check_identity
from devkit_agt.features.worktree.usecases.lifecycle import (
    BASE_KEY,
    MARKER,
    UNIT_KEY,
    _check_deletable,
    _clean,
    _config,
    _created,
    _find,
    _marked_path,
    _marker,
    _merged,
    _query,
    check_branch,
    locate,
)


def _identity(path: Path) -> tuple[int, int]:
    if path.is_symlink():
        raise ConflictError("finish target is a symbolic link", target_files=[str(path)])
    try:
        info = path.stat()
    except OSError as exc:
        raise ConflictError("finish target cannot be identified", target_files=[str(path)]) from exc
    return info.st_dev, info.st_ino


def _markers(base: Path, branch: str) -> tuple[str, str, str]:
    return tuple(_config(base, _marker(branch, key)) for key in (MARKER, BASE_KEY, UNIT_KEY))  # type: ignore[return-value]


def _deletable(base: Path, branch: str, into: str | None) -> None:
    try:
        _check_deletable(base, branch, into)
    except BranchUnpushedError as exc:
        exc.fix = "Keep the branch by setting worktree.delete_branch = false and prepare a new request; resolve upstream synchronization separately under its own authority"
        raise


def plan_finish(
    position: Position,
    branch: str,
    *,
    pull_request: str = "auto",
    delete_branch: bool = True,
    merge_method: str = "no-ff",
    target_sha: str | None = None,
) -> FinishPlan:
    """Preflight local integration and exact cleanup without fetching, pushing or changing Git state.

    The source must contain the target (only later target advances are merged in), or the target must already
    contain the source, which plans a cleanup-only finish (``already_merged``); any other pair is
    ``WORKTREE_MERGE_NOT_FF``. Under ``merge_method="no-ff"`` a plan that builds a merge commit refuses without a
    committer identity (``WORKTREE_COMMIT_FAILED``).
    """
    check_branch(branch)
    if position.linked:
        raise from_base_error(
            RunFromBaseError,
            "prepare integration from the retained base checkout",
            position.base,
            position.root,
        )
    if pull_request == "required":
        raise PullRequestPolicyError(
            "required PR policy prevents local integration", fix=pull_request_policy_fix(branch)
        )
    if position.branch is None:
        raise BaseDetachedError("local integration requires the base checkout on its target branch")
    if not _clean(position.base):
        raise BaseDirtyError("the base checkout has uncommitted changes", target_files=[str(position.base)])
    entry = _find(position, branch)
    if entry is None and not _created(position.base, branch):
        raise NotFoundError("local integration requires a linked worktree or a devkit-marked task branch")
    markers = _markers(position.base, branch)
    if entry is None and markers[1] and markers[1] != position.branch:
        raise ConflictError("the base branch differs from the task's recorded base")
    path = entry.path if entry else _marked_path(position, branch)
    if entry and not _clean(path):
        raise DirtyError("the task worktree has uncommitted or untracked changes", target_files=[str(path)])
    source = run_git_text(position.base, "rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}")
    target = target_sha or run_git_text(position.base, "rev-parse", "--verify", "HEAD^{commit}")
    already = _merged(position.base, source, target)
    if not already and not _merged(position.base, target, source):
        raise MergeNotFastForwardError(
            f"{branch} neither contains the target {position.branch} at {target[:12]} nor is contained in it"
        )
    if merge_method == "no-ff" and not already:
        check_identity(position.base)
    if delete_branch:
        _deletable(position.base, branch, position.branch)
    common = position.base / ".git"
    return FinishPlan(
        str(position.base),
        str(common),
        _identity(common),
        branch,
        source,
        position.branch,
        target,
        str(path),
        _identity(path) if entry else None,
        run_git_text(position.base, "for-each-ref", "--format=%(upstream)", f"refs/heads/{branch}"),
        markers,
        delete_branch,
        merge_method,
        already,
    )


def validate_finish(
    plan: FinishPlan,
    *,
    merged: bool = False,
    removed: bool = False,
    finalized: bool = False,
    result: str | None = None,
    target: str | None = None,
    check_upstream: bool = True,
) -> None:
    """Recheck identities immediately before a mutation; allow only the executor's own completed transitions.

    Before the merge the base must point at ``target`` (default: the plan's target); after it, the base must contain
    ``result`` (default: the source), so later commits on the base are allowed.
    """
    base = Path(plan.base)
    position = locate(base)
    if str(position.base) != plan.base or position.linked or str(base / ".git") != plan.common_dir:
        raise ConflictError("repository identity changed; prepare a new integration request")
    if _identity(Path(plan.common_dir)) != plan.common_identity or position.branch != plan.target_branch:
        raise ConflictError("Git common directory or target branch changed; prepare a new request")
    head = run_git_text(base, "rev-parse", "--verify", "HEAD^{commit}")
    if merged:
        if not _merged(base, result or plan.source_sha, head):
            raise ConflictError(
                "the target no longer contains the integrated result; inspect Git state and prepare a new request"
            )
    elif head != (target or plan.target_sha):
        raise ConflictError(
            "target SHA changed outside the approved transition; inspect Git state and prepare a new request"
        )
    if not _clean(base):
        raise BaseDirtyError("the base checkout changed during integration", target_files=[plan.base])
    if finalized:
        source = _query(base, "rev-parse", "--verify", "--quiet", f"refs/heads/{plan.branch}^{{commit}}")
        if (plan.delete_branch and source is not None) or (not plan.delete_branch and source != plan.source_sha):
            raise ConflictError(
                "finalized source branch changed or was recreated; preserve it and prepare a new request"
            )
        if plan.worktree_identity is not None and (
            _find(position, plan.branch) is not None or Path(plan.path).exists()
        ):
            raise ConflictError("a finalized worktree target reappeared; preserve it and prepare a new request")
        return
    if run_git_text(base, "rev-parse", "--verify", f"refs/heads/{plan.branch}^{{commit}}") != plan.source_sha:
        raise ConflictError("source SHA changed; prepare a new request")
    if _markers(base, plan.branch) != plan.markers:
        raise ConflictError("task branch markers changed; prepare a new request")
    if run_git_text(base, "for-each-ref", "--format=%(upstream)", f"refs/heads/{plan.branch}") != plan.source_upstream:
        raise ConflictError("source upstream changed; prepare a new request")
    entry = _find(position, plan.branch)
    if plan.worktree_identity is not None:
        if removed:
            if entry is not None or Path(plan.path).exists() or Path(plan.path).is_symlink():
                raise ConflictError("a removed worktree target was recreated; preserve it and prepare a new request")
        elif entry is None or str(entry.path) != plan.path or _identity(entry.path) != plan.worktree_identity:
            raise ConflictError("worktree identity changed; prepare a new request")
        elif not _clean(entry.path):
            raise DirtyError(
                "the approved worktree is dirty; preserve it and inspect its changes", target_files=[plan.path]
            )
    elif entry is not None:
        raise ConflictError("a worktree appeared outside the approved cleanup scope")
    if plan.delete_branch and check_upstream:
        _deletable(base, plan.branch, plan.target_branch)
