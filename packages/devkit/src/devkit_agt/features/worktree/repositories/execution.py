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


def remove(base: Path, checkout: Path, sha: str, run_id: str, lock_fd: int | None = None) -> str:
    """Remove only a registered clean detached checkout with this exact ownership."""
    entries = git(base, "worktree", "list", "--porcelain").split("\n\n")
    entry = next((e for e in entries if e.splitlines()[0] == f"worktree {checkout}"), None)
    if entry is None:
        if not checkout.exists() and not checkout.is_symlink():
            return "already_clean"
        raise ValueError("unrelated execution checkout")
    common = git(base, "rev-parse", "--path-format=absolute", "--git-common-dir")
    expected = {"run_id": run_id, "sha": sha, "checkout": str(checkout), "common": common}
    if not checkout.exists() and not checkout.is_symlink():
        # An interrupted removal may have removed the directory before retiring
        # its exact registration. Never prune unrelated worktrees.
        markers = list((Path(common) / "worktrees").glob("*/devkit-execution.json"))
        owned = [p for p in markers if json.loads(p.read_text()) == expected]
        if len(owned) != 1 or (owned[0].parent / "gitdir").read_text().strip() != str(checkout / ".git"):
            raise ValueError("missing checkout ownership cannot be revalidated")
        if f"HEAD {sha}" not in entry.splitlines() or "detached" not in entry.splitlines():
            raise ValueError("missing checkout registration differs")
        _remove_checkout(base, checkout, lock_fd, missing=True)
        return "cleaned"
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
    _remove_checkout(base, checkout, lock_fd, missing=False)
    return "cleaned"


def _remove_checkout(base: Path, checkout: Path, lock_fd: int | None, *, missing: bool) -> None:
    # The native remover inherits the cleanup lock so parent death cannot let a
    # second cleaner race removal. Only an absent, owned path permits --force.
    argv = ["git", "-C", str(base), "worktree", "remove"]
    if missing:
        argv.append("--force")
    argv.append(str(checkout))
    process = subprocess.Popen(
        argv,
        env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        pass_fds=() if lock_fd is None else (lock_fd,),
    )
    try:
        stdout, stderr = process.communicate()
    except BaseException:
        # Settle the already-started effect before releasing the caller's lock.
        while True:
            try:
                process.communicate()
                break
            except KeyboardInterrupt:
                continue
        raise
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, argv, stdout, stderr)


if __name__ == "__main__":
    create(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4])
