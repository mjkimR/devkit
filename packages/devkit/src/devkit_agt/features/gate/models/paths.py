"""Stable project-relative display paths."""

from pathlib import Path


def display_path(path: Path, root: Path | None) -> str:
    """``path`` relative to ``root`` (POSIX separators) when it lies inside it, else as it is."""
    return path.relative_to(root).as_posix() if root is not None and path.is_relative_to(root) else str(path)
