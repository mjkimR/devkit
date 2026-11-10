"""Resolve the command's Git worktree without requiring adaptive approach selection."""

from pathlib import Path

from devkit_dist.features.project.repositories.project import git_toplevel

from devkit_adaptive.base.errors import RepositoryUnsupported


def repository(root: Path) -> Path:
    found = git_toplevel(root)
    if found is None:
        raise RepositoryUnsupported(f"workspace root is not a Git worktree: {root}")
    return found.resolve()
