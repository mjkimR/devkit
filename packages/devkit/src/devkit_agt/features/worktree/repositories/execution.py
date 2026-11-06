"""Execution-only detached checkout ownership; also captured by the execution supervisor.

Standard library only: this file can run outside an installed project environment.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def configured_setup(root: Path) -> str | None:
    """Reuse worktree setup policy; only the launch caller loads project packages."""
    from devkit_dist.features.project.repositories.project import find_project_root

    from devkit_agt.features.worktree.repositories.config import read_worktree_config

    return read_worktree_config(find_project_root(root)).setup


def git(base: Path, *args: str) -> str:
    """Run Git without inherited repository overrides."""
    result = subprocess.run(
        ["git", "-C", str(base), *args],
        env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def create(base: Path, checkout: Path, sha: str, run_id: str) -> None:
    """Prepare one unique detached checkout without activity lifecycle effects."""
    if checkout.exists() or checkout.is_symlink():
        raise ValueError("execution checkout path already exists")
    git(base, "worktree", "add", "--detach", str(checkout), sha)
    git_dir = Path(git(checkout, "rev-parse", "--absolute-git-dir"))
    (git_dir / "devkit-execution.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "sha": sha,
                "checkout": str(checkout),
                "common": git(base, "rev-parse", "--path-format=absolute", "--git-common-dir"),
            }
        )
    )


def remove(base: Path, checkout: Path, sha: str, run_id: str) -> str:
    """Remove only a registered clean detached checkout with this exact ownership."""
    entries = git(base, "worktree", "list", "--porcelain").split("\n\n")
    entry = next((e for e in entries if e.splitlines()[0] == f"worktree {checkout}"), None)
    if entry is None:
        if not checkout.exists() and not checkout.is_symlink():
            return "already_clean"
        raise ValueError("unrelated execution checkout")
    if checkout.is_symlink() or not checkout.is_dir() or "detached" not in entry.splitlines():
        raise ValueError("execution checkout identity differs")
    if git(checkout, "rev-parse", "HEAD") != sha:
        raise ValueError("execution checkout SHA differs")
    common = git(base, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if git(checkout, "rev-parse", "--path-format=absolute", "--git-common-dir") != common:
        raise ValueError("execution checkout repository differs")
    git_dir = Path(git(checkout, "rev-parse", "--absolute-git-dir"))
    expected = {"run_id": run_id, "sha": sha, "checkout": str(checkout), "common": common}
    if json.loads((git_dir / "devkit-execution.json").read_text()) != expected:
        raise ValueError("execution checkout ownership differs")
    if git(checkout, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("execution checkout is dirty")
    git(base, "worktree", "remove", str(checkout))
    return "cleaned"


if __name__ == "__main__":
    create(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4])
