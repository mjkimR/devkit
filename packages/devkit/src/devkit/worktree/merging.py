"""The result commit a local integration lands, built in the object store and never in a checkout.

``[worktree] merge`` selects the method: ``"no-ff"`` (the default) lands a merge commit whose first parent is the
target and whose second parent is the approved branch tip, so every commit of the task stays an ancestor of the base
and ``git log --first-parent`` shows one line per task; ``"ff-only"`` lands the tip itself. ``build_result`` builds
the commit (``git commit-tree``; with an advanced target ``git merge-tree --write-tree``, Git 2.38 or later) and
changes no ref; ``fast_forward`` then moves the base checkout onto it, so the base checkout never stops mid-merge.
See ``ADR-merge-commit-outside-checkout``.
"""

from __future__ import annotations

import os
import re
import tomllib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from devkit.core.errors import GitError
from devkit.core.git import run_git
from devkit.core.locks import file_lock
from devkit.worktree.config import MERGE_METHODS
from devkit.worktree.errors import (
    CommitFailedError,
    GitUnsupportedError,
    MergeConflictError,
    MergeFailedError,
    MergeNotFastForwardError,
)

COMMIT_TIMEOUT = 30.0  # seconds for `git commit-tree`, a signing program included
MERGE_TREE_TIMEOUT = 120.0  # seconds for `git merge-tree --write-tree`
MERGE_TREE_VERSION = (2, 38)  # the first Git with `merge-tree --write-tree`
LOCK_NAME = "devkit-integration.lock"  # in the common Git directory; serializes devkit integration executors
CONFIG_PATH = ".devkit/config.toml"
_VERSION = re.compile(r"git version (\d+)\.(\d+)")


def _git(base: Path, *args: str, timeout: float | None = None) -> str:
    if timeout is None:
        return os.fsdecode(run_git(base, *args)).strip()
    return os.fsdecode(run_git(base, *args, timeout=timeout)).strip()


def is_ancestor(base: Path, ancestor: str, descendant: str) -> bool:
    """Whether commit ``ancestor`` is contained in ``descendant`` (a commit is its own ancestor)."""
    try:
        run_git(base, "merge-base", "--is-ancestor", ancestor, descendant)
    except GitError as exc:
        if exc.returncode == 1:
            return False
        raise
    return True


def merge_message(branch: str, target_branch: str) -> str:
    """The devkit-composed merge commit message; both names are validated branch names, never caller text."""
    return f"chore(merge): integrate {branch} into {target_branch}"


@contextmanager
def integration_lock(common_dir: Path, *, timeout: float = 0) -> Iterator[None]:
    """Hold the Git common directory's integration lock; ``LOCK_HELD`` when another executor keeps it past ``timeout``."""
    with file_lock(common_dir / LOCK_NAME, timeout=timeout, what="waiting for the devkit integration lock"):
        yield


def source_merge_method(base: Path, source: str) -> str | None:
    """The ``[worktree] merge`` value committed at ``source``, or ``None`` when it sets none or cannot be read."""
    try:
        if not _git(base, "ls-tree", "--name-only", source, "--", CONFIG_PATH):
            return None
        data = tomllib.loads(os.fsdecode(run_git(base, "show", f"{source}:{CONFIG_PATH}")))
    except (GitError, ValueError, UnicodeError):
        return None
    table = data.get("worktree")
    value = table.get("merge") if isinstance(table, dict) else None
    return value if value in MERGE_METHODS else None


def merge_method(base: Path, configured: str, source: str) -> str:
    """The method in force: ``"ff-only"`` in the base's (``configured``) or the source's policy wins."""
    return "ff-only" if "ff-only" in (configured, source_merge_method(base, source)) else "no-ff"


def check_identity(base: Path) -> None:
    """Refuse before any change when Git has no committer identity for the merge commit (``WORKTREE_COMMIT_FAILED``)."""
    try:
        run_git(base, "var", "GIT_COMMITTER_IDENT")
    except GitError as exc:
        raise CommitFailedError(
            f"Git has no committer identity for the merge commit; nothing was changed: {exc.stderr or exc.message}"
        ) from exc


def _signs(base: Path) -> bool:
    """Whether ``commit.gpgSign`` asks for signed commits; ``git commit-tree`` does not read it on its own."""
    try:
        return _git(base, "config", "--type=bool", "--get", "commit.gpgSign") == "true"
    except GitError as exc:
        if exc.returncode == 1:  # unset
            return False
        raise


def git_version(base: Path) -> tuple[int, int]:
    """The running Git's major and minor version; ``(0, 0)`` when it cannot be read."""
    match = _VERSION.match(_git(base, "version"))
    return (int(match.group(1)), int(match.group(2))) if match else (0, 0)


def _merge_tree(base: Path, target: str, source: str) -> str:
    if git_version(base) < MERGE_TREE_VERSION:
        raise GitUnsupportedError(
            "merging an advanced target needs git merge-tree --write-tree (Git 2.38 or later); nothing was changed"
        )
    try:
        output = _git(base, "merge-tree", "--write-tree", "--no-messages", target, source, timeout=MERGE_TREE_TIMEOUT)
    except GitError as exc:
        if exc.returncode == 1:
            raise MergeConflictError(
                "the target's later commits conflict with the task branch; nothing was changed on the target"
            ) from exc
        raise MergeFailedError(
            f"git merge-tree failed; nothing was changed on the target: {exc.stderr or exc.message}"
        ) from exc
    return output.splitlines()[0].strip()


def build_result(
    base: Path,
    *,
    branch: str,
    target_branch: str,
    target: str,
    source: str,
    method: str,
    advance: bool = False,
) -> str:
    """Build the commit that lands ``source`` onto ``target`` and return its id; no ref or checkout changes.

    ``"ff-only"`` returns ``source`` when it contains ``target``, else ``WORKTREE_MERGE_NOT_FF``. ``"no-ff"`` commits
    the source tree with parents ``target`` and ``source`` when the source contains the target; otherwise, only with
    ``advance`` (an approved integration absorbing later target commits), it merges the trees with
    ``git merge-tree --write-tree`` (``WORKTREE_GIT_UNSUPPORTED`` below Git 2.38, ``WORKTREE_MERGE_CONFLICT`` on a
    conflict) and commits that. ``git commit-tree`` uses the configured identity, signs (``-S``, with
    ``user.signingKey`` and ``gpg.*``) when ``commit.gpgSign`` is on, since the plumbing command ignores that setting
    itself, and is bounded by ``COMMIT_TIMEOUT`` (``WORKTREE_COMMIT_FAILED``). A refused or failed build leaves at most an unreferenced object.
    """
    if method not in MERGE_METHODS:
        raise ValueError(f"unknown merge method {method!r}")
    contained = is_ancestor(base, target, source)
    if method == "ff-only":
        if not contained:
            raise MergeNotFastForwardError(
                f'{branch} does not contain {target_branch} at {target[:12]} and merge = "ff-only" allows only a'
                " fast-forward; nothing was changed"
            )
        return source
    if contained:
        tree = _git(base, "rev-parse", "--verify", f"{source}^{{tree}}")
    elif advance:
        tree = _merge_tree(base, target, source)
    else:
        raise MergeNotFastForwardError(
            f"{branch} does not contain {target_branch} at {target[:12]}; nothing was changed"
        )
    try:
        return _git(
            base,
            "commit-tree",
            *(["-S"] if _signs(base) else []),
            tree,
            "-p",
            target,
            "-p",
            source,
            "-m",
            merge_message(branch, target_branch),
            timeout=COMMIT_TIMEOUT,
        )
    except GitError as exc:
        reason = "timed out" if exc.returncode is None else f"failed: {exc.stderr or exc.message}"
        raise CommitFailedError(
            f"git commit-tree of the merge commit {reason}; nothing was changed on the target"
        ) from exc


def fast_forward(base: Path, result: str) -> None:
    """Fast-forward the base checkout onto ``result`` (``git merge --ff-only``); it never stops mid-merge."""
    run_git(base, "merge", "--ff-only", "--quiet", result)
