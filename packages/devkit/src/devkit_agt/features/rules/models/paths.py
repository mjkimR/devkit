"""Workspace-relative display paths."""

from __future__ import annotations

from pathlib import Path


def display_path(path: Path | None, workspace_root: Path) -> str | None:
    """``path`` relative to the workspace when it lies inside it, else absolute."""
    if path is None:
        return None
    try:
        return path.relative_to(workspace_root).as_posix()
    except ValueError:
        return str(path)
