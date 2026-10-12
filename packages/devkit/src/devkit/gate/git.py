"""The Git queries the gate system needs, built on ``devkit.core.git.run_git``.

``GateGitError`` is the advisory form of ``devkit.core.GitError``: every query
here maps a failed Git call to it, so the CLI boundary renders one error code.
"""

from __future__ import annotations

import os
from pathlib import Path

from devkit.advisory import Actor, AdvisoryError, Retry
from devkit.core import GitError, run_git

_TIMEOUT = 30.0


class GateGitError(AdvisoryError):
    code = "GATE_GIT_FAILED"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


def _git(cwd: Path, *args: str) -> str:
    try:
        output = run_git(cwd, *args, timeout=_TIMEOUT)
    except GitError as exc:
        raise GateGitError(str(exc)) from exc
    return os.fsdecode(output.rstrip(b"\n"))


def _path(cwd: Path, *args: str) -> Path:
    return Path(_git(cwd, *args)).resolve()


def repo_root(cwd: Path) -> Path:
    """The top level of the work tree containing ``cwd``: where Git runs hooks and gates read the project."""
    try:
        return _path(cwd, "rev-parse", "--show-toplevel")
    except GateGitError as exc:
        raise GateGitError(
            f"{cwd} is not inside a Git work tree: {exc.message}",
            input_error=True,
            target_files=[str(cwd)],
            fix="Pass --workspace-root/-w a directory inside the repository",
        ) from exc


def git_dir(cwd: Path) -> Path:
    """The git dir of the current worktree (``.git/worktrees/<name>`` in a linked worktree)."""
    return _path(cwd, "rev-parse", "--absolute-git-dir")


def common_git_dir(cwd: Path) -> Path:
    """The git dir shared by every worktree, so all checkouts of a repository read the same local config."""
    return _path(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")


def config_value(cwd: Path, key: str) -> str | None:
    """The effective value of a Git config key, or ``None`` when it is unset."""
    try:
        output = run_git(cwd, "config", "--get", key, timeout=_TIMEOUT)
    except GitError as exc:
        if exc.returncode == 1:  # the key is not set
            return None
        raise GateGitError(str(exc)) from exc
    value = os.fsdecode(output).strip()
    return value or None
