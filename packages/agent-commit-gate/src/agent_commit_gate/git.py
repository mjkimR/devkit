"""The few Git queries the gate system needs."""

from __future__ import annotations

import subprocess
from pathlib import Path

from agent_advisory import AdvisoryError, Retry


class GitError(AdvisoryError):
    code = "GATE_GIT_FAILED"
    retry = Retry.AFTER_FIX


def _git(cwd: Path, *args: str) -> str:
    try:
        completed = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=False)
    except OSError as exc:
        raise GitError(f"git is not available: {exc}") from exc
    if completed.returncode != 0:
        raise GitError(f"git {args[0]} failed in {cwd}: {completed.stderr.strip() or completed.returncode}")
    return completed.stdout.strip()


def repo_root(cwd: Path) -> Path:
    return Path(_git(cwd, "rev-parse", "--show-toplevel")).resolve()


def common_git_dir(cwd: Path) -> Path:
    """The git dir shared by every worktree, so all checkouts of a repository read the same local config."""
    return Path(_git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()


def hooks_dir(cwd: Path) -> Path:
    return Path(_git(cwd, "rev-parse", "--path-format=absolute", "--git-path", "hooks")).resolve()


def config_value(cwd: Path, key: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(cwd), "config", "--get", key], capture_output=True, text=True, check=False
    )
    return completed.stdout.strip() or None if completed.returncode == 0 else None
