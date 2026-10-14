"""Atomic file replacement: a reader sees the old content or the new, never a partial write.

POSIX only (directory ``fsync``). The data goes to a temporary file in the
target's directory, is flushed to disk, takes its permission bits, and then
replaces the target with ``os.replace``; the directory is synced so the rename
survives a crash. An interrupted or failed write leaves the target as it was
and removes the temporary file. A symlink at ``path`` is replaced by the new
file, never written through: a caller that means the link's target resolves
the path first (and confines it, ``devkit.core.resolve_within``).
"""

from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path

DEFAULT_MODE = 0o644


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write_bytes(path: Path, data: bytes, *, mode: int | None = None) -> None:
    """Replace the file at ``path`` with ``data`` atomically, creating missing parent directories.

    ``mode`` sets the permission bits; ``None`` keeps those of the regular file
    at ``path``, or ``0o644`` when there is none. Raises ``OSError`` when the
    file cannot be written; the target is then unchanged.
    """
    if mode is None:
        try:
            current = path.lstat()
        except FileNotFoundError:
            current = None
        mode = stat.S_IMODE(current.st_mode) if current is not None and stat.S_ISREG(current.st_mode) else DEFAULT_MODE
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.devkit-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    _fsync_directory(path.parent)


def atomic_write_text(path: Path, text: str, *, mode: int | None = None) -> None:
    """``atomic_write_bytes`` of ``text`` encoded as UTF-8, exactly (no newline translation)."""
    atomic_write_bytes(path, text.encode("utf-8"), mode=mode)
