"""Workspace-relative POSIX paths that cannot escape their root.

Paths recorded in devkit files (the installation receipt, bundle manifests,
configuration) and paths read from Git are POSIX paths relative to a workspace
root. ``normalize_relpath`` is the single validator for them:

- empty or whitespace-only, ``.`` (after normalization) and values containing
  a NUL character are rejected;
- absolute paths (``/x``) and any ``..`` segment are rejected;
- a backslash is an ordinary file-name character on POSIX and is accepted,
  but a value that would escape its root if backslashes were read as
  separators (``\\x``, ``..\\x``, ``a\\..\\b``) or that starts with a Windows
  drive (``C:``) is rejected, so a recorded value never reads as an escape;
- redundant separators and ``.`` segments are normalized away (``a//./b`` is
  ``a/b``); ``canonical=True`` rejects such values instead.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from devkit.core.errors import UnsafePathError

_DRIVE = re.compile(r"[A-Za-z]:")


def normalize_relpath(value: str, *, canonical: bool = False) -> PurePosixPath:
    """Validate a workspace-relative POSIX path and return it normalized.

    Raises ``UnsafePathError`` for the values listed in the module docstring.
    With ``canonical=True`` the value must already be in normalized form
    (``str(result) == value``), as paths written by devkit always are.
    """
    if not isinstance(value, str):
        raise UnsafePathError(f"path must be a string, not {type(value).__name__}")
    if not value.strip():
        raise UnsafePathError("path is empty")
    if "\0" in value:
        raise UnsafePathError(f"path contains a NUL character: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise UnsafePathError(f"path must be relative: {value}")
    if ".." in path.parts:
        raise UnsafePathError(f"path must not contain '..': {value}")
    if "\\" in value:
        as_windows = value.replace("\\", "/")
        if as_windows.startswith("/") or ".." in PurePosixPath(as_windows).parts:
            raise UnsafePathError(f"path escapes its root when backslashes are separators: {value}")
    if _DRIVE.match(value):
        raise UnsafePathError(f"path must not start with a drive: {value}")
    if str(path) == ".":
        raise UnsafePathError(f"path names the root itself: {value}")
    if canonical and str(path) != value:
        raise UnsafePathError(f"path is not in canonical form (expected {path}): {value}")
    return path


def is_safe_relpath(value: object, *, canonical: bool = False) -> bool:
    """Whether ``normalize_relpath`` accepts ``value``."""
    try:
        normalize_relpath(value, canonical=canonical)  # type: ignore[arg-type]
    except UnsafePathError:
        return False
    return True


def resolve_within(root: Path, rel: str | PurePosixPath) -> Path:
    """Resolve ``rel`` under ``root``, following symlinks, and refuse results outside ``root``.

    ``rel`` is validated with ``normalize_relpath`` first. The returned path is
    fully resolved (symlinks followed; components that do not exist yet are
    kept as given). Raises ``UnsafePathError`` when the resolved path is not
    ``root`` itself or inside it, as when a symlink points elsewhere.
    """
    relative = normalize_relpath(rel if isinstance(rel, str) else rel.as_posix())
    base = root.resolve()
    resolved = base.joinpath(*relative.parts).resolve()
    if not resolved.is_relative_to(base):
        raise UnsafePathError(f"path resolves outside {base}: {relative}")
    return resolved
