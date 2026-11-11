"""Advisory file locks: ``flock`` on a lock file, held for a ``with`` block.

Linux and macOS only (``fcntl.flock``; ``LockUnsupportedError`` elsewhere). The operating system releases
a lock when its process dies, so none goes stale. Network file systems are not supported: ``flock`` is not
guaranteed there.

``file_lock`` opens the lock file and holds the lock for a block; ``flock_fd`` takes the lock on a descriptor the
caller opened (a directory, a read-only file) with the same bounded wait. ``NO_LOCK_ERRNOS`` are the ``errno``
values with which a file system refuses ``flock`` itself, which ``flock_fd`` maps through its ``unsupported``
factory.
"""

from __future__ import annotations

import contextlib
import errno
import os
import stat
import time
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType

from devkit_core.base.errors import LockHeldError, LockUnsupportedError, UnsafePathError
from devkit_core.core.deadline import Deadline

LOCK_FILE_MODE = 0o600
POLL_INTERVAL = 0.01  # seconds between attempts while a bounded wait lasts
# ``errno`` values with which a file system refuses ``flock`` itself (a network or FUSE file system, for example).
NO_LOCK_ERRNOS = frozenset({errno.ENOTSUP, errno.EOPNOTSUPP, errno.ENOLCK, errno.EINVAL, errno.ENOSYS})

# Builds the error for ``flock`` refused by the file system from the ``OSError`` it raised.
UnsupportedFactory = Callable[[OSError], BaseException]


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


def _bound(timeout: float | None, deadline: Deadline | None, function: str = "file_lock") -> Deadline | None:
    if timeout is not None and deadline is not None:
        raise ValueError(f"{function} takes a timeout or a deadline, not both")
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
    fd = _open(path)
    try:
        _acquire(fcntl, fd, shared, limit, path, what or f"waiting for the lock on {path}", None)
        try:
            yield
        finally:
            with contextlib.suppress(OSError):
                fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def flock_fd(
    fd: int,
    *,
    target: Path | str,
    shared: bool = False,
    timeout: float | None = None,
    deadline: Deadline | None = None,
    what: str | None = None,
    unsupported: UnsupportedFactory | None = None,
) -> None:
    """Take an exclusive (``shared=False``) or shared ``flock`` on the open descriptor ``fd``, as ``file_lock`` does.

    The caller opened ``fd`` (and checked what it names) and releases the lock by closing it or with ``LOCK_UN``.
    ``target`` names the locked path in the errors. The wait is bounded and fails exactly as ``file_lock``'s: by
    ``timeout`` seconds or a shared ``deadline`` (both is ``ValueError``), polled every ``POLL_INTERVAL`` seconds and at
    least once, raising ``deadline.exceeded(what)`` when the deadline has an error factory, else ``LockHeldError``;
    ``what`` defaults to ``waiting for the lock on <target>``. Without either bound the call blocks.

    ``flock`` refused by the file system (``NO_LOCK_ERRNOS``) raises ``unsupported(error)`` when the factory is given
    (``LockUnsupportedError`` with the caller's fix, or a caller's own code), else the ``OSError`` itself, as
    ``file_lock`` does; every other ``OSError`` propagates.
    """
    fcntl = _fcntl()
    limit = _bound(timeout, deadline, "flock_fd")
    _acquire(fcntl, fd, shared, limit, target, what or f"waiting for the lock on {target}", unsupported)


def _acquire(
    fcntl: ModuleType,
    fd: int,
    shared: bool,
    limit: Deadline | None,
    target: Path | str,
    what: str,
    unsupported: UnsupportedFactory | None,
) -> None:
    operation = fcntl.LOCK_SH if shared else fcntl.LOCK_EX
    try:
        if limit is None:
            fcntl.flock(fd, operation)
        else:
            _poll(fcntl, fd, operation, limit, target, what)
    except OSError as exc:
        if unsupported is not None and exc.errno in NO_LOCK_ERRNOS:
            raise unsupported(exc) from exc
        raise


def _poll(fcntl: ModuleType, fd: int, operation: int, limit: Deadline, target: Path | str, what: str) -> None:
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
                    f"another process holds the lock on {target}",
                    what=what,
                    seconds=limit.seconds,
                    target_files=[str(target)],
                ) from None
            time.sleep(min(POLL_INTERVAL, remaining))
