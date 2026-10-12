"""Exact Git trees for gate evaluation.

``devkit rules check --staged`` evaluates the index (what a commit would
contain) and ``--ci --base <ref>`` evaluates ``HEAD`` against its merge base
with ``<ref>``. Both read the tree from Git rather than the working directory,
so unstaged edits, ignored files and local-only configuration cannot change the
result. The tree is materialized into a temporary directory, which becomes the
workspace root for the run: ``.devkit/config.toml``, the installation receipt
and synchronized rules are therefore taken from the same snapshot. Managed rule
copies are usually Git-ignored and absent from the tree; the rule engine then
reads them from the working tree only when they match the hash recorded in the
snapshot's receipt (see ``engine.discovery``).

The snapshot root must be the top level of the Git work tree: Git reports tree
and diff paths relative to it, and a snapshot of a subdirectory would silently
check nothing.

Materialization writes regular and executable files, recreates symlinks whose
target stays inside the tree (others are skipped) and creates an empty
directory for each submodule, so a link to a tracked symlink or into a
submodule resolves as it does in the working tree. Only regular files are
evaluation targets.
"""

from __future__ import annotations

import os
import posixpath
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from devkit.core import GitError, is_safe_relpath, run_git

REGULAR_MODES = {"100644", "100755"}
SYMLINK_MODE = "120000"
GITLINK_MODE = "160000"


class SnapshotError(RuntimeError):
    """Git is unavailable, the directory is not a repository top level, or a ref cannot be resolved."""


@dataclass(frozen=True)
class Snapshot:
    root: Path
    mode: str  # "staged" or "ci"
    tree: str
    base: str
    changed: tuple[str, ...]  # changed regular files present in ``tree``
    deleted: tuple[str, ...]
    files: tuple[tuple[str, str, str], ...]  # (path, object sha, mode) of every regular file, symlink and submodule

    def describe(self) -> str:
        return (
            f"[SNAPSHOT: mode={self.mode} tree={self.tree[:12]} base={self.base[:12]} "
            f"changed={len(self.changed)} deleted={len(self.deleted)}]"
        )


def _git(root: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        return run_git(root, *args, input=stdin)
    except GitError as exc:
        raise SnapshotError(str(exc)) from exc


def _decode(name: bytes) -> str:
    return name.decode("utf-8", errors="surrogateescape")


def _require_toplevel(root: Path) -> None:
    try:
        toplevel_raw = _git(root, "rev-parse", "--show-toplevel").rstrip(b"\n")
    except SnapshotError as exc:
        raise SnapshotError(f"{root} is not inside a Git work tree ({exc})") from exc
    toplevel = Path(os.fsdecode(toplevel_raw)).resolve()
    if toplevel != root:
        raise SnapshotError(
            f"a Git snapshot must be taken at the work tree top level {toplevel}, not {root}; "
            f"run from the repository root or pass --workspace-root {toplevel}"
        )


def _changes(root: Path, prior: str, tree: str) -> tuple[list[str], list[str]]:
    """Changed and deleted paths between two trees, from one ``--name-status`` diff."""
    output = _git(root, "diff", "--name-status", "-z", "--no-renames", prior, tree, "--")
    parts = [part for part in output.split(b"\0") if part]
    changed: list[str] = []
    deleted: list[str] = []
    for status, name in zip(parts[0::2], parts[1::2], strict=True):
        path = _decode(name)
        changed.append(path)
        if status.startswith(b"D"):
            deleted.append(path)
    return changed, deleted


def git_snapshot(root: Path, *, staged: bool, base: str = "origin/main") -> Snapshot:
    """Capture the staged index or the ``HEAD`` tree with its merge base against ``base``.

    ``root`` must be the top level of the Git work tree.
    """
    root = root.resolve()
    _require_toplevel(root)
    if staged:
        tree = _git(root, "write-tree").decode().strip()
        try:
            prior = _git(root, "rev-parse", "--verify", "--quiet", "HEAD^{tree}").decode().strip()
        except SnapshotError:
            # Unborn branch: compare against the empty tree.
            prior = _git(root, "hash-object", "-t", "tree", "--stdin", stdin=b"").decode().strip()
        mode = "staged"
    else:
        tree = _git(root, "rev-parse", "--verify", "--quiet", "HEAD^{tree}").decode().strip()
        prior = _git(root, "merge-base", "--", base, "HEAD").decode().strip()
        mode = "ci"
    changed, deleted = _changes(root, prior, tree)
    files: list[tuple[str, str, str]] = []
    regular: set[str] = set()
    for entry in _git(root, "ls-tree", "-r", "--full-tree", "-z", tree).split(b"\0"):
        if not entry:
            continue
        meta, _, path = entry.partition(b"\t")
        file_mode, _kind, sha = meta.decode().split(" ")
        name = _decode(path)
        if file_mode not in REGULAR_MODES | {SYMLINK_MODE, GITLINK_MODE} or not is_safe_relpath(name, canonical=True):
            continue
        files.append((name, sha, file_mode))
        if file_mode in REGULAR_MODES:
            regular.add(name)
    return Snapshot(
        root=root,
        mode=mode,
        tree=tree,
        base=prior,
        changed=tuple(p for p in changed if p in regular),
        deleted=tuple(deleted),
        files=tuple(files),
    )


def _inside_tree(name: str, link_target: str) -> bool:
    """Whether a symlink at ``name`` pointing to ``link_target`` resolves inside the tree, lexically."""
    if not link_target or link_target.startswith("/") or "\0" in link_target:
        return False
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(name), link_target))
    return joined != ".." and not joined.startswith("../") and joined != "."


def _target(directory: Path, name: str) -> Path:
    target = directory / Path(*PurePosixPath(name).parts)
    if target.exists() or target.is_symlink():
        raise SnapshotError(
            f"cannot materialize {name}: another path in the tree has the same name on this file system "
            "(paths that differ only by case)"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def materialize(snapshot: Snapshot, directory: Path) -> None:
    """Write the snapshot's files, in-tree symlinks and submodule placeholders under ``directory``."""
    blobs = [(name, sha, mode) for name, sha, mode in snapshot.files if mode != GITLINK_MODE]
    for name, _, mode in snapshot.files:
        if mode == GITLINK_MODE:
            _target(directory, name).mkdir()
    if not blobs:
        return
    request = "".join(f"{sha}\n" for _, sha, _ in blobs).encode()
    output = _git(snapshot.root, "cat-file", "--batch", stdin=request)
    offset = 0
    links: list[tuple[str, str]] = []
    for name, sha, file_mode in blobs:
        newline = output.index(b"\n", offset)
        header = output[offset:newline].decode().split(" ")
        if len(header) != 3 or header[0] != sha or header[1] != "blob":
            raise SnapshotError(f"unexpected cat-file output for {name}")
        size = int(header[2])
        start = newline + 1
        data = output[start : start + size]
        offset = start + size + 1
        if file_mode == SYMLINK_MODE:
            links.append((name, os.fsdecode(data)))
            continue
        target = _target(directory, name)
        target.write_bytes(data)
        if file_mode == "100755":
            target.chmod(0o755)
    # Symlinks last, so a link never redirects where a later regular file is written.
    for name, link_target in links:
        if _inside_tree(name, link_target):
            _target(directory, name).symlink_to(link_target)
