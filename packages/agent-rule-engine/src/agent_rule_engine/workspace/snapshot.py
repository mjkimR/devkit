"""Exact Git trees for gate evaluation.

``agent-rules check --staged`` evaluates the index (what a commit would
contain) and ``--ci --base <ref>`` evaluates ``HEAD`` against its merge base
with ``<ref>``. Both read the tree from Git rather than the working directory,
so unstaged edits, ignored files and local-only configuration cannot change the
result. The tree is materialized into a temporary directory, which becomes the
workspace root for the run: ``.devkit/config.toml``, the installation receipt
and synchronized rules are therefore taken from the same snapshot. Managed rule
copies are usually Git-ignored and absent from the tree; the CLI then reads
them from the working tree only when they match the hash recorded in the
snapshot's receipt (see ``engine.discovery``).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

BLOB_MODES = {"100644", "100755"}


class SnapshotError(RuntimeError):
    """Git is unavailable, the directory is not a repository, or a ref cannot be resolved."""


@dataclass(frozen=True)
class Snapshot:
    root: Path
    mode: str  # "staged" or "ci"
    tree: str
    base: str
    changed: tuple[str, ...]  # changed paths present in ``tree``
    deleted: tuple[str, ...]
    files: tuple[tuple[str, str, str], ...]  # (path, blob sha, mode) of every regular file

    def describe(self) -> str:
        return (
            f"[SNAPSHOT: mode={self.mode} tree={self.tree[:12]} base={self.base[:12]} "
            f"changed={len(self.changed)} deleted={len(self.deleted)}]"
        )


def _git(root: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            input=stdin,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise SnapshotError(f"git is not available: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise SnapshotError(f"git {args[0]} failed: {detail or completed.returncode}")
    return completed.stdout


def _names(data: bytes) -> tuple[str, ...]:
    return tuple(part.decode("utf-8", errors="surrogateescape") for part in data.split(b"\0") if part)


def _safe(path: str) -> bool:
    pure = PurePosixPath(path)
    return bool(path) and not pure.is_absolute() and ".." not in pure.parts and "\\" not in path


def git_snapshot(root: Path, *, staged: bool, base: str = "origin/main") -> Snapshot:
    """Capture the staged index or the ``HEAD`` tree with its merge base against ``base``."""
    root = root.resolve()
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
    changed = _names(_git(root, "diff", "--name-only", "-z", "--no-renames", prior, tree, "--"))
    deleted = _names(_git(root, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=D", prior, tree, "--"))
    files: list[tuple[str, str, str]] = []
    for entry in _git(root, "ls-tree", "-r", "-z", tree).split(b"\0"):
        if not entry:
            continue
        meta, _, path = entry.partition(b"\t")
        file_mode, kind, sha = meta.decode().split(" ")
        name = path.decode("utf-8", errors="surrogateescape")
        if kind == "blob" and file_mode in BLOB_MODES and _safe(name):
            files.append((name, sha, file_mode))
    present = {name for name, _, _ in files}
    return Snapshot(
        root=root,
        mode=mode,
        tree=tree,
        base=prior,
        changed=tuple(p for p in changed if p in present),
        deleted=deleted,
        files=tuple(files),
    )


def materialize(snapshot: Snapshot, directory: Path) -> None:
    """Write every regular file of the snapshot under ``directory``; symlinks and submodules are skipped."""
    if not snapshot.files:
        return
    request = "".join(f"{sha}\n" for _, sha, _ in snapshot.files).encode()
    output = _git(snapshot.root, "cat-file", "--batch", stdin=request)
    offset = 0
    for name, sha, file_mode in snapshot.files:
        newline = output.index(b"\n", offset)
        header = output[offset:newline].decode().split(" ")
        if len(header) != 3 or header[0] != sha or header[1] != "blob":
            raise SnapshotError(f"unexpected cat-file output for {name}")
        size = int(header[2])
        start = newline + 1
        data = output[start : start + size]
        offset = start + size + 1
        target = directory / Path(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        if file_mode == "100755":
            target.chmod(0o755)
