"""The result commit a local integration lands, built in the object store and never in a checkout.

``[worktree] merge`` selects the method: ``"no-ff"`` (the default) lands a merge commit whose first parent is the
target and whose second parent is the approved branch tip, so every commit of the task stays an ancestor of the base
and ``git log --first-parent`` shows one line per task; ``"ff-only"`` lands the tip itself. ``build_result`` builds
the commit (``git commit-tree``; with an advanced target ``git merge-tree --write-tree``, Git 2.38 or later) and
changes no ref; ``fast_forward`` then moves the base checkout onto it, so the base checkout never stops mid-merge.
See ``ADR-merge-commit-outside-checkout``. Local preparation of a moved target builds the same merge as a
deterministic prospective commit that never lands (``ADR-moved-target-merge``).
"""

from __future__ import annotations

import os
import re
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from devkit_core.base.errors import GitError
from devkit_core.core.git import is_ancestor, run_git, run_git_result, run_git_text
from devkit_core.core.locks import file_lock
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project.repositories.project import commit_config

from devkit_agt.features.worktree.models.errors import (
    CommitFailedError,
    GitUnsupportedError,
    MergeConflictError,
    MergeFailedError,
    MergeNotFastForwardError,
)
from devkit_agt.features.worktree.models.merging import SIDES, ConflictSettler
from devkit_agt.features.worktree.repositories.config import MERGE_METHODS

COMMIT_TIMEOUT = 30.0  # seconds for `git commit-tree`, a signing program included
MERGE_TREE_TIMEOUT = 120.0  # seconds for `git merge-tree --write-tree`
MERGE_TREE_VERSION = (2, 38)  # the first Git with `merge-tree --write-tree`
LOCK_NAME = "devkit-integration.lock"  # in the common Git directory; serializes devkit integration executors
_VERSION = re.compile(r"git version (\d+)\.(\d+)")


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
        data = commit_config(base, source)
    except (GitError, ConfigError):
        return None
    table = data.get("worktree") if data is not None else None
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
        return run_git_text(base, "config", "--type=bool", "--get", "commit.gpgSign") == "true"
    except GitError as exc:
        if exc.returncode == 1:  # unset
            return False
        raise


def git_version(base: Path) -> tuple[int, int]:
    """The running Git's major and minor version; ``(0, 0)`` when it cannot be read."""
    match = _VERSION.match(run_git_text(base, "version"))
    return (int(match.group(1)), int(match.group(2))) if match else (0, 0)


def _merge_tree_output(base: Path, target: str, source: str) -> tuple[int, bytes]:
    """Run ``git merge-tree --write-tree -z --no-messages``; its exit status (``0`` clean, ``1`` conflicted) and output.

    Exit ``1`` is an answer whose standard output carries the conflicted entries, so the shared runner accepts it; any
    other failure is ``MergeFailedError``.
    """
    try:
        return run_git_result(
            base,
            *("merge-tree", "--write-tree", "-z", "--no-messages", target, source),
            ok_returncodes=(0, 1),
            timeout=MERGE_TREE_TIMEOUT,
        )
    except GitError as exc:
        if exc.returncode is None:  # Git did not start or did not finish
            raise MergeFailedError(f"{exc.message}; nothing was changed on the target") from exc
        raise MergeFailedError(
            f"git merge-tree failed; nothing was changed on the target: {exc.stderr or f'exit status {exc.returncode}'}"
        ) from exc


def _conflicts(records: list[bytes]) -> dict[str, dict[int, tuple[str, str]]]:
    """The conflicted paths of ``merge-tree -z`` output and, per path, each stage's ``(mode, object id)``."""
    found: dict[str, dict[int, tuple[str, str]]] = {}
    for record in records:
        if not record:
            continue
        meta, _, raw = record.partition(b"\t")
        mode, oid, stage = meta.decode().split(" ")
        found.setdefault(os.fsdecode(raw), {})[int(stage)] = (mode, oid)
    return found


def _seeded_tree(base: Path, tree: str, sides: dict[str, tuple[str, str] | None]) -> str:
    """``tree`` with each path of ``sides`` set to its ``(mode, object id)``, or removed for ``None``.

    Uses a temporary index outside the repository, so no index, ref or checkout of the repository changes.
    """
    lines = b"".join(
        (f"{entry[0]} {entry[1]}" if entry else f"0 {'0' * len(tree)}").encode() + b"\t" + os.fsencode(path) + b"\0"
        for path, entry in sorted(sides.items())
    )
    with tempfile.TemporaryDirectory(prefix="devkit-merge-") as scratch:
        index = str(Path(scratch) / "index")
        run_git(base, "read-tree", tree, index=index)
        run_git(base, "update-index", "-z", "--index-info", input=lines, index=index)
        return run_git_text(base, "write-tree", index=index)


def _merge_tree(base: Path, target: str, source: str, settle: ConflictSettler | None = None) -> str:
    if git_version(base) < MERGE_TREE_VERSION:
        raise GitUnsupportedError(
            "merging an advanced target needs git merge-tree --write-tree (Git 2.38 or later); nothing was changed"
        )
    returncode, output = _merge_tree_output(base, target, source)
    records = output.split(b"\0")
    tree = records[0].decode().strip()
    if returncode == 0:
        return tree
    conflicts = _conflicts(records[1:])
    if settle is None or not conflicts:
        raise MergeConflictError(
            "the target's later commits conflict with the task branch; nothing was changed on the target"
        )
    sides = settle(tuple(sorted(conflicts)))
    unsettled = [path for path in sorted(conflicts) if sides.get(path) not in SIDES]
    if unsettled:
        raise MergeConflictError(
            f"the target's later commits conflict with the task branch in {len(unsettled)} file(s) left unsettled;"
            " nothing was changed on the target",
            *unsettled,
        )
    return _seeded_tree(
        base, tree, {path: stages.get(2 if sides[path] == "ours" else 3) for path, stages in conflicts.items()}
    )


def _committer(base: Path, commit: str) -> tuple[int, bytes]:
    """The committer timestamp and the verbatim committer identity (name, email, raw date and offset) of ``commit``."""
    header = run_git(base, "cat-file", "commit", commit).split(b"\n\n", 1)[0]
    for line in header.split(b"\n"):
        if line.startswith(b"committer "):
            ident = line.removeprefix(b"committer ")
            parts = ident.rsplit(b" ", 2)
            try:
                return int(parts[-2]), ident
            except (IndexError, ValueError):
                break
    raise MergeFailedError(f"commit {commit[:12]} has no readable committer line; nothing was changed on the target")


def _prospective_commit(base: Path, tree: str, target: str, source: str, message: str) -> str:
    """Write an unsigned, UTF-8 merge commit object that depends only on its tree, parents and message.

    Author and committer copy the committer line of the parent with the later committer date (the target on a tie), so
    neither Git identity, ``TZ`` nor ``i18n.commitEncoding`` changes its id.
    """
    _, ident = max(_committer(base, target), _committer(base, source), key=lambda item: item[0])
    raw = (
        f"tree {tree}\nparent {target}\nparent {source}\n".encode()
        + b"author "
        + ident
        + b"\ncommitter "
        + ident
        + b"\n\n"
        + message.encode()
        + b"\n"
    )
    try:
        return run_git_text(base, "hash-object", "-t", "commit", "-w", "--stdin", input=raw)
    except GitError as exc:
        raise MergeFailedError(
            f"writing the prospective merge commit failed; nothing was changed on the target: {exc.stderr or exc.message}"
        ) from exc


def build_result(
    base: Path,
    *,
    branch: str,
    target_branch: str,
    target: str,
    source: str,
    method: str,
    advance: bool = False,
    prospective: bool = False,
    settle: ConflictSettler | None = None,
) -> str:
    """Build the commit that lands ``source`` onto ``target`` and return its id; no ref or checkout changes.

    ``"ff-only"`` returns ``source`` when it contains ``target``, else ``WORKTREE_MERGE_NOT_FF``. ``"no-ff"`` commits
    the source tree with parents ``target`` and ``source`` when the source contains the target; otherwise, only with
    ``advance`` (an approved integration absorbing later target commits), it merges the trees with
    ``git merge-tree --write-tree`` (``WORKTREE_GIT_UNSUPPORTED`` below Git 2.38, ``WORKTREE_MERGE_CONFLICT`` on a
    conflict) and commits that. With ``settle`` a conflicted merge asks it which side each conflicted path keeps
    (``ConflictSettler``) and commits that tree instead of refusing; without one, every conflict refuses. ``git commit-tree`` uses the configured identity, signs (``-S``, with
    ``user.signingKey`` and ``gpg.*``) when ``commit.gpgSign`` is on, since the plumbing command ignores that setting
    itself, and is bounded by ``COMMIT_TIMEOUT`` (``WORKTREE_COMMIT_FAILED``). With ``prospective`` (local
    preparation, which checks a result before the confirmation) a ``"no-ff"`` build writes the deterministic unsigned
    commit of ``_prospective_commit`` instead, so two preparations of one source and target build one commit. A refused
    or failed build leaves at most an unreferenced object.
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
        tree = run_git_text(base, "rev-parse", "--verify", f"{source}^{{tree}}")
    elif advance:
        tree = _merge_tree(base, target, source, settle)
    else:
        raise MergeNotFastForwardError(
            f"{branch} does not contain {target_branch} at {target[:12]}; nothing was changed"
        )
    if prospective:
        return _prospective_commit(base, tree, target, source, merge_message(branch, target_branch))
    try:
        return run_git_text(
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
