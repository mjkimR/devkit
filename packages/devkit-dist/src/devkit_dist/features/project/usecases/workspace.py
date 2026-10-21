"""Resolve the project workspace used by a command adapter."""

from pathlib import Path

from devkit_dist.features.project.repositories import project


def find_project_root(start: Path) -> Path:
    return project.find_project_root(start)


def require_devkit_root(root: Path, param: str = "--workspace-root") -> Path:
    return project.require_devkit_root(root, param)


def require_git_toplevel(start: Path) -> Path:
    return project.require_git_toplevel(start)
