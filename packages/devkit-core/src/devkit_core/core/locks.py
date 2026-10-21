"""Advisory file locks: ``flock`` on a lock file, held for a ``with`` block.

Linux and macOS only (``fcntl.flock``; ``LockUnsupportedError`` elsewhere). The operating system releases
a lock when its process dies, so none goes stale. Network file systems are not supported: ``flock`` is not
guaranteed there.
"""

from __future__ import annotations

import contextlib
import errno
import os
import stat
import time
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

from devkit_core.base.errors import LockHeldError, LockUnsupportedError, UnsafePathError
from devkit_core.core.deadline import Deadline

LOCK_FILE_MODE = 0o600
POLL_INTERVAL = 0.01  # seconds between attempts while a bounded wait lasts


def _fcntl() -> ModuleType:
    try:
        import fcntl
    except ImportError as exc:
        raise LockUnsupportedError("fcntl.flock is not available on this platform") from exc
    return fcntl


def _open(path: Path) -> int:
    """The lock file's descriptor; ``UnsafePathError`` for a symlink or anything but a regular file."""
    try:
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, LOCK_FILE_MODE)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise UnsafePathError(f"the lock file {path} is a symbolic link", target_files=[str(path)]) from exc
        if exc.errno == errno.EISDIR:
            raise UnsafePathError(f"the lock file {path} is a directory", target_files=[str(path)]) from exc
        raise
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise UnsafePathError(f"the lock file {path} is not a regular file", target_files=[str(path)])
    return fd


def _bound(timeout: float | None, deadline: Deadline | None) -> Deadline | None:
    if timeout is not None and deadline is not None:
        raise ValueError("file_lock takes a timeout or a deadline, not both")
    return Deadline(timeout) if timeout is not None else deadline


@contextlib.contextmanager
def file_lock(
    path: Path,
    *,
    shared: bool = False,
    timeout: float | None = None,
    deadline: Deadline | None = None,
    what: str | None = None,
) -> Iterator[None]:
    """Hold an exclusive (``shared=False``) or shared ``flock`` on the lock file ``path`` for the block.

    ``path`` is created (mode ``0o600``) when it is missing; its directory must exist. It is opened with
    ``O_NOFOLLOW``: a symbolic link, or anything else that is not a regular file, is ``UnsafePathError``
    (``PATH_UNSAFE``) and is never locked through. Other file system failures raise ``OSError``.

    The wait for another holder is bounded by ``timeout`` seconds or by a shared ``deadline``; passing both is
    a programming error (``ValueError``), as it is for ``run_git``:
    the lock is polled every ``POLL_INTERVAL`` seconds, at least once even when no time is left (``timeout=0``
    tries once and never waits). When the wait runs out it raises ``deadline.exceeded(what)`` if the
    deadline has an error factory, else ``LockHeldError`` (``LOCK_HELD``, a ``DeadlineExceededError``).
    ``what`` names the wait in that error (default ``waiting for the lock on <path>``). Without either
    bound the call blocks until the lock is free.
    """
    fcntl = _fcntl()
    limit = _bound(timeout, deadline)
    operation = fcntl.LOCK_SH if shared else fcntl.LOCK_EX
    fd = _open(path)
    try:
        if limit is None:
            fcntl.flock(fd, operation)
        else:
            _poll(fcntl, fd, operation, limit, path, what or f"waiting for the lock on {path}")
        try:
            yield
        finally:
            with contextlib.suppress(OSError):
                fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _poll(fcntl: ModuleType, fd: int, operation: int, limit: Deadline, path: Path, what: str) -> None:
    while True:
        try:
            fcntl.flock(fd, operation | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            remaining = limit.remaining()
            if remaining <= 0:
                if limit.error is not None:
                    raise limit.exceeded(what) from None
                raise LockHeldError(
                    f"another process holds the lock on {path}",
                    what=what,
                    seconds=limit.seconds,
                    target_files=[str(path)],
                ) from None
            time.sleep(min(POLL_INTERVAL, remaining))
