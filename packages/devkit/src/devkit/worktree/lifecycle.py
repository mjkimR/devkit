"""The task worktree lifecycle: locate the checkout, start an activity branch, finish it, report leftovers.

A task runs on an activity branch ``<activity>-<slug>`` (``plan-<slug>`` or ``dev-<slug>``, ``check_branch``). Its
worktree is always ``<parent of base>/<base name>-wt-<branch>``, created from the base checkout's HEAD; the base
working tree is never touched by ``start``. ``start_branch`` creates the branch without a worktree and switches the
current checkout to it; ``attach`` gives an existing branch its worktree. Every branch these create or attach carries
the marker ``branch.<branch>.devkitWorktree`` (the worktree or checkout path) in the common Git configuration, with
``devkitBase`` (the branch ``start_branch`` started from) and ``devkitUnit`` (the unit ``attach`` was given) beside
it; ``git branch -d`` removes them with the branch, and a ``finish`` that keeps the branch unsets the marker.
``finish`` runs in the base: it fast-forwards the base onto the branch and pushes it (``merge=True``) or verifies the
branch is merged, removes the worktree and deletes the branch. Every step refuses instead of forcing, the checks of
the worktree's branch, the base and the upstreams run before the first change, and rerunning resumes. ``status``
changes nothing.
"""

from __future__ import annotations

import contextlib
import dataclasses
import json
import os
import re
import shlex
import signal
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit.core.errors import ArgumentError, GitError
from devkit.core.git import run_git
from devkit.core.local_config import LOCAL_CONFIG_PATH, read_local_config
from devkit.core.logs import get_logger
from devkit.core.project import require_git_toplevel
from devkit.core.receipt import RECEIPT_PATH
from devkit.worktree.errors import (
    AddFailedError,
    BaseBehindError,
    BaseDetachedError,
    BaseDirtyError,
    BaseOnBranchError,
    BranchAheadNotice,
    BranchDeleteFailedError,
    BranchExistsError,
    BranchOutOfSyncError,
    BranchUnpushedError,
    ConflictError,
    DirtyError,
    LockedError,
    MergeFailedError,
    MergeNotFastForwardError,
    NestedError,
    NotFoundError,
    PullRequestPolicyError,
    PushFailedWarning,
    PushRejectedWarning,
    RemoteUncheckedWarning,
    RemoveFailedError,
    RunFromBaseError,
    SetupFailedWarning,
    SyncFailedWarning,
    UnitInvalidError,
    UnmergedError,
    UnsupportedLayoutError,
    WorktreeError,
)
from devkit.worktree.merging import build_result, check_identity, merge_message

_log = get_logger(__name__)

ACTIVITY_PREFIXES = ("plan", "dev")  # Planning and Development activity branches: plan-<slug>, dev-<slug>
BRANCH = re.compile(rf"(?:{'|'.join(ACTIVITY_PREFIXES)})-[a-z0-9][a-z0-9_-]*")
BRANCH_LIMIT = 64  # characters of the whole branch name, prefix included
# Recorded in the common configuration on every branch ``start`` creates or attaches; only a marked branch is deleted
# without its worktree, so ``finish`` never deletes an ordinary branch that happens to share the name.
MARKER = "devkitWorktree"
BASE_KEY = "devkitBase"  # the branch ``start_branch`` started from, where the base checkout returns to
UNIT_KEY = "devkitUnit"  # the unit directory ``attach`` was given, for the stale-branch report
LS_REMOTE_TIMEOUT = 30.0  # seconds to ask one remote whether it has the branch
PUSH_TIMEOUT = 120.0  # seconds; a slow or stuck push must not hold the cleanup
FETCH_TIMEOUT = 120.0  # seconds for the upstream fetch before the merge
SETUP_TIMEOUT = 900.0  # seconds for the `setup` command (dependency installs)
SYNC_TIMEOUT = 300.0  # seconds for `devkit sync --locked` in a new worktree
CHECKOUT_TIMEOUT = 1800.0  # seconds for `git worktree add` and `remove`: a large checkout (LFS, slow hooks) takes long


@dataclass(frozen=True)
class Position:
    """The checkout a command runs in."""

    root: Path  # top level of this checkout
    base: Path  # top level of the base checkout (whose Git directory is the common one)
    branch: str | None  # this checkout's branch; None when detached
    linked: bool  # True inside a linked worktree


@dataclass(frozen=True)
class StartResult:
    branch: str
    path: Path
    base: Path
    created: bool  # False when the existing worktree was reused
    setup: str | None = None  # the setup command that ran, if any
    synced: bool | None = None  # whether `devkit sync --locked` restored the project; None when it did not run
    notices: list[AdvisoryError] = field(default_factory=list)
    existing: bool = False  # the branch existed before (`attach`)
    unit: str | None = None  # the unit `attach` was given, relative to the devkit project

    @property
    def slug(self) -> str:
        return slug_of(self.branch)

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "slug": self.slug,
            "path": str(self.path),
            "base": str(self.base),
            "created": self.created,
            "existing": self.existing,
            "unit": self.unit,
            "setup": self.setup,
            "synced": self.synced,
            "notices": [notice.to_dict() for notice in self.notices],
        }


@dataclass(frozen=True)
class BranchStartResult:
    """``start_branch``: the branch was created at ``checkout``'s HEAD and ``checkout`` switched to it."""

    branch: str
    checkout: Path
    started_from: str  # the branch the checkout was on, recorded as ``devkitBase``
    notices: list[AdvisoryError] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return slug_of(self.branch)

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "slug": self.slug,
            "checkout": str(self.checkout),
            "from": self.started_from,
            "notices": [notice.to_dict() for notice in self.notices],
        }


@dataclass
class FinishResult:
    """How far ``finish`` got; ``push`` is ``pushed``, ``rejected``, ``failed`` or ``no-upstream``, ``None`` without
    a merge. ``removed`` is also ``True`` when there was no worktree to remove (a rerun after it was removed, or a
    branch ``start_branch`` created, whose ``path`` is the checkout it was started in). ``discarded`` is ``True`` for
    ``discard``: the branch was deleted unmerged."""

    branch: str
    path: Path
    merged: bool = False
    push: str | None = None
    removed: bool | None = False  # None: the branch never had a worktree (``start_branch``, made by hand)
    branch_deleted: bool = False
    discarded: bool = False
    notices: list[AdvisoryError] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return slug_of(self.branch)

    def to_dict(self) -> dict[str, Any]:
        value = {"branch": self.branch, "slug": self.slug} | dataclasses.asdict(self) | {"path": str(self.path)}
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
    locked: bool = False


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


def _head(base: Path) -> str | None:
    """The base HEAD's commit id; ``None`` before its first commit."""
    return _query(base, "rev-parse", "--verify", "--quiet", "HEAD")


def _merged(base: Path, rev: str | None, head: str | None) -> bool:
    """Whether the commit ``head`` (the base HEAD) contains ``rev``; ``status`` and ``finish`` share this test.

    A ``rev`` that names no commit (an unborn branch, made by ``git switch --orphan``) is not merged.
    """
    if rev is None or head is None:
        return False
    try:
        return _succeeds(base, "merge-base", "--is-ancestor", rev, head)
    except GitError:
        if _query(base, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}") is None:
            return False
        raise


def _resolve(path: str) -> Path:
    return Path(path).resolve()


def check_branch(branch: str) -> str:
    """``branch`` when it is an activity branch: ``plan-`` or ``dev-`` and a slug of lowercase letters, digits,
    ``-`` and ``_`` starting with a letter or digit, 64 characters at most in all."""
    if not BRANCH.fullmatch(branch) or len(branch) > BRANCH_LIMIT:
        raise ArgumentError(
            f"branch {branch!r}: expected an activity branch <activity>-<slug>, the activity one of"
            f" {', '.join(ACTIVITY_PREFIXES)} and the slug lowercase letters, digits, '-' and '_' starting with a"
            f" letter or digit ({BRANCH_LIMIT} characters at most in all)",
            target_files=["BRANCH"],
            fix="Pass plan-<slug> for a Planning activity or dev-<slug> for a Development activity",
        )
    return branch


def slug_of(branch: str) -> str:
    """The slug of an activity branch: its name without the activity prefix."""
    return branch.split("-", 1)[1] if "-" in branch else branch


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


def path_for(position: Position, branch: str) -> Path:
    """``<parent of base>/<base name>-wt-<branch>``."""
    return position.base.parent / f"{position.base.name}-wt-{branch}"


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
        elif line == "locked" or line.startswith("locked "):
            current.locked = True
    return entries


def _marker(branch: str, key: str = MARKER) -> str:
    """The configuration key marking ``branch`` as created by ``start`` (or another of its ``devkit*`` keys)."""
    return f"branch.{branch}.{key}"


def _created(base: Path, branch: str) -> bool:
    """Whether ``start`` created ``branch`` (it carries the marker in the common configuration)."""
    return _query(base, "config", "--local", "--get", _marker(branch)) is not None


def _unmark(base: Path, branch: str) -> None:
    """Remove ``branch``'s marker; a branch without one (Git exits 5) is left as it is."""
    try:
        run_git(base, "config", "--local", "--unset-all", _marker(branch))
    except GitError as exc:
        if exc.returncode != 5:
            raise


def _clean(checkout: Path) -> bool:
    return not _git(checkout, "status", "--porcelain", "--untracked-files=normal")


def _local_snapshot(base: Path, project: Path | None) -> tuple[Path, bytes, int] | None:
    source_root = base / (project or Path("."))
    read_local_config(source_root)
    source = source_root / LOCAL_CONFIG_PATH
    if not source.exists():
        return None
    return source, source.read_bytes(), source.stat().st_mode & 0o7777


def _copy_local_snapshot(path: Path, project: Path | None, captured: tuple[Path, bytes, int] | None) -> None:
    if captured is None:
        return
    from devkit.worktree.errors import LocalCopyError

    source, content, mode = captured
    destination = path / (project or Path(".")) / LOCAL_CONFIG_PATH
    try:
        if destination.exists() or destination.is_symlink():
            raise OSError("destination already exists; refusing to overwrite it")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(content)
        destination.chmod(mode)
    except OSError as exc:
        raise LocalCopyError(
            f"worktree created but local configuration copy failed: {source} -> {destination}: {exc}",
            target_files=[str(source), str(destination)],
            fix=f"Deliberately copy {shlex.quote(str(source))} to {shlex.quote(str(destination))}, then rerun setup and devkit sync --locked in {shlex.quote(str(path))}",
        ) from exc


def start(
    position: Position,
    branch: str,
    *,
    setup: str | None = None,
    project: Path | None = None,
    revision: str | None = None,
) -> StartResult:
    """Create the activity branch's worktree from the base HEAD.

    With ``revision``, resolve a commit before the remote checks and pass that exact commit to Git for creation:
    setup never executes a later ambient base HEAD. Without it, creation uses the base HEAD as before.

    A branch that already exists, locally or on a remote (``_remote_holders``), is refused
    (``WORKTREE_BRANCH_EXISTS``), also when its worktree is already registered: an existing branch is continued only
    through ``attach`` (``--existing-branch``), which checks it and reuses that worktree. A new worktree is a fresh
    checkout without the base's ignored files, so two steps follow its creation:

    1. ``setup`` runs in the worktree through ``/bin/sh -c`` (without the caller's ``VIRTUAL_ENV``), for the
       environment the project needs (``uv sync``);
    2. when ``project`` (a directory relative to the checkout's top level) is a synchronized devkit project,
       ``devkit sync --locked`` runs there with the worktree's ``.venv`` interpreter when devkit is installed in
       it, else this one, and restores the managed copies under ``.devkit/managed/`` that the commit gates, rules
       and context commands read, never changing the committed receipt, ``AGENTS.md`` or seeded files.

    A failure of either is a warning (``WORKTREE_SETUP_FAILED``, ``WORKTREE_SYNC_FAILED``) whose ``[FIX]``
    reruns it; the worktree stays. A failed ``git worktree add`` leaves nothing
    behind (``WORKTREE_ADD_FAILED``).
    """
    check_branch(branch)
    if position.linked:
        raise NestedError(
            f"{position.root} is a linked worktree; task worktrees are created from the base checkout",
            target_files=[str(position.base)],
        )
    if revision is not None:
        revision = _git(position.base, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}")
    path = path_for(position, branch)
    for entry in _entries(position.base):
        if entry.path == path:
            if entry.prunable:
                raise ConflictError(
                    f"{path} is a registered worktree whose directory is missing",
                    fix=f"git -C {shlex.quote(str(position.base))} worktree prune",
                )
            if entry.branch != branch:
                raise ConflictError(f"{path} is a worktree on {entry.branch or 'a detached HEAD'}, not {branch}")
            raise BranchExistsError(
                f"branch {branch} already has its worktree at {path}; a new start never continues an existing branch",
                fix=_attach_fix(branch),
            )
        if entry.branch == branch:
            raise BranchExistsError(f"branch {branch} is checked out at {entry.path}", fix=_attach_fix(branch))
    if path.exists() or path.is_symlink():
        raise ConflictError(f"{path} exists and is not a worktree of this repository")
    notices = _refuse_existing(position.base, branch)
    captured_local = _local_snapshot(position.base, project)
    _add(position.base, path, branch, revision=revision)
    _log.info("created worktree %s on %s", path, branch)
    _copy_local_snapshot(path, project, captured_local)
    setup_ran, synced = _prepare(path, setup, project, notices)
    return StartResult(branch, path, position.base, True, setup_ran, synced, notices)


def _prepare(
    path: Path, setup: str | None, project: Path | None, notices: list[AdvisoryError]
) -> tuple[str | None, bool | None]:
    """Run ``setup`` and ``devkit sync --locked`` in a new worktree; their warnings go to ``notices``.

    Returns the setup command that ran and whether the sync restored the project (``None`` when it did not run).
    """
    if setup is not None:
        failure = _run(["/bin/sh", "-c", setup], path, f"setup {setup!r}", SETUP_TIMEOUT)
        if failure is not None:
            notices.append(SetupFailedWarning(failure, fix=f"cd {shlex.quote(str(path))} && {setup}"))
    synced = None
    target = path / project if project is not None else None
    if target is not None and (target / RECEIPT_PATH).is_file():
        warning = _sync(_interpreter(path), target)
        synced = warning is None
        if warning is not None:
            notices.append(warning)
    return setup, synced


def _attach_fix(branch: str, source: str | None = None) -> str:
    return (
        f"To continue it, devkit worktree start {branch} --existing-branch {source or branch} --unit <unit directory>;"
        " otherwise choose another slug"
    )


def _refuse_existing(base: Path, branch: str) -> list[AdvisoryError]:
    """Refuse a new ``branch`` that exists locally or on a remote; the warnings of remotes that could not be asked."""
    if _succeeds(base, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"):
        raise BranchExistsError(f"branch {branch} already exists", fix=_attach_fix(branch))
    holders, notices = _remote_holders(base, branch)
    if holders:
        raise BranchExistsError(
            f"branch {branch} already exists on {', '.join(holders)}",
            fix=_attach_fix(branch, f"{holders[0]}/{branch}"),
        )
    return notices


def _remote_holders(base: Path, branch: str) -> tuple[list[str], list[AdvisoryError]]:
    """The remotes that have ``branch``, and a warning for each remote that could not be asked.

    Each configured remote is asked with ``git ls-remote --heads`` (no prompts, within ``LS_REMOTE_TIMEOUT``); one
    that cannot be reached is judged by its remote-tracking ref ``refs/remotes/<remote>/<branch>`` from the last
    fetch instead, and reported as ``WORKTREE_REMOTE_UNCHECKED``.
    """
    holders: list[str] = []
    notices: list[AdvisoryError] = []
    for remote in _git(base, "remote").splitlines():
        try:
            listed = os.fsdecode(
                run_git(base, "ls-remote", "--heads", remote, f"refs/heads/{branch}", timeout=LS_REMOTE_TIMEOUT)
            ).strip()
        except GitError as exc:
            tracked = _succeeds(base, "rev-parse", "--verify", "--quiet", f"refs/remotes/{remote}/{branch}")
            notices.append(
                RemoteUncheckedWarning(
                    f"could not ask {remote} whether it has {branch}: {exc.stderr or exc.message}; judged by"
                    f" refs/remotes/{remote}/{branch} from the last fetch ({'present' if tracked else 'absent'})",
                    fix=f"Once {remote} is reachable, git -C {shlex.quote(str(base))} ls-remote --heads {remote}"
                    f" {branch}; if it lists the branch, continue it with --existing-branch {remote}/{branch}",
                )
            )
            if tracked:
                holders.append(remote)
            continue
        if listed:
            holders.append(remote)
    return holders, notices


def start_branch(position: Position, branch: str) -> BranchStartResult:
    """Create the activity branch at the current HEAD and switch the current checkout to it, without a worktree.

    ``git switch -c`` carries uncommitted changes over to the branch. The same name rule and refusals as ``start``
    apply: a branch that exists locally or on a remote is ``WORKTREE_BRANCH_EXISTS``. The branch gets the marker
    (the checkout's path) and ``devkitBase``, the branch the checkout was on, so ``finish --merge`` can integrate it
    from the base once the checkout is back on that branch. It runs in the base checkout (``WORKTREE_NESTED`` in a
    linked worktree, which ``finish`` would remove) on a branch (``WORKTREE_BASE_DETACHED`` otherwise: nothing would
    say where the task integrates).
    """
    check_branch(branch)
    if position.linked:
        raise NestedError(
            f"{position.root} is a linked worktree; activity branches are started in the base checkout",
            target_files=[str(position.base)],
        )
    if position.branch is None:
        raise BaseDetachedError(
            f"{position.root} is on a detached HEAD; the branch would record no branch to integrate into",
            target_files=[str(position.root)],
        )
    for entry in _entries(position.base):
        if entry.branch == branch:
            raise BranchExistsError(f"branch {branch} is checked out at {entry.path}", fix=_attach_fix(branch))
    notices = _refuse_existing(position.base, branch)
    try:
        run_git(position.root, "switch", "--quiet", "-c", branch)
    except GitError as exc:
        if f"a branch named '{branch}' already exists" in exc.stderr:
            raise BranchExistsError(
                f"branch {branch} already exists: it was created while start ran; nothing was changed",
                fix=_attach_fix(branch),
            ) from exc
        raise
    run_git(position.base, "config", "--local", _marker(branch), str(position.root))
    run_git(position.base, "config", "--local", _marker(branch, BASE_KEY), position.branch)
    _log.info("switched %s to the new branch %s from %s", position.root, branch, position.branch)
    return BranchStartResult(branch, position.root, position.branch, notices)


def attach(
    position: Position,
    branch: str,
    *,
    source: str,
    unit: str,
    setup: str | None = None,
    project: Path | None = None,
    check: Callable[[Path, str, str, str], None] | None = None,
) -> StartResult:
    """Give the existing activity branch ``branch`` its worktree, to continue it at the stage its unit reached.

    ``source`` is ``branch`` or ``<remote>/<branch>``. The branch must exist locally or as a fetched
    remote-tracking ref (nothing is fetched); a remote-only branch gets a local branch tracking it. A local branch
    that lacks commits of its remote-tracking branch is ``WORKTREE_BRANCH_OUT_OF_SYNC`` (never merged or reset); one
    ahead of it is attached. ``unit`` (relative to ``project``, the devkit project directory in the checkout) must be
    a directory of the branch's tree (``WORKTREE_UNIT_INVALID``); ``check(root, branch, unit, tip)`` then verifies
    that branch and unit belong together (the ``devkit.attach_check`` extensions in the CLI). Nothing in the branch
    is reset or rewritten.

    A registered, clean worktree of the branch at its path is reused; one elsewhere, or a path occupied otherwise,
    is refused. When the base checkout is on the branch, it must be clean and is switched back to the branch
    recorded as ``devkitBase`` (``WORKTREE_CONFLICT`` when none is), then the worktree is created as by ``start``,
    with its setup and sync. The marker and ``devkitUnit`` are recorded.
    """
    check_branch(branch)
    if position.linked:
        raise NestedError(
            f"{position.root} is a linked worktree; task worktrees are created from the base checkout",
            target_files=[str(position.base)],
        )
    base = position.base
    remotes = _git(base, "remote").splitlines()
    remote = _source_remote(source, branch, remotes)
    unit_path = _unit_path(unit, project)
    local = _query(base, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}^{{commit}}")
    remote_ref, remote_tip = _remote_tracking(base, branch, remote, remotes, local is not None)
    if local is None and remote_tip is None:
        raise NotFoundError(
            f"branch {branch} exists neither locally nor as a fetched remote-tracking ref"
            + (f" refs/remotes/{remote}/{branch}" if remote else ""),
            fix=f"git -C {shlex.quote(str(base))} fetch {remote or '--all'}, then rerun; or start a new branch"
            f" without --existing-branch",
        )
    ahead = None
    if local is not None and remote_tip is not None and remote_ref is not None:
        ahead = _check_in_sync(position, branch, local, remote_ref)
    tip = local or remote_tip
    assert tip is not None
    if _object_type(base, f"{tip}:{unit_path}") != "tree":
        raise UnitInvalidError(f"{unit_path} is not a directory on {branch} ({tip[:7]})", target_files=[unit])
    if check is not None:
        check(base, branch, unit_path, tip)
    path = path_for(position, branch)
    reuse, back = False, None
    for entry in _entries(base):
        if entry.path == path:
            if entry.prunable:
                raise ConflictError(
                    f"{path} is a registered worktree whose directory is missing",
                    fix=f"git -C {shlex.quote(str(base))} worktree prune",
                )
            if entry.branch != branch:
                raise ConflictError(f"{path} is a worktree on {entry.branch or 'a detached HEAD'}, not {branch}")
            if not _clean(path):
                raise ConflictError(f"{path} has uncommitted changes")
            reuse = True
        elif entry.branch == branch and entry.path == base:
            back = _return_branch(base, branch)
        elif entry.branch == branch:
            raise BranchExistsError(
                f"branch {branch} is checked out at {entry.path}, not at {path}; nothing was changed",
                fix=f"Finish or remove the worktree at {entry.path} once the user agrees, then rerun",
            )
    if not reuse and (path.exists() or path.is_symlink()):
        raise ConflictError(f"{path} exists and is not a worktree of this repository")
    captured_local = _local_snapshot(base, project) if not reuse else None
    if back is not None:
        run_git(base, "switch", "--quiet", back)
        _log.info("switched the base checkout from %s back to %s", branch, back)
    if local is None:
        assert remote_ref is not None
        run_git(base, "branch", "--quiet", "--track", branch, remote_ref)
    notices: list[AdvisoryError] = [ahead] if ahead is not None else []
    setup_ran: str | None = None
    synced: bool | None = None
    if not reuse:
        _add(base, path, branch, existing=True)
        _log.info("attached worktree %s to the existing branch %s", path, branch)
        _copy_local_snapshot(path, project, captured_local)
        setup_ran, synced = _prepare(path, setup, project, notices)
    run_git(base, "config", "--local", _marker(branch), str(path))
    run_git(base, "config", "--local", _marker(branch, UNIT_KEY), unit)
    return StartResult(branch, path, base, not reuse, setup_ran, synced, notices, existing=True, unit=unit)


def _source_remote(source: str, branch: str, remotes: list[str]) -> str | None:
    """The remote ``--existing-branch`` names (``<remote>/<branch>``), ``None`` for ``<branch>``."""
    if source == branch:
        return None
    remote, _, name = source.rpartition("/")
    if name == branch and remote in remotes:
        return remote
    raise ArgumentError(
        f"--existing-branch {source!r} must be {branch} or <remote>/{branch} with a configured remote"
        f" ({', '.join(remotes) or 'none configured'})",
        target_files=["--existing-branch"],
        fix=f"Pass --existing-branch {branch}" + (f" or --existing-branch {remotes[0]}/{branch}" if remotes else ""),
    )


def _unit_path(unit: str, project: Path | None) -> str:
    """``unit`` (relative to the devkit project) as a path relative to the checkout's top level."""
    relative = Path(unit)
    if not unit or relative.is_absolute() or ".." in relative.parts or relative == Path("."):
        raise UnitInvalidError(
            f"--unit {unit!r} must be a directory relative to the devkit project, inside it", target_files=[unit]
        )
    return (project / relative if project is not None else relative).as_posix()


def _remote_tracking(
    base: Path, branch: str, remote: str | None, remotes: list[str], local: bool
) -> tuple[str | None, str | None]:
    """The remote-tracking ref (``refs/remotes/<remote>/<branch>``) the branch is compared with or created from, and
    its tip.

    The named remote (``WORKTREE_NOT_FOUND`` when a local branch exists but that remote's tracking ref was never
    fetched: comparing with nothing would attach a stale branch); else the local branch's upstream when it is a
    fetched remote-tracking ref; else the one remote whose tracking ref exists, also for a local branch without an
    upstream (``--no-worktree`` sets none), so a fetched copy that moved on is never skipped (``ARGUMENT_INVALID``
    when several do).
    """
    if remote is None and local:
        upstream = _git(base, "for-each-ref", "--format=%(upstream)", f"refs/heads/{branch}")
        if upstream.startswith("refs/remotes/"):
            tip = _query(base, "rev-parse", "--verify", "--quiet", f"{upstream}^{{commit}}")
            if tip:
                return upstream, tip
    candidates = [remote] if remote is not None else remotes
    found = [
        (ref, tip)
        for name in candidates
        if (
            tip := _query(
                base, "rev-parse", "--verify", "--quiet", f"{(ref := f'refs/remotes/{name}/{branch}')}^{{commit}}"
            )
        )
    ]
    if len(found) > 1:
        names = [ref.removeprefix("refs/remotes/") for ref, _ in found]
        raise ArgumentError(
            f"branch {branch} exists on several remotes ({', '.join(names)})",
            target_files=["--existing-branch"],
            fix=f"Pass --existing-branch {names[0]} (or another <remote>/{branch})",
        )
    if remote is not None and local and not found:
        raise NotFoundError(
            f"--existing-branch {remote}/{branch}: refs/remotes/{remote}/{branch} was never fetched, so the local"
            f" branch {branch} cannot be compared with it; nothing was changed",
            fix=f"git -C {shlex.quote(str(base))} fetch {shlex.quote(remote)}, then rerun",
        )
    return found[0] if found else (None, None)


def _check_in_sync(position: Position, branch: str, local: str, remote_ref: str) -> BranchAheadNotice | None:
    """Refuse a local branch that lacks commits of ``remote_ref``; one ahead of it passes with a notice that the
    remote still lacks its commits, an equal one silently."""
    base = position.base
    if _succeeds(base, "merge-base", "--is-ancestor", remote_ref, local):
        if _git(base, "rev-parse", f"{remote_ref}^{{commit}}") == local:
            return None
        name = remote_ref.removeprefix("refs/remotes/")
        remote, _, _ = name.partition("/")
        return BranchAheadNotice(
            f"the local branch {branch} has commits {name} lacks; it was attached as it is, and the remote is synchronized"
            " only by a push",
            fix=f"git -C {shlex.quote(str(base))} push {shlex.quote(remote)} {branch} when the work is to be shared",
        )
    behind = _succeeds(base, "merge-base", "--is-ancestor", local, remote_ref)
    name = remote_ref.removeprefix("refs/remotes/")
    holder = next((entry.path for entry in _entries(base) if entry.branch == branch), None)
    if behind and holder is None:
        fix = f"git -C {shlex.quote(str(base))} fetch . {remote_ref}:refs/heads/{branch}, then rerun"
    elif behind:
        fix = f"git -C {shlex.quote(str(holder))} merge --ff-only {name}, then rerun"
    else:
        fix = f"Reconcile {branch} with {name} (rebase or merge) with the user, then rerun"
    state = "is behind" if behind else "has diverged from"
    raise BranchOutOfSyncError(
        f"the local branch {branch} {state} {name}; devkit neither merges nor resets it; nothing was changed",
        fix=fix,
    )


def _object_type(base: Path, spec: str) -> str | None:
    """The type of the object ``spec`` (``<rev>:<path>``) names, ``None`` when it names none."""
    try:
        return _git(base, "cat-file", "-t", spec)
    except GitError as exc:
        if exc.returncode is None:
            raise
        return None


def _return_branch(base: Path, branch: str) -> str:
    """The recorded ``devkitBase`` the base checkout, which is on ``branch``, switches back to; refuse when it has
    uncommitted changes or no branch is recorded."""
    if not _clean(base):
        raise ConflictError(
            f"the base checkout {base} is on {branch} with uncommitted changes; nothing was changed",
            fix=f"Commit the changes on {branch} (or stash them) in {base}, then rerun",
        )
    back = _config(base, _marker(branch, BASE_KEY))
    if not back:
        raise ConflictError(
            f"the base checkout {base} is on {branch} and no branch to return to is recorded; nothing was changed",
            fix=f"git -C {shlex.quote(str(base))} switch <the branch {branch} integrates into>, then rerun",
        )
    return back


def _add(base: Path, path: Path, branch: str, *, existing: bool = False, revision: str | None = None) -> None:
    """``git worktree add -b branch path`` (``git worktree add path branch`` for an ``existing`` branch, which is never
    deleted) and the branch's marker; on failure, remove what was created before raising ``WORKTREE_ADD_FAILED``.

    The marker (``branch.<branch>.devkitWorktree = <path>``) is written to the common configuration (``--local`` in
    the base checkout), so ``finish`` can tell the branch from one devkit did not create. ``start`` checked that
    neither ``path`` nor ``branch`` existed, but another process may create either before Git does: Git then
    refuses with "already exists" and nothing of that is removed (``WORKTREE_BRANCH_EXISTS`` for the branch, which
    Git checks first; ``WORKTREE_CONFLICT`` for the path, once the branch Git created for it is removed). Otherwise
    a failed or timed-out call leaves its own registered, possibly half-checked-out worktree (which Git locks while
    it initializes it), removed with ``--force --force``, and its new branch, deleted with ``git branch -d`` only
    while its tip is still the base HEAD it was created from. What cannot be removed is named with the command that
    removes it.
    """
    origin = revision or _head(base)
    step = f"git worktree add {path}"
    try:
        add = ("add", str(path), branch) if existing else ("add", "-b", branch, str(path))
        if revision is not None and not existing:
            add += (revision,)
        _git_session(base, "worktree", *add, timeout=CHECKOUT_TIMEOUT)
        step = f"git config {_marker(branch)}"
        run_git(base, "config", "--local", _marker(branch), str(path))
    except GitError as exc:
        reason = exc.stderr or exc.message
        if _timed_out(exc):
            reason = f"{exc.message}: {exc.stderr}" if exc.stderr else exc.message
        if not existing and f"a branch named '{branch}' already exists" in exc.stderr:
            raise BranchExistsError(
                f"branch {branch} already exists: it was created while start ran; nothing was changed"
            ) from exc
        foreign = f"'{path}' already exists" in exc.stderr
        left = _undo_add(base, path, branch, origin, own_path=not foreign, own_branch=not existing)
        message = f"{step} failed: {reason}"
        if foreign and not left:
            raise ConflictError(
                f"{path} exists and is not a worktree of this repository: it was created while start ran; nothing"
                " was changed"
            ) from exc
        if not left:
            raise AddFailedError(f"{message}; the partial worktree and branch were removed") from exc
        raise AddFailedError(
            f"{message}; what it created could not all be removed",
            *(f"left: {item}" for item, _ in left),
            fix="Once the user agrees, "
            + " && ".join(command for _, command in left)
            + ", then rerun the same command",
        ) from exc


def _timed_out(error: GitError) -> bool:
    return isinstance(error.__cause__, subprocess.TimeoutExpired)


def _undo_add(
    base: Path, path: Path, branch: str, origin: str | None, *, own_path: bool = True, own_branch: bool = True
) -> list[tuple[str, str]]:
    """Remove what a failed ``git worktree add`` created; ``(what, the command that removes it)`` for each leftover.

    ``path`` is left alone unless ``own_path`` (the add did not fail because it already existed), the branch unless
    ``own_branch`` (the add created it). The branch is deleted only while its tip is ``origin``, the base HEAD it
    was created from; one whose tip moved (a hook committed to it, or another process made it) is a leftover the
    user decides about.
    """
    quoted = shlex.quote(str(base))
    left: list[tuple[str, str]] = []
    if own_path:
        try:
            registered = any(entry.path == path for entry in _entries(base))
        except GitError:
            registered = True
        if registered:
            try:
                _git_session(base, "worktree", "remove", "--force", "--force", str(path), timeout=CHECKOUT_TIMEOUT)
            except GitError as exc:
                _log.info("could not remove the partial worktree %s: %s", path, exc.message)
                left.append(
                    (f"worktree {path}", f"git -C {quoted} worktree remove --force --force {shlex.quote(str(path))}")
                )
        if not registered and (path.exists() or path.is_symlink()):
            left.append((f"directory {path}", f"rm -rf {shlex.quote(str(path))}"))
    if not own_branch:
        return left
    remains, moved = True, False
    try:
        tip = _query(base, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}")
        remains, moved = tip is not None, tip is not None and tip != origin
        if remains and not moved and not left:
            run_git(base, "branch", "-d", branch)
            remains = False
    except GitError as exc:
        _log.info("could not delete the branch %s: %s", branch, exc.message)
    if remains:
        note = " (it no longer points at the base HEAD it was created from)" if moved else ""
        left.append((f"branch {branch}{note}", f"git -C {quoted} branch -D {branch}"))
    return left


def _interpreter(checkout: Path) -> str:
    """The checkout's ``.venv`` interpreter when devkit is installed in it (as the commit gate hooks decide), else
    the one running this process."""
    python = checkout / ".venv/bin/python"
    if python.is_file() and any(
        info.is_dir() for info in checkout.glob(".venv/lib/python*/site-packages/devkit_agt-*.dist-info")
    ):
        return str(python)
    return sys.executable


def _sync(interpreter: str, target: Path) -> SyncFailedWarning | None:
    """Run ``devkit sync --locked`` in ``target``; ``None`` on success, else the warning that reports why.

    The sync runs with ``--format json``, so a refusal arrives as one error object: the warning carries its code,
    message, targets and fix. Rerunning cures neither a stale receipt (``RECEIPT_STALE``) nor a missing package
    (``SELECTION_INVALID``), so rerunning is the fix only when the error names none, or the output is not an error
    object (a timeout, a crash, a devkit without ``--locked``).
    """
    label = "devkit sync --locked"
    rerun = f"cd {shlex.quote(str(target))} && {shlex.quote(interpreter)} -m devkit sync --locked"
    argv = [interpreter, "-m", "devkit", "sync", "--locked", "--format", "json", "-w", str(target)]
    completed = _execute(argv, target, label, SYNC_TIMEOUT)
    if isinstance(completed, str):
        return SyncFailedWarning(completed, fix=rerun)
    if completed.returncode == 0:
        return None
    error = _error_object(completed.stdout)
    if error is None:
        return SyncFailedWarning(_failure(label, completed), fix=rerun)
    raw = error.get("advisory")
    advisory: dict[str, Any] = raw if isinstance(raw, dict) else {}
    fix = advisory.get("fix")
    targets = advisory.get("target_files") or []
    return SyncFailedWarning(
        f"{label} exited {completed.returncode} in {target}: ({error.get('code')}) {error.get('message')}",
        *(str(detail) for detail in advisory.get("details") or []),
        target_files=[str(target / name) for name in targets if isinstance(name, str)],
        fix=f"In {target}: {fix}" if isinstance(fix, str) and fix else rerun,
        what_to_report=advisory.get("what_to_report") if isinstance(advisory.get("what_to_report"), str) else None,
    )


def _error_object(stdout: bytes) -> dict[str, Any] | None:
    """The ``{"error": {...}}`` a devkit command prints under ``--format json`` when it fails, else ``None``."""
    try:
        document = json.loads(os.fsdecode(stdout))
    except ValueError:
        return None
    error = document.get("error") if isinstance(document, dict) else None
    return error if isinstance(error, dict) and isinstance(error.get("code"), str) else None


def _session(
    argv: list[str], cwd: Path | None, env: dict[str, str], timeout: float
) -> subprocess.CompletedProcess[bytes]:
    """Run ``argv`` in a session of its own with its output captured; ``OSError`` when it cannot start.

    A timeout (``subprocess.TimeoutExpired``, re-raised) or any other exception first kills the whole process
    group, so what the command started (``uv sync`` under a shell, a hook or filter under Git) stops with it.
    """
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    with process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except BaseException:
            _kill_group(process)
            raise
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)


def _git_session(cwd: Path, *args: str, timeout: float) -> bytes:
    """``run_git`` (same environment, errors and output) for Git commands that run hooks and filters.

    ``git worktree add`` runs the ``post-checkout`` hook and checkout filters (Git LFS); in a session of its own, a
    timeout kills them with Git instead of leaving them writing into a path the cleanup removes. A timeout is a
    ``GitError`` whose ``__cause__`` is ``subprocess.TimeoutExpired``, as from ``run_git``.
    """
    command = ("git", "-C", str(cwd), *args)
    label = f"git {args[0]}"
    env = {**os.environ, "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0"}
    try:
        completed = _session(list(command), None, env, timeout)
    except subprocess.TimeoutExpired as exc:
        raise GitError(f"{label} timed out after {timeout}s in {cwd}", command=command) from exc
    except OSError as exc:
        raise GitError(f"git is not available: {exc}", command=command) from exc
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GitError(
            f"{label} failed in {cwd}: {stderr or f'exit status {completed.returncode}'}",
            command=command,
            returncode=completed.returncode,
            stderr=stderr,
        )
    return completed.stdout


def _execute(argv: list[str], cwd: Path, label: str, timeout: float) -> subprocess.CompletedProcess[bytes] | str:
    """Run ``argv`` in ``cwd`` with its output captured, without the caller's ``VIRTUAL_ENV``, in a session of its
    own (``_session``); why it could not run when it timed out or did not start."""
    env = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
    try:
        return _session(argv, cwd, env, timeout)
    except subprocess.TimeoutExpired:
        return f"{label} did not finish within {timeout:.0f}s"
    except OSError as exc:
        return f"{label} could not start: {exc}"


def _kill_group(process: subprocess.Popen[bytes]) -> None:
    """Kill the process group ``process`` leads and reap it; its pipes are left unread."""
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(process.pid, signal.SIGKILL)
    process.wait()


def _failure(label: str, completed: subprocess.CompletedProcess[bytes]) -> str:
    """Why a command failed: its exit code, its advisory headlines (the code and message of each block) and the last
    lines of its output, so a long advisory block never pushes its headline out."""
    lines = os.fsdecode(completed.stderr or completed.stdout).strip().splitlines()
    headlines = [line for line in lines if line.startswith(("[ERROR]", "[WARN]"))]
    tail = [line for line in lines[-5:] if line not in headlines]
    shown = [*headlines, *tail]
    return f"{label} exited {completed.returncode}" + (":\n" + "\n".join(shown) if shown else "")


def _run(argv: list[str], cwd: Path, label: str, timeout: float) -> str | None:
    """Run ``argv`` in ``cwd`` with its output captured; ``None`` on success, else why it failed."""
    completed = _execute(argv, cwd, label, timeout)
    if isinstance(completed, str):
        return completed
    return None if completed.returncode == 0 else _failure(label, completed)


def _find(position: Position, branch: str) -> _Entry | None:
    """The branch's worktree (by its path, else its branch), checked for ``finish``; ``None`` when there is none.

    Only a linked worktree on ``branch`` qualifies: ``finish`` judges the merge by that branch, so removing a worktree
    that is detached or on another branch would drop commits the branch does not hold (``WORKTREE_CONFLICT``), as
    would treating the base checkout as the task; a base checkout on a branch ``start_branch`` created is told to
    switch back to its recorded ``devkitBase``. A locked worktree is ``WORKTREE_LOCKED``.
    """
    base, path = position.base, path_for(position, branch)
    entries = _entries(base)
    entry = next((item for item in entries if item.path == path), None)
    entry = entry or next((item for item in entries if item.branch == branch), None)
    if entry is None:
        return None
    if entry.path == base:
        back = _config(base, _marker(branch, BASE_KEY))
        if back:
            raise BaseOnBranchError(
                f"the base checkout is on {branch}; finish works on it from {back}, the branch it was started from;"
                " nothing was changed",
                fix=f"git -C {shlex.quote(str(base))} switch {back}",
            )
        raise ConflictError(
            f"{branch} is the base checkout's branch; finish integrates a task branch into the base and never"
            " removes it",
            fix="Pass the branch of a linked worktree (`devkit worktree status` lists them)",
        )
    if entry.branch != branch:
        raise ConflictError(
            f"{entry.path} is on {entry.branch or 'a detached HEAD'}, not {branch}; removing it would drop commits"
            f" the branch {branch} does not hold; nothing was changed",
            fix=f"Check out {branch} in {entry.path} with the worktree's commits on it, then rerun",
        )
    if entry.locked:
        raise LockedError(
            f"{entry.path} is locked; nothing was changed",
            fix=f"git -C {shlex.quote(str(base))} worktree unlock {shlex.quote(str(entry.path))}",
        )
    return entry


def find(position: Position, branch: str) -> Path:
    """The path of the branch's linked worktree, found by its path or its branch.

    ``WORKTREE_NOT_FOUND`` when there is none; ``WORKTREE_CONFLICT`` or ``WORKTREE_LOCKED`` when ``finish`` would
    refuse to remove it.
    """
    entry = _find(position, branch)
    if entry is None:
        raise NotFoundError(f"no worktree at {path_for(position, branch)} or on branch {branch}")
    return entry.path


def finish(
    position: Position,
    branch: str,
    *,
    merge: bool = False,
    pull_request: str = "auto",
    delete_branch: bool = True,
    before_remove: Callable[[FinishResult], None] | None = None,
    guard: Callable[[str, str], None] | None = None,
    network: str = "allow",
    before_step: Callable[[str, FinishResult], None] | None = None,
    merge_method: str = "no-ff",
) -> FinishResult:
    """Integrate the activity branch into the base, then remove its worktree and the branch.

    ``network="forbid"`` excludes fetch and push. ``before_step(step, result)`` runs immediately before each
    local mutation (merge, worktree_remove, branch_delete or marker_clear); it may refuse by raising.

    ``merge`` lands the branch on the base (it must be clean and on a branch, and contain the tip of its upstream
    when one is configured and reachable) and pushes the base branch to that upstream. The branch must contain the
    base HEAD (``WORKTREE_MERGE_NOT_FF`` otherwise); under ``merge_method="no-ff"`` (``[worktree] merge``) the base
    fast-forwards onto a merge commit ``merging.build_result`` builds from the base HEAD and the tip, under
    ``"ff-only"`` onto the tip. A branch the base already contains builds nothing (a rerun after the merge). A failed push is a
    ``WORKTREE_PUSH_FAILED`` or ``WORKTREE_PUSH_REJECTED`` warning and does not stop the cleanup. Without ``merge``
    the branch must already be merged into the base HEAD. With ``merge``, ``guard(merge_base, tip)`` runs after the
    other checks and before the first change, with the commit ids of the branch's merge base with the base HEAD
    (empty when there is none) and of its tip; it refuses by raising (the ``devkit.finish_guard`` extensions in the
    CLI). The checks of the worktree's branch and lock, the base and the upstreams (including whether ``git branch
    -d`` will accept the branch) run before the first change; uncommitted changes in the worktree surface when it is
    removed (``WORKTREE_DIRTY``). ``before_remove`` runs once the merge is confirmed and before the worktree is
    removed (a caller's own cleanup; it runs again on a rerun). A refusal after that carries the partial result as
    ``error.result``, also an ``AdvisoryError`` that ``before_remove`` raises.

    A branch without a worktree is finished only when ``start``, ``start_branch`` or ``attach`` marked it (its
    ``branch.<branch>.devkitWorktree`` marker): one whose worktree is already gone (what a stopped run leaves), or
    one ``start_branch`` created, which ``merge`` integrates like a worktree's branch. Any other branch of that name
    is ``WORKTREE_NOT_FOUND``, and nothing runs, merges, pushes or is deleted for it. The marker gates only this
    path: a branch whose worktree exists finishes whether or not it carries it. It lasts until the finish
    completes: ``git branch -d`` removes it with the branch, and without ``delete_branch`` it is unset once the
    worktree is removed, so a rerun after a completed finish is ``WORKTREE_NOT_FOUND`` either way.
    """
    if network not in {"allow", "forbid"}:
        raise ArgumentError("network must be allow or forbid")
    check_branch(branch)
    if position.linked:
        raise RunFromBaseError(
            f"{position.root} is the worktree finish would remove", target_files=[str(position.base)]
        )
    if merge and pull_request == "required":
        raise PullRequestPolicyError(
            '[worktree] pull_request = "required" integrates through a pull request; --merge would merge locally'
        )
    base, ref = position.base, f"refs/heads/{branch}"
    entry = _find(position, branch)
    if entry is None:
        exists = _succeeds(base, "rev-parse", "--verify", "--quiet", ref)
        if not exists or not _created(base, branch):
            if not exists or not _merged(base, ref, _head(base)):
                unmerged = f", and branch {branch} is not merged into the base HEAD" if exists else ""
                raise NotFoundError(f"no worktree at {path_for(position, branch)} or on branch {branch}{unmerged}")
            # Only a marked branch resumes, whether or not it is deleted: any other merged branch (the base's own
            # included) would otherwise run ``before_remove``, merge and push for a task that never existed.
            raise NotFoundError(
                f"no worktree at {path_for(position, branch)} or on branch {branch}; the branch {branch} is merged"
                f" into the base HEAD but has no {_marker(branch)} marker, so devkit worktree start did not create"
                " it, or a finish already completed for it (or start created it before devkit recorded the marker;"
                " such branches are not resumed automatically); finish does not resume it; nothing was changed",
                fix=f"Once the user agrees, git -C {shlex.quote(str(base))} branch -d {branch}"
                if delete_branch
                else f"Nothing is left to finish: {branch} has no worktree, and [worktree] delete_branch = false"
                " keeps its branch",
            )
        _log.info("%s has no worktree; finishing the marked branch alone", branch)
        result = FinishResult(branch, _marked_path(position, branch), removed=_gone(position, branch))
        back = _config(base, _marker(branch, BASE_KEY))
        if merge and back and position.branch != back:
            raise ConflictError(
                f"{branch} was started from {back}, but the base checkout is on {position.branch or 'a detached HEAD'};"
                f" finish --merge integrates it into {back}; nothing was changed",
                fix=f"git -C {shlex.quote(str(base))} switch {back}, then rerun",
            )
    else:
        result = FinishResult(branch, entry.path)
    if merge:
        if position.branch is None:
            raise BaseDetachedError(
                f"{base} is on a detached HEAD; the merge would move no branch and nothing would be pushed",
                target_files=[str(base)],
            )
        if not _clean(base):
            raise BaseDirtyError(f"{base} has uncommitted changes", target_files=[str(base)])
    elif not _merged(base, ref, _head(base)):
        raise UnmergedError(f"{branch} is not merged into the base HEAD; nothing was changed")
    if delete_branch:
        _check_deletable(base, branch)
    if merge:
        tip = _git(base, "rev-parse", "--verify", f"{ref}^{{commit}}")
        head = _head(base)
        if head is not None and not _merged(base, tip, head):
            if not _merged(base, head, tip):
                raise MergeNotFastForwardError(
                    f"{branch} does not contain the base HEAD {head[:12]}; finish --merge lands only a branch that"
                    " contains it; nothing was changed"
                )
            if merge_method == "no-ff":
                check_identity(base)
        if guard is not None:
            guard((_query(base, "merge-base", head, tip) or "") if head else "", tip)
        if network == "allow":
            _check_upstream(position)
        if _git(base, "rev-parse", "--verify", f"{ref}^{{commit}}") != tip:
            raise ConflictError(
                f"{branch} moved while finish checked it (it was {tip[:7]}); only the checked commit is merged;"
                " nothing was changed",
                fix="Let the run committing to it end, then rerun the same command",
            )
        landing = tip
        if head is not None and _head(base) != head:
            raise ConflictError(
                f"the base HEAD moved while finish checked {branch} (it was {head[:7]}); nothing was changed",
                fix="Let the run committing to the base end, then rerun the same command",
            )
        if head is not None and not _merged(base, tip, head):
            # The commit the guard checked, not the branch ref, which a running worker could move meanwhile.
            landing = build_result(
                base,
                branch=branch,
                target_branch=position.branch or "HEAD",
                target=head,
                source=tip,
                method=merge_method,
            )
        try:
            if before_step is not None:
                before_step("merge", result)
            run_git(base, "merge", "--ff-only", "--quiet", landing)
        except GitError as exc:
            if exc.returncode is None:
                raise
            if network == "forbid" and _merged(base, _head(base), landing):
                raise MergeFailedError(f"local merge of {branch} failed: {exc.stderr or exc.message}") from exc
            raise MergeNotFastForwardError(f"{branch} cannot be fast-forwarded onto the base: {exc.stderr}") from exc
        result.merged = True
        if network == "allow":
            _push(position, result)
        else:
            result.push = "excluded"
    try:
        if before_remove is not None:
            before_remove(result)
        if result.removed is False:
            if before_step is not None:
                before_step("worktree_remove", result)
            _remove(base, result.path)
            result.removed = True
        if delete_branch:
            try:
                if before_step is not None:
                    before_step("branch_delete", result)
                run_git(base, "branch", "-d", branch)
            except GitError as exc:
                raise BranchDeleteFailedError(
                    f"the worktree is removed, but git branch -d {branch} failed: {exc.stderr or exc.message}"
                ) from exc
            result.branch_deleted = True
        else:
            if before_step is not None:
                before_step("marker_clear", result)
            _unmark(base, branch)  # the finish is complete; a rerun no longer resumes
    except AdvisoryError as error:
        # Every refusal from here on carries the partial result, an advisory ``before_remove`` raises included
        # (unless that caller's error defines a ``result`` of its own).
        if isinstance(error, WorktreeError) or not hasattr(error, "result"):
            vars(error)["result"] = result
        raise
    return result


def _gone(position: Position, branch: str) -> bool | None:
    """For a branch without a worktree: ``True`` when its worktree was removed earlier (its marker names the worktree
    path), ``None`` when it never had one (``start_branch`` marks the checkout it switched; or no marker at all)."""
    value = _config(position.base, _marker(branch))
    return True if value and Path(value) == path_for(position, branch) else None


def _marked_path(position: Position, branch: str) -> Path:
    """The checkout a marked branch without a worktree belongs to: the path its marker records (``start_branch``
    records the checkout it switched), else the branch's worktree path."""
    value = _config(position.base, _marker(branch))
    return Path(value) if value else path_for(position, branch)


def discard(
    position: Position, branch: str, *, before_remove: Callable[[FinishResult], None] | None = None
) -> FinishResult:
    """Drop an unmerged activity branch: remove its worktree and force-delete the branch (``git branch -D``).

    The close of a task (a depth escalation, a supersede, an abandon) is the only use; the caller decides it on the
    authority its close kind needs. Any activity branch is dropped, whether or not devkit started it;
    a worktree with uncommitted or untracked changes is ``WORKTREE_DIRTY``: never removed by force. ``before_remove``
    runs before the worktree is removed, as for ``finish``. Remote branches and pull requests are the caller's.
    """
    check_branch(branch)
    if position.linked:
        raise RunFromBaseError(
            f"{position.root} is the worktree discard would remove", target_files=[str(position.base)]
        )
    base, ref = position.base, f"refs/heads/{branch}"
    entry = _find(position, branch)
    exists = _succeeds(base, "rev-parse", "--verify", "--quiet", ref)
    if entry is None:
        if not exists:
            raise NotFoundError(f"no worktree at {path_for(position, branch)} or on branch {branch}")
        # An activity branch is dropped whether or not devkit started it (another checkout, made by hand): its name
        # says it is a task's, and the close that drops it is the caller's decision.
        result = FinishResult(branch, _marked_path(position, branch), removed=_gone(position, branch))
    else:
        result = FinishResult(branch, entry.path)
    try:
        if before_remove is not None:
            before_remove(result)
        if result.removed is False:
            _remove(base, result.path)
            result.removed = True
        if exists:
            try:
                run_git(base, "branch", "-D", branch)
            except GitError as exc:
                raise BranchDeleteFailedError(
                    f"the worktree is removed, but git branch -D {branch} failed: {exc.stderr or exc.message}"
                ) from exc
            result.branch_deleted = True
        _unmark(base, branch)
        result.discarded = True
    except AdvisoryError as error:
        if isinstance(error, WorktreeError) or not hasattr(error, "result"):
            vars(error)["result"] = result
        raise
    return result


def _remove(base: Path, path: Path) -> None:
    try:
        _git_session(base, "worktree", "remove", str(path), timeout=CHECKOUT_TIMEOUT)
    except GitError as exc:
        if _timed_out(exc):  # the directory may be partly deleted while still registered
            raise RemoveFailedError(
                f"{exc.message}; {path} may be partly deleted and is still a registered worktree, so a rerun would"
                " report its deleted files as uncommitted changes",
                fix=f"Once the user agrees, git -C {shlex.quote(str(base))} worktree remove --force"
                f" {shlex.quote(str(path))}, then rerun the same command",
            ) from exc
        if "modified or untracked" in exc.stderr or "--force" in exc.stderr:
            raise DirtyError(f"{path} has uncommitted changes: {exc.stderr}") from exc
        raise RemoveFailedError(f"git worktree remove {path} failed: {exc.stderr or exc.message}") from exc


def _check_deletable(base: Path, branch: str) -> None:
    """Refuse before any change when ``git branch -d`` would refuse ``branch`` once it is merged into the base.

    A branch whose upstream exists is deleted only when that upstream contains it (Git checks HEAD otherwise, which
    the merge or the merged check guarantees): a task branch pushed with ``-u`` and committed to since.
    """
    upstream = _git(base, "for-each-ref", "--format=%(upstream)", f"refs/heads/{branch}")
    if not upstream or not _succeeds(base, "rev-parse", "--verify", "--quiet", upstream):
        return
    if _succeeds(base, "merge-base", "--is-ancestor", f"refs/heads/{branch}", upstream):
        return
    remote = _config(base, f"branch.{branch}.remote")
    merge_ref = _config(base, f"branch.{branch}.merge")
    quoted = shlex.quote(str(base))
    if remote and remote != "." and merge_ref:
        fix = f"git -C {quoted} push {shlex.quote(remote)} refs/heads/{branch}:{merge_ref}"
    else:
        fix = f"git -C {quoted} branch --unset-upstream {branch}"
    raise BranchUnpushedError(
        f"{upstream}, the upstream of {branch}, lacks its commits, so git branch -d would refuse the branch after"
        " the merge; nothing was changed",
        fix=fix,
    )


def _upstream(position: Position) -> tuple[str, str] | None:
    """The base branch's configured remote and remote ref; ``None`` on a detached HEAD or without an upstream."""
    if position.branch is None:
        return None
    remote = _config(position.base, f"branch.{position.branch}.remote")
    merge_ref = _config(position.base, f"branch.{position.branch}.merge")
    if not remote or remote == "." or not merge_ref:
        return None
    return remote, merge_ref


def _check_upstream(position: Position) -> None:
    """Refuse before the merge when the base branch's upstream has commits the base lacks: the push would fail.

    The upstream ref is fetched (no prompts, within ``FETCH_TIMEOUT``). A fetch that fails (offline, an
    unreachable remote, a remote ref that does not exist yet) skips the check: the merge stays local until the
    push, which reports what remains.
    """
    upstream = _upstream(position)
    if upstream is None:
        return
    remote, merge_ref = upstream
    base = position.base
    try:
        run_git(base, "fetch", "--quiet", "--no-tags", remote, merge_ref, timeout=FETCH_TIMEOUT)
    except GitError as exc:
        _log.info("could not fetch %s %s; the base is not checked against it: %s", remote, merge_ref, exc.message)
        return
    tip = _query(base, "rev-parse", "--verify", "--quiet", "FETCH_HEAD^{commit}")
    if tip is None or _succeeds(base, "merge-base", "--is-ancestor", tip, "HEAD"):
        return
    raise BaseBehindError(
        f"{remote} {merge_ref} has commits the base branch {position.branch} lacks, so the push after the merge"
        " would be rejected; nothing was changed",
        fix=f"git -C {shlex.quote(str(base))} pull --ff-only {shlex.quote(remote)} {merge_ref}",
        target_files=[str(base)],
    )


def _push(position: Position, result: FinishResult) -> None:
    """Push the base branch to its configured upstream with an explicit refspec; never prompts, never forces."""
    result.push = "no-upstream"
    upstream = _upstream(position)
    if upstream is None or position.branch is None:
        return
    remote, merge_ref = upstream
    base = shlex.quote(str(position.base))
    refspec = f"refs/heads/{position.branch}:{merge_ref}"
    push = f"git -C {base} push {shlex.quote(remote)} {refspec}"
    try:
        run_git(position.base, "push", "--quiet", remote, refspec, timeout=PUSH_TIMEOUT)
    except GitError as exc:
        reason = exc.stderr or exc.message
        if "[rejected]" in exc.stderr:  # the upstream moved on: pushing again fails identically
            result.push = "rejected"
            result.notices.append(
                PushRejectedWarning(
                    f"the base was merged and the worktree is being cleaned up, but {remote} rejected the push"
                    f" because it has commits the base lacks: {reason}",
                    fix=(
                        f"git -C {base} fetch {shlex.quote(remote)} {merge_ref} && git -C {base} merge --no-ff -m"
                        f" {shlex.quote(merge_message(f'{remote}/{_short(merge_ref)}', position.branch))} FETCH_HEAD"
                        f" && {push}"
                    ),
                )
            )
            return
        result.push = "failed"
        result.notices.append(
            PushFailedWarning(
                f"the base was merged and the worktree is being cleaned up, but the push to {remote} failed: {reason}",
                fix=push,
            )
        )
        return
    result.push = "pushed"


def _short(ref: str) -> str:
    return ref.removeprefix("refs/heads/")


def _config(base: Path, key: str) -> str:
    return _query(base, "config", "--get", key) or ""


def status(position: Position) -> StatusResult:
    """Every worktree with its merge and dirty state, and the unmerged branches no worktree checks out."""
    base = position.base
    entries = _entries(base)
    base_branch = _query(base, "symbolic-ref", "--quiet", "--short", "HEAD")
    base_head = _head(base)

    def merged(rev: str | None) -> bool:
        return _merged(base, rev, base_head)

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
