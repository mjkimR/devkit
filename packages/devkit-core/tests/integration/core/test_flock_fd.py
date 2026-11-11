"""``devkit_core.core.locks.flock_fd``: the bounded ``flock`` wait on a descriptor the caller opened."""

from __future__ import annotations

import errno
import os
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest
from devkit.advisory import AdvisoryError
from devkit_core.core import Deadline, LockHeldError, LockUnsupportedError, file_lock, flock_fd, locks


class _CallerTimeout(AdvisoryError):
    code = "CALLER_TIMEOUT"


@pytest.fixture
def directory_fd(tmp_path: Path) -> Iterator[int]:
    fd = os.open(tmp_path, os.O_RDONLY)
    yield fd
    os.close(fd)


def test_locks_a_directory_and_reports_the_holder(tmp_path: Path, directory_fd: int) -> None:
    flock_fd(directory_fd, target=tmp_path, timeout=0)
    second = os.open(tmp_path, os.O_RDONLY)
    try:
        with pytest.raises(LockHeldError) as raised:
            flock_fd(second, target=tmp_path, timeout=0)
        error = raised.value
        assert error.message == f"another process holds the lock on {tmp_path}"
        assert (error.what, error.seconds, error.target_files) == (
            f"waiting for the lock on {tmp_path}",
            0,
            (str(tmp_path),),
        )
    finally:
        os.close(second)


def test_shared_locks_coexist_and_exclude_a_writer(tmp_path: Path) -> None:
    path = tmp_path / "lock"
    path.write_text("")
    first, second, writer = (os.open(path, os.O_RDONLY) for _ in range(3))
    try:
        flock_fd(first, target=path, shared=True, timeout=0)
        flock_fd(second, target=path, shared=True, timeout=0)
        with pytest.raises(LockHeldError):
            flock_fd(writer, target=path, timeout=0.05)
    finally:
        for fd in (first, second, writer):
            os.close(fd)


def test_a_deadline_with_an_error_factory_raises_its_error(tmp_path: Path, directory_fd: int) -> None:
    path = tmp_path / "lock"
    with file_lock(path):
        fd = os.open(path, os.O_RDONLY)
        try:
            deadline = Deadline(0, error=lambda what, seconds: _CallerTimeout(f"{what} ran out"))
            with pytest.raises(_CallerTimeout, match=r"^waiting for the namespace lock ran out$"):
                flock_fd(fd, target=path, deadline=deadline, what="waiting for the namespace lock")
        finally:
            os.close(fd)


def test_timeout_and_deadline_together_are_a_programming_error(tmp_path: Path, directory_fd: int) -> None:
    with pytest.raises(ValueError, match="flock_fd takes a timeout or a deadline"):
        flock_fd(directory_fd, target=tmp_path, timeout=1, deadline=Deadline(1))


class _Refusing:
    """An ``fcntl`` stand-in whose ``flock`` fails with ``code``."""

    LOCK_SH, LOCK_EX, LOCK_NB, LOCK_UN = 1, 2, 4, 8

    def __init__(self, code: int) -> None:
        self.code = code

    def flock(self, fd: int, operation: int) -> None:
        raise OSError(self.code, os.strerror(self.code))


def _refusing(monkeypatch: pytest.MonkeyPatch, code: int) -> None:
    stand_in: ModuleType | _Refusing = _Refusing(code)
    monkeypatch.setattr(locks, "_fcntl", lambda: stand_in)


@pytest.mark.parametrize("code", sorted(locks.NO_LOCK_ERRNOS))
@pytest.mark.parametrize("timeout", [None, 1.0])
def test_a_file_system_without_locks_maps_through_the_factory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, directory_fd: int, code: int, timeout: float | None
) -> None:
    _refusing(monkeypatch, code)
    with pytest.raises(LockUnsupportedError) as raised:
        flock_fd(
            directory_fd,
            target=tmp_path,
            timeout=timeout,
            unsupported=lambda exc: LockUnsupportedError(f"no flock: {exc.strerror}"),
        )
    assert isinstance(raised.value.__cause__, OSError)
    with pytest.raises(OSError) as plain:
        flock_fd(directory_fd, target=tmp_path, timeout=timeout)
    assert plain.value.errno == code


def test_other_errors_propagate_unmapped(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, directory_fd: int) -> None:
    _refusing(monkeypatch, errno.EBADF)
    with pytest.raises(OSError) as raised:
        flock_fd(directory_fd, target=tmp_path, unsupported=lambda exc: LockUnsupportedError("unused"))
    assert raised.value.errno == errno.EBADF


def test_file_lock_keeps_raising_the_os_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _refusing(monkeypatch, errno.ENOLCK)
    with pytest.raises(OSError) as raised, file_lock(tmp_path / "lock"):
        pass
    assert not isinstance(raised.value, LockUnsupportedError) and raised.value.errno == errno.ENOLCK
