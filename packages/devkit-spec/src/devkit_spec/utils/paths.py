"""Literal workspace-relative path normalization and comparison."""

from __future__ import annotations

import posixpath
from pathlib import Path

from devkit_core.base.errors import ArgumentError

from devkit_spec.base.errors import EntrypointsPathError

ROOT = "."

_FORBIDDEN = frozenset("\\:*?[]\x00\r\n")


def normalize(value: str) -> str:
    """``value`` in normalized form; ``EntrypointsPathError`` when it is not a literal workspace-relative path."""
    if not value.strip() or value.startswith("/") or any(char in _FORBIDDEN for char in value):
        raise EntrypointsPathError(
            f"invalid entrypoint {value!r}: use a literal workspace-relative path", target_files=[value]
        )
    if ".." in value.split("/"):
        raise EntrypointsPathError(f"invalid entrypoint {value!r}: parent traversal is forbidden", target_files=[value])
    return posixpath.normpath(value)


def covers(ancestor: str, path: str) -> bool:
    """Whether the normalized ``ancestor`` is ``path`` itself or a directory containing it."""
    return ancestor in (ROOT, path) or path.startswith(f"{ancestor}/")


def overlaps(first: str, second: str) -> bool:
    """Whether two entrypoint values name the same path or one contains the other; invalid values never overlap."""
    try:
        a, b = normalize(first), normalize(second)
    except EntrypointsPathError:
        return False
    return covers(a, b) or covers(b, a)


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
