"""Workspace-relative command argument paths."""

import posixpath
from pathlib import Path

from devkit_core.base.errors import ArgumentError


def _bundle_dir(root: Path, value: str) -> str:
    """The workspace-relative form of ``--spec`` (absolute, or relative to the workspace root)."""
    path = Path(value)
    absolute = path.resolve() if path.is_absolute() else Path(posixpath.normpath((root / path).as_posix()))
    try:
        relative = absolute.relative_to(root).as_posix()
    except ValueError:
        relative = ""
    if not relative or relative == ".":
        raise ArgumentError(
            f"--spec {value}: not a directory inside the workspace",
            target_files=["--spec"],
            fix="Pass the bundle directory relative to the workspace root: specs/<YYYY-MM>/<YYYYMMDD>-<slug>",
        )
    return relative
