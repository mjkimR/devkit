"""Capture source bytes from a fixed Git pair, never from an unstaged snapshot side."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devkit_core.core import GitError, run_git

from devkit_agt.features.rules.models.snapshot import Snapshot
from devkit_agt.features.rules.repositories.workspace.cache import WorkspaceCache


@dataclass(frozen=True)
class CapturedChange:
    path: str
    before: bytes
    after: bytes
    status: str
    available: bool = True


@dataclass(frozen=True)
class CapturedChanges:
    mode: str
    base: str
    files: tuple[CapturedChange, ...]
    available: bool = True


def _tree(root: Path, ref: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in run_git(root, "ls-tree", "-r", "-z", ref).split(b"\0"):
        if not line:
            continue
        meta, name = line.split(b"\t", 1)
        mode, _kind, sha = meta.decode().split()
        if mode in ("100644", "100755"):
            entries[name.decode("utf-8", errors="surrogateescape")] = sha
    return entries


def _blob(root: Path, sha: str | None) -> bytes:
    return run_git(root, "cat-file", "blob", sha) if sha is not None else b""


def capture_changes(
    root: Path,
    cache: WorkspaceCache,
    *,
    snapshot: Snapshot | None = None,
    base: str | None = None,
    explicit: tuple[str, ...] = (),
) -> CapturedChanges:
    """Working after bytes come through the run cache and are checked against disk again for races."""
    mode = snapshot.mode if snapshot is not None else "working"
    git_root = snapshot.root if snapshot is not None else root
    try:
        if snapshot is not None:
            base = snapshot.base
        elif base is None:
            # Distinguish an unborn repository from a broken/unreadable HEAD.
            run_git(git_root, "rev-parse", "--git-dir")
            try:
                base = run_git(git_root, "rev-parse", "--verify", "HEAD^{tree}").decode().strip()
            except GitError:
                ref = run_git(git_root, "symbolic-ref", "-q", "HEAD").decode().strip()
                if run_git(git_root, "for-each-ref", "--format=%(refname)", ref).strip():
                    raise
                base = run_git(git_root, "hash-object", "-t", "tree", "--stdin", input=b"").decode().strip()
        prior = _tree(git_root, base)
        if snapshot is not None:
            current = {p: sha for p, sha, m in snapshot.files if m in ("100644", "100755")}
            touched = set(snapshot.changed) | set(snapshot.deleted)
            names = touched | set(explicit)
        else:
            changed = run_git(
                git_root, "diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", "-z", base, "--"
            )
            extra = run_git(git_root, "ls-files", "--others", "--exclude-standard", "-z")
            names = {p.decode("utf-8", errors="surrogateescape") for p in (changed + extra).split(b"\0") if p}
            touched = set(names)
            names.update(explicit)
            current = {}
        files: list[CapturedChange] = []
        for name in sorted(names):
            try:
                old = _blob(git_root, prior.get(name))
                if snapshot is not None:
                    exists = name in current
                    new = _blob(git_root, current.get(name))
                else:
                    path = root / name
                    exists = path.is_file() and not path.is_symlink()
                    new = cache.read_bytes(name) if exists else b""
                    if exists and path.read_bytes() != new:
                        raise ValueError("content changed during capture")
                status = (
                    "added"
                    if name not in prior
                    else "deleted"
                    if not exists
                    else "modified"
                    if old != new or name in touched
                    else "unchanged"
                )
                files.append(CapturedChange(name, old, new, status))
            except (GitError, OSError, ValueError):
                files.append(CapturedChange(name, b"", b"", "unavailable", False))
        return CapturedChanges(mode, base, tuple(files))
    except (GitError, OSError, ValueError):
        return CapturedChanges(mode, base or "", (), False)
