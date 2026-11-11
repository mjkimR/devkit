"""Literal workspace-relative path normalization and comparison."""

from __future__ import annotations

import posixpath

from devkit_docs.base.errors import EntrypointsPathError

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
