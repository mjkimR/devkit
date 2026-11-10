"""Capture Git content with a disposable index; never mutate checkout refs or index."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from devkit_core.core.git import parse_status_records

from ..models.errors import SnapshotFailed
from ..models.records import digest


def git(root: Path, *args: str, index: str | None = None) -> bytes:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    if index:
        env["GIT_INDEX_FILE"] = index
    result = subprocess.run(["git", "-C", str(root), *args], env=env, capture_output=True, check=False)
    if result.returncode:
        raise SnapshotFailed("Cannot capture inspected Git content", f"git {args[0]} exited {result.returncode}")
    return result.stdout


def capture(root: Path, excluded: list[str]) -> tuple[dict[str, Any], bytes | None]:
    paths = ["--", ".", *(f":(top,literal,exclude){p}" for p in excluded)]
    source = git(root, "rev-parse", "HEAD").decode().strip()
    status = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all", *paths)
    dirty_paths = [record.path for record in parse_status_records(status)]
    if not dirty_paths:
        return {
            "source_sha": source,
            "dirty": False,
            "dirty_paths": [],
            "inspected_tree": git(root, "rev-parse", "HEAD^{tree}").decode().strip(),
            "diff_digest": None,
            "diff_path": None,
        }, None
    git_dir = Path(os.fsdecode(git(root, "rev-parse", "--absolute-git-dir")).strip())
    descriptor, name = tempfile.mkstemp(prefix="devkit-history-index-", dir=git_dir)
    os.close(descriptor)
    Path(name).unlink()
    try:
        git(root, "read-tree", "HEAD", index=name)
        git(root, "add", "-A", *paths, index=name)
        tree = git(root, "write-tree", index=name).decode().strip()
    finally:
        Path(name).unlink(missing_ok=True)
        Path(name + ".lock").unlink(missing_ok=True)
    diff = git(
        root,
        "-c",
        "diff.noprefix=false",
        "-c",
        "core.quotepath=false",
        "diff",
        "--no-ext-diff",
        "--no-textconv",
        "--no-renames",
        "--no-color",
        "--binary",
        "HEAD",
        *paths,
    )
    untracked = git(root, "ls-files", "--others", "--exclude-standard", "-z", *paths)
    try:
        for rel in sorted(p for p in untracked.split(b"\0") if p):
            path = root / os.fsdecode(rel)
            data = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()
            diff += len(rel).to_bytes(8, "big") + rel + len(data).to_bytes(8, "big") + data
    except OSError as exc:
        raise SnapshotFailed("Cannot retain inspected untracked content", type(exc).__name__) from exc
    return {
        "source_sha": source,
        "dirty": True,
        "dirty_paths": sorted(dirty_paths),
        "inspected_tree": tree,
        "diff_digest": digest(diff),
        "diff_path": "inspected.diff",
    }, diff
