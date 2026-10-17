"""Immutable local finish scope and identity checks, shared by approval services and library callers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from devkit.worktree.errors import (
    BaseDetachedError,
    BaseDirtyError,
    BranchUnpushedError,
    ConflictError,
    DirtyError,
    MergeNotFastForwardError,
    NotFoundError,
    PullRequestPolicyError,
    RunFromBaseError,
)
from devkit.worktree.lifecycle import (
    BASE_KEY,
    MARKER,
    UNIT_KEY,
    Position,
    _check_deletable,
    _clean,
    _config,
    _created,
    _find,
    _git,
    _marked_path,
    _marker,
    _merged,
    _query,
    check_branch,
    locate,
)


@dataclass(frozen=True)
class FinishPlan:
    base: str
    common_dir: str
    common_identity: tuple[int, int]
    branch: str
    source_sha: str
    target_branch: str
    target_sha: str
    path: str
    worktree_identity: tuple[int, int] | None
    source_upstream: str
    markers: tuple[str, str, str]
    delete_branch: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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


def _deletable(base: Path, branch: str) -> None:
    try:
        _check_deletable(base, branch)
    except BranchUnpushedError as exc:
        exc.fix = "Keep the branch by setting worktree.delete_branch = false and prepare a new request; resolve upstream synchronization separately under its own authority"
        raise


def plan_finish(
    position: Position, branch: str, *, pull_request: str = "auto", delete_branch: bool = True
) -> FinishPlan:
    """Preflight local FF integration and exact cleanup without fetching, pushing or changing Git state."""
    check_branch(branch)
    if position.linked:
        raise RunFromBaseError("prepare integration from the retained base checkout")
    if pull_request == "required":
        raise PullRequestPolicyError("required PR policy prevents local integration")
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
    source = _git(position.base, "rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}")
    target = _git(position.base, "rev-parse", "--verify", "HEAD^{commit}")
    if not _merged(position.base, target, source):
        raise MergeNotFastForwardError("integrate the base into the task branch and reverify before preparing approval")
    if delete_branch:
        _deletable(position.base, branch)
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
        _git(position.base, "for-each-ref", "--format=%(upstream)", f"refs/heads/{branch}"),
        markers,
        delete_branch,
    )


def validate_finish(plan: FinishPlan, *, merged: bool = False, removed: bool = False, finalized: bool = False) -> None:
    """Recheck identities immediately before a mutation; allow only the executor's own completed transitions."""
    base = Path(plan.base)
    position = locate(base)
    if str(position.base) != plan.base or position.linked or str(base / ".git") != plan.common_dir:
        raise ConflictError("repository identity changed; prepare a new integration request")
    if _identity(Path(plan.common_dir)) != plan.common_identity or position.branch != plan.target_branch:
        raise ConflictError("Git common directory or target branch changed; prepare a new request")
    expected = plan.source_sha if merged else plan.target_sha
    if _git(base, "rev-parse", "--verify", "HEAD^{commit}") != expected:
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
    if _git(base, "rev-parse", "--verify", f"refs/heads/{plan.branch}^{{commit}}") != plan.source_sha:
        raise ConflictError("source SHA changed; prepare a new request")
    if _markers(base, plan.branch) != plan.markers:
        raise ConflictError("task branch markers changed; prepare a new request")
    if _git(base, "for-each-ref", "--format=%(upstream)", f"refs/heads/{plan.branch}") != plan.source_upstream:
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
    if plan.delete_branch:
        _deletable(base, plan.branch)
