"""The Git queries the gate system needs, built on ``devkit.core.git.run_git``.

A failed Git call raises ``devkit.core.GitError`` (``GIT_FAILED``) as it is.
The repository root is ``devkit.core.require_git_toplevel``, whose error is an
input error naming ``--workspace-root``.
"""

from __future__ import annotations

import os
from pathlib import Path

from devkit.core import GitError, run_git


def _git(cwd: Path, *args: str) -> str:
    return os.fsdecode(run_git(cwd, *args).rstrip(b"\n"))


def _path(cwd: Path, *args: str) -> Path:
    return Path(_git(cwd, *args)).resolve()


def git_dir(cwd: Path) -> Path:
    """The git dir of the current worktree (``.git/worktrees/<name>`` in a linked worktree)."""
    return _path(cwd, "rev-parse", "--absolute-git-dir")


def common_git_dir(cwd: Path) -> Path:
    """The git dir shared by every worktree, so all checkouts of a repository read the same local config."""
    return _path(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")


def config_value(cwd: Path, key: str) -> str | None:
    """The effective value of a Git config key, or ``None`` when it is unset."""
    try:
        output = run_git(cwd, "config", "--get", key)
    except GitError as exc:
        if exc.returncode == 1:  # the key is not set
            return None
        raise
    value = os.fsdecode(output).strip()
    return value or None


def config_scope(cwd: Path, key: str) -> str | None:
    """The scope (``local``, ``worktree``, ``global``, ``system``, ``command``) of a key's effective value."""
    try:
        output = run_git(cwd, "config", "--show-scope", "--get", key)
    except GitError as exc:
        if exc.returncode == 1:  # the key is not set
            return None
        raise
    scope, _, _ = os.fsdecode(output).partition("\t")
    return scope or None
