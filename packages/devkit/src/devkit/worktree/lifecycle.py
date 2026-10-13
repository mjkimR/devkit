"""The task worktree lifecycle: locate the checkout, start a slug's worktree, finish it, report leftovers.

A slug's worktree is always ``<parent of base>/<base name>-wt-<slug>`` on the
branch ``<slug>``, created from the base checkout's HEAD; the base working tree
is never touched by ``start``. ``finish`` runs in the base: it fast-forwards the
base onto the branch and pushes it (``merge=True``) or verifies the branch is
merged, removes the worktree and deletes the branch. Every step refuses
instead of forcing, and rerunning resumes. ``status`` changes nothing.
"""

from __future__ import annotations

import dataclasses
import logging
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit.core.errors import ArgumentError, GitError
from devkit.core.git import run_git
from devkit.core.project import require_git_toplevel
from devkit.core.receipt import RECEIPT_PATH
from devkit.worktree.errors import (
    BaseDirtyError,
    BranchExistsError,
    ConflictError,
    DirtyError,
    MergeNotFastForwardError,
    NestedError,
    NotFoundError,
    PullRequestPolicyError,
    PushFailedWarning,
    RunFromBaseError,
    SetupFailedWarning,
    SyncFailedWarning,
    UnmergedError,
    UnsupportedLayoutError,
    WorktreeError,
)

_log = logging.getLogger(__name__)

SLUG = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}")
PUSH_TIMEOUT = 120.0  # seconds; a slow or stuck push must not hold the cleanup
SETUP_TIMEOUT = 900.0  # seconds for the `setup` command (dependency installs)
SYNC_TIMEOUT = 300.0  # seconds for `devkit sync` in a new worktree


@dataclass(frozen=True)
class Position:
    """The checkout a command runs in."""

    root: Path  # top level of this checkout
    base: Path  # top level of the base checkout (whose Git directory is the common one)
    branch: str | None  # this checkout's branch; None when detached
    linked: bool  # True inside a linked worktree


@dataclass(frozen=True)
class StartResult:
    slug: str
    path: Path
    branch: str
    base: Path
    created: bool  # False when the existing worktree was reused
    setup: str | None = None  # the setup command that ran, if any
    synced: bool | None = None  # whether `devkit sync` restored the project; None when it did not run
    notices: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "path": str(self.path),
            "branch": self.branch,
            "base": str(self.base),
            "created": self.created,
            "setup": self.setup,
            "synced": self.synced,
            "notices": [notice.to_dict() for notice in self.notices],
        }


@dataclass
class FinishResult:
    """How far ``finish`` got; ``push`` is ``pushed``, ``failed`` or ``no-upstream``, ``None`` without a merge."""

    slug: str
    path: Path
    branch: str
    merged: bool = False
    push: str | None = None
    removed: bool = False
    branch_deleted: bool = False
    notices: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        value = dataclasses.asdict(self) | {"path": str(self.path)}
        value["notices"] = [notice.to_dict() for notice in self.notices]
        return value


@dataclass(frozen=True)
class WorktreeStatus:
    path: Path
    branch: str | None  # None when detached
    head: str | None  # short commit id; None before the first commit
    role: str  # base | linked
    merged: bool | None  # into the base HEAD; None for the base itself
    dirty: bool | None  # None when the directory is missing or unreadable
    prunable: bool  # Git reports the worktree directory missing

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self) | {"path": str(self.path)}


@dataclass(frozen=True)
class BranchStatus:
    """A local branch that no worktree checks out and the base HEAD does not contain."""

    name: str
    head: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass(frozen=True)
class StatusResult:
    base: Path
    base_branch: str | None
    worktrees: list[WorktreeStatus]
    branches: list[BranchStatus]

    def to_dict(self) -> dict[str, Any]:
        return {
            "base": str(self.base),
            "base_branch": self.base_branch,
            "worktrees": [item.to_dict() for item in self.worktrees],
            "branches": [item.to_dict() for item in self.branches],
        }


@dataclass
class _Entry:
    path: Path
    branch: str | None = None
    head: str | None = None
    prunable: bool = False


def _git(cwd: Path, *args: str) -> str:
    return os.fsdecode(run_git(cwd, *args)).strip()


def _query(cwd: Path, *args: str) -> str | None:
    """The output of a Git query, or ``None`` when it answers no (exit 1); any other failure raises."""
    try:
        return _git(cwd, *args)
    except GitError as exc:
        if exc.returncode == 1:
            return None
        raise


def _succeeds(cwd: Path, *args: str) -> bool:
    return _query(cwd, *args) is not None


def _resolve(path: str) -> Path:
    return Path(path).resolve()


def check_slug(slug: str) -> str:
    """``slug`` when it is a valid task slug (lowercase letters, digits, ``-`` and ``_``; 64 at most)."""
    if not SLUG.fullmatch(slug):
        raise ArgumentError(
            f"slug {slug!r}: expected lowercase letters, digits, '-' and '_', starting with a letter or digit"
            " (64 characters at most)",
            target_files=["SLUG"],
        )
    return slug


def locate(start: Path) -> Position:
    """The checkout containing ``start``: its top level, the base checkout, the branch, whether it is linked."""
    root = require_git_toplevel(start)
    git_dir = _resolve(_git(root, "rev-parse", "--path-format=absolute", "--git-dir"))
    common = _resolve(_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    branch = _query(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    # The base checkout is the one whose Git directory is the common directory.
    if common.name != ".git" or not (common.parent / ".git").is_dir():
        raise UnsupportedLayoutError(f"{root}: the common Git directory {common} is not the .git of a work tree")
    return Position(root=root, base=common.parent, branch=branch or None, linked=git_dir != common)


def path_for(position: Position, slug: str) -> Path:
    """``<parent of base>/<base name>-wt-<slug>``."""
    return position.base.parent / f"{position.base.name}-wt-{slug}"


def _entries(base: Path) -> list[_Entry]:
    records = os.fsdecode(run_git(base, "worktree", "list", "--porcelain", "-z")).split("\0")
    entries: list[_Entry] = []
    current: _Entry | None = None
    for line in records:
        if line.startswith("worktree "):
            current = _Entry(_resolve(line.removeprefix("worktree ")))
            entries.append(current)
        elif current is None:
            continue
        elif line.startswith("branch "):
            current.branch = line.removeprefix("branch ").removeprefix("refs/heads/")
        elif line.startswith("HEAD "):
            head = line.removeprefix("HEAD ")
            current.head = head if head.strip("0") else None  # Git prints a zero id before the first commit
        elif line == "prunable" or line.startswith("prunable "):
            current.prunable = True
    return entries


def _clean(checkout: Path) -> bool:
    return not _git(checkout, "status", "--porcelain", "--untracked-files=normal")


def start(position: Position, slug: str, *, setup: str | None = None, project: Path | None = None) -> StartResult:
    """Create the slug's worktree from the base HEAD, or reuse it when it is on the slug's branch and clean.

    A new worktree is a fresh checkout without the base's ignored files, so two steps follow its creation:

    1. ``setup`` runs in the worktree through ``/bin/sh -c`` (without the caller's ``VIRTUAL_ENV``), for the
       environment the project needs (``uv sync``);
    2. when ``project`` (a directory relative to the checkout's top level) is a synchronized devkit project,
       ``devkit sync`` runs there with the worktree's ``.venv`` interpreter, else this one, and restores the
       managed copies under ``.devkit/managed/`` that the commit gates, rules and context commands read.

    A failure of either is a warning (``WORKTREE_SETUP_FAILED``, ``WORKTREE_SYNC_FAILED``) whose ``[FIX]``
    reruns it; the worktree stays. A reused worktree runs neither.
    """
    check_slug(slug)
    if position.linked:
        raise NestedError(
            f"{position.root} is a linked worktree; task worktrees are created from the base checkout",
            target_files=[str(position.base)],
        )
    path, branch = path_for(position, slug), slug
    for entry in _entries(position.base):
        if entry.path == path:
            if entry.branch != branch:
                raise ConflictError(f"{path} is a worktree on {entry.branch or 'a detached HEAD'}, not {branch}")
            if not _clean(path):
                raise ConflictError(f"{path} has uncommitted changes")
            return StartResult(slug, path, branch, position.base, created=False)
        if entry.branch == branch:
            raise BranchExistsError(f"branch {branch} is checked out at {entry.path}")
    if path.exists() or path.is_symlink():
        raise ConflictError(f"{path} exists and is not a worktree of this repository")
    if _succeeds(position.base, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"):
        raise BranchExistsError(f"branch {branch} already exists")
    run_git(position.base, "worktree", "add", "-b", branch, str(path))
    _log.info("created worktree %s on %s", path, branch)
    notices: list[AdvisoryError] = []
    if setup is not None:
        failure = _run(["/bin/sh", "-c", setup], path, f"setup {setup!r}", SETUP_TIMEOUT)
        if failure is not None:
            notices.append(SetupFailedWarning(failure, fix=f"cd {shlex.quote(str(path))} && {setup}"))
    synced = None
    target = path / project if project is not None else None
    if target is not None and (target / RECEIPT_PATH).is_file():
        python = path / ".venv/bin/python"
        interpreter = str(python) if python.is_file() else sys.executable
        failure = _run([interpreter, "-m", "devkit", "sync", "-w", str(target)], target, "devkit sync", SYNC_TIMEOUT)
        synced = failure is None
        if failure is not None:
            fix = f"cd {shlex.quote(str(target))} && {shlex.quote(interpreter)} -m devkit sync"
            notices.append(SyncFailedWarning(failure, fix=fix))
    return StartResult(slug, path, branch, position.base, True, setup, synced, notices)


def _run(argv: list[str], cwd: Path, label: str, timeout: float) -> str | None:
    """Run ``argv`` in ``cwd`` with its output captured; ``None`` on success, else why it failed (its last lines)."""
    env = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
    try:
        completed = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return f"{label} did not finish within {timeout:.0f}s"
    except OSError as exc:
        return f"{label} could not start: {exc}"
    if completed.returncode == 0:
        return None
    tail = os.fsdecode(completed.stderr or completed.stdout).strip().splitlines()[-5:]
    return f"{label} exited {completed.returncode}" + (":\n" + "\n".join(tail) if tail else "")


def find(position: Position, slug: str) -> Path:
    """The path of the slug's worktree (by its path or its branch); ``WORKTREE_NOT_FOUND`` when there is none."""
    path = path_for(position, slug)
    for entry in _entries(position.base):
        if entry.path == path or entry.branch == slug:
            return entry.path
    raise NotFoundError(f"no worktree at {path} or on branch {slug}")


def finish(
    position: Position,
    slug: str,
    *,
    merge: bool = False,
    pull_request: bool = True,
    delete_branch: bool = True,
    before_remove: Callable[[FinishResult], None] | None = None,
) -> FinishResult:
    """Integrate the slug's branch into the base, then remove its worktree and branch.

    ``merge`` fast-forwards the base onto the branch (it must be clean) and pushes the base branch to its
    configured upstream; a failed push is a ``WORKTREE_PUSH_FAILED`` warning and does not stop the cleanup.
    Without ``merge`` the branch must already be merged into the base HEAD. ``before_remove`` runs once the
    merge is confirmed and before the worktree is removed (a caller's own cleanup). A refusal after the merge
    carries the partial result as ``error.result``.
    """
    check_slug(slug)
    if position.linked:
        raise RunFromBaseError(
            f"{position.root} is the worktree finish would remove", target_files=[str(position.base)]
        )
    if merge and pull_request:
        raise PullRequestPolicyError(
            "[worktree] pull_request = true integrates through a pull request; --merge would merge locally"
        )
    base = position.base
    result = FinishResult(slug, find(position, slug), slug)
    if merge:
        if not _clean(base):
            raise BaseDirtyError(f"{base} has uncommitted changes", target_files=[str(base)])
        try:
            run_git(base, "merge", "--ff-only", "--quiet", result.branch)
        except GitError as exc:
            if exc.returncode is None:
                raise
            raise MergeNotFastForwardError(
                f"{result.branch} cannot be fast-forwarded onto the base: {exc.stderr}"
            ) from exc
        result.merged = True
        _push(position, result)
    elif not _succeeds(base, "merge-base", "--is-ancestor", f"refs/heads/{result.branch}", "HEAD"):
        raise UnmergedError(f"{result.branch} is not merged into the base HEAD; nothing was changed")
    try:
        if before_remove is not None:
            before_remove(result)
        try:
            run_git(base, "worktree", "remove", str(result.path))
        except GitError as exc:
            if "modified or untracked" in exc.stderr or "--force" in exc.stderr:
                raise DirtyError(f"{result.path} has uncommitted changes: {exc.stderr}") from exc
            raise
        result.removed = True
        if delete_branch:
            run_git(base, "branch", "-d", result.branch)
            result.branch_deleted = True
    except WorktreeError as error:
        error.result = result
        raise
    return result


def _push(position: Position, result: FinishResult) -> None:
    """Push the base branch to its configured upstream with an explicit refspec; never prompts, never forces."""
    result.push = "no-upstream"
    if position.branch is None:
        return
    remote = _config(position.base, f"branch.{position.branch}.remote")
    merge_ref = _config(position.base, f"branch.{position.branch}.merge")
    if not remote or remote == "." or not merge_ref:
        return
    refspec = f"refs/heads/{position.branch}:{merge_ref}"
    try:
        run_git(position.base, "push", "--quiet", remote, refspec, timeout=PUSH_TIMEOUT)
    except GitError as exc:
        result.push = "failed"
        result.notices.append(
            PushFailedWarning(
                f"the base was merged and the worktree is being cleaned up, but the push to {remote} failed: "
                f"{exc.stderr or exc.message}",
                fix=f"git -C {shlex.quote(str(position.base))} push {remote} {refspec}",
            )
        )
        return
    result.push = "pushed"


def _config(base: Path, key: str) -> str:
    return _query(base, "config", "--get", key) or ""


def status(position: Position) -> StatusResult:
    """Every worktree with its merge and dirty state, and the unmerged branches no worktree checks out."""
    base = position.base
    entries = _entries(base)
    base_branch = _query(base, "symbolic-ref", "--quiet", "--short", "HEAD")
    base_head = _query(base, "rev-parse", "--verify", "--quiet", "HEAD")

    def merged(rev: str | None) -> bool:
        return (
            rev is not None and base_head is not None and _succeeds(base, "merge-base", "--is-ancestor", rev, base_head)
        )

    worktrees: list[WorktreeStatus] = []
    for entry in entries:
        is_base = entry.path == base
        dirty: bool | None = None
        if not entry.prunable and entry.path.is_dir():
            try:
                dirty = not _clean(entry.path)
            except GitError:
                dirty = None
        worktrees.append(
            WorktreeStatus(
                path=entry.path,
                branch=entry.branch,
                head=entry.head[:7] if entry.head else None,
                role="base" if is_base else "linked",
                merged=None if is_base else merged(f"refs/heads/{entry.branch}" if entry.branch else entry.head),
                dirty=dirty,
                prunable=entry.prunable,
            )
        )
    checked_out = {entry.branch for entry in entries if entry.branch}
    branches = []
    refs = _git(base, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads/")
    for line in refs.splitlines():
        name, _, head = line.partition(" ")
        if name and name not in checked_out and not merged(head):
            branches.append(BranchStatus(name, head[:7]))
    branches.sort(key=lambda item: item.name)
    return StatusResult(base, base_branch, worktrees, branches)
