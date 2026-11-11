"""Helpers shared by the files a unit's writers create: ``decisions/NN-*.yaml``, ``envelopes/<kind>-NN.yaml`` and
the anchor.

Writers serialize on an exclusive ``flock`` of the directory they write in, not on a lock file: a lock file would
sit among the records, where the loaders, ``lint-clean`` and ``new``'s leftover check would all have to skip it,
and it would outlive every writer. A directory lock leaves nothing behind and dies with its process. The wait for
it is bounded (``LOCK_TIMEOUT``, then ``LockHeldError``); a platform or file system without ``flock`` is
``LockUnsupportedError``. POSIX only, like ``devkit_core.core.file_lock``.
"""

from __future__ import annotations

import errno
import os
import re
import secrets
from collections.abc import Callable, Iterator
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Any

from devkit_core.base.errors import UnsafePathError
from devkit_core.core import LockUnsupportedError, flock_fd

# ``.<name>.<12 hex digits>.tmp``: a file being written (or left by an interrupted write) next to ``<name>``.
TEMPORARY = re.compile(r"\..+\.[0-9a-f]{12}\.tmp")
LOCK_TIMEOUT = 10.0  # seconds a writer waits for another one; each holds the lock for one small file
# ``link`` errors of a file system without hard links (SMB, exFAT, some FUSE and bind mounts).
_NO_HARD_LINKS = {errno.EPERM, errno.ENOTSUP, errno.EOPNOTSUPP, errno.EXDEV, errno.ENOSYS}


def as_text(value: Any) -> str:
    """``value`` as a string; ``None`` is ``""``."""
    return "" if value is None else str(value)


def is_temporary(name: str) -> bool:
    """Whether ``name`` is a temporary file of a write in progress (or interrupted); loaders and lint skip it."""
    return TEMPORARY.fullmatch(name) is not None


def temporary_path(path: Path) -> Path:
    """A fresh temporary file name next to ``path`` (``is_temporary`` holds for it)."""
    return path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")


def _open_directory(directory: Path) -> int:
    """A descriptor of ``directory`` itself; ``UnsafePathError`` when it is a symbolic link or not a directory."""
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        return os.open(directory, flags)
    except OSError as exc:
        if exc.errno in (errno.ELOOP, errno.ENOTDIR):
            raise UnsafePathError(
                f"{directory} is not a directory (a symbolic link or a file); records are written only into one",
                target_files=[str(directory)],
                fix=f"Replace {directory} with a plain directory",
            ) from exc
        raise


def _no_flock(directory: Path, exc: OSError) -> LockUnsupportedError:
    return LockUnsupportedError(
        f"the file system of {directory} does not support flock: {exc.strerror}",
        target_files=[str(directory)],
        fix="Keep the work unit on a local file system that supports flock",
    )


@contextmanager
def locked(directory: Path) -> Iterator[None]:
    """Hold an exclusive ``flock`` on ``directory`` itself for the block.

    The wait for another writer is bounded by ``LOCK_TIMEOUT`` seconds, then
    ``LockHeldError`` (``LOCK_HELD``). Without ``fcntl``, or on a file system that cannot lock, it raises
    ``LockUnsupportedError`` (``LOCK_UNSUPPORTED``).
    """
    fd = _open_directory(directory)
    try:
        flock_fd(fd, target=directory, timeout=LOCK_TIMEOUT, unsupported=lambda exc: _no_flock(directory, exc))
        yield
    finally:
        os.close(fd)


def _publish(temporary: Path, path: Path) -> bool:
    """Give the written ``temporary`` the name ``path`` unless that exists; the caller holds the directory lock.

    A hard link fails instead of replacing an existing file. On a file system without hard links the name is
    checked and the file renamed instead: under the directory lock no devkit writer can create ``path`` in between,
    though a file a host writes without the lock in that instant would be replaced.
    """
    try:
        os.link(temporary, path)
        return True
    except FileExistsError:
        return False
    except OSError as exc:
        if exc.errno not in _NO_HARD_LINKS:
            raise
    if os.path.lexists(path):
        return False
    os.rename(temporary, path)
    return True


def _write_new(path: Path, body: str) -> bool:
    temporary = temporary_path(path)
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        return _publish(temporary, path)
    finally:
        with suppress(FileNotFoundError):
            temporary.unlink()


def write_new_file(path: Path, body: str) -> bool:
    """Create ``path`` holding ``body`` completely or not at all; ``False`` when ``path`` already exists.

    ``body`` goes to a temporary file in the same directory first (``temporary_path``), which then takes the name
    ``path`` under the directory's lock (``locked``) without ever replacing a file, so an interrupted write leaves no
    partial ``path``. The file gets the mode a plain ``open`` would give it (``0o666`` less the umask).
    """
    with locked(path.parent):
        return _write_new(path, body)


def write_numbered(
    directory: Path,
    seq: int,
    name_for: Callable[[int], str],
    sequence_of: Callable[[str], int | None],
    body: str,
) -> tuple[Path, int]:
    """Write ``body`` as ``directory / name_for(n)`` under a sequence number ``n`` no other file holds.

    ``sequence_of`` gives the number a file name already holds in this
    numbering (``None`` for a file outside it), so the number is reserved
    itself, not only the file name: ``n`` is ``seq`` or, when that is not above
    every number taken, the next one above them. Writers serialize on the lock
    of ``directory`` (``locked``); the file is created whole and never replaces
    one (``write_new_file``). A file a host writes without the lock can still
    take a number meanwhile; it is never overwritten, and this file takes the
    next number. Returns the path written and its sequence number.
    """
    directory.mkdir(parents=True, exist_ok=True)
    with locked(directory):
        taken = [n for entry in os.listdir(directory) if (n := sequence_of(entry)) is not None]
        n = max(seq, max(taken, default=0) + 1)
        while not _write_new(directory / name_for(n), body):
            n += 1
    return directory / name_for(n), n
