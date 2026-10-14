from __future__ import annotations

import os
import stat
import sys
import threading
import time
from pathlib import Path

import pytest
from devkit.advisory import ActionMode, AdvisoryError
from devkit.core import (
    ArgumentError,
    Deadline,
    DeadlineExceededError,
    LockHeldError,
    LockUnsupportedError,
    UnsafePathError,
    file_lock,
)


class _CallerTimeout(AdvisoryError):
    code = "CALLER_TIMEOUT"


def test_creates_a_private_lock_file_and_releases_it(tmp_path: Path) -> None:
    path = tmp_path / "lock"
    with file_lock(path):
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
    with file_lock(path, timeout=0):  # released: free again at once
        pass


def test_a_held_lock_fails_at_once_with_timeout_zero(tmp_path: Path) -> None:
    path = tmp_path / "lock"
    with file_lock(path), pytest.raises(LockHeldError) as raised, file_lock(path, timeout=0):
        pass
    error = raised.value
    assert isinstance(error, DeadlineExceededError)
    assert (error.code, error.mode, error.seconds) == ("LOCK_HELD", ActionMode.DEFER, 0)
    assert error.what == f"waiting for the lock on {path}" and error.target_files == (str(path),)


def test_readers_share_and_a_writer_waits_for_them(tmp_path: Path) -> None:
    path = tmp_path / "lock"
    with file_lock(path, shared=True), file_lock(path, shared=True, timeout=0):
        start = time.monotonic()
        with pytest.raises(LockHeldError), file_lock(path, timeout=0.1, what="waiting for the registry"):
            pass
        assert time.monotonic() - start >= 0.1
    with file_lock(path), pytest.raises(LockHeldError), file_lock(path, shared=True, timeout=0):
        pass


def test_a_bounded_wait_acquires_once_the_holder_releases(tmp_path: Path) -> None:
    path = tmp_path / "lock"
    held, release, acquired = threading.Event(), threading.Event(), threading.Event()

    def holder() -> None:
        with file_lock(path):
            held.set()
            release.wait(5)

    thread = threading.Thread(target=holder)
    thread.start()
    assert held.wait(5)
    threading.Timer(0.1, release.set).start()
    with file_lock(path, deadline=Deadline(5)):
        acquired.set()
    thread.join(5)
    assert acquired.is_set()


def test_an_unbounded_wait_blocks_until_the_lock_is_free(tmp_path: Path) -> None:
    path = tmp_path / "lock"
    acquired = threading.Event()

    def waiter() -> None:
        with file_lock(path):
            acquired.set()

    with file_lock(path):
        thread = threading.Thread(target=waiter)
        thread.start()
        thread.join(0.2)
        assert thread.is_alive() and not acquired.is_set()
    thread.join(5)
    assert acquired.is_set()


def test_a_deadline_with_an_error_factory_raises_the_callers_error(tmp_path: Path) -> None:
    path = tmp_path / "lock"
    deadline = Deadline(0.05, error=lambda what, seconds: _CallerTimeout(f"{what} exceeded {seconds:g}s"))
    expected = r"^waiting for the namespace lock exceeded 0.05s$"
    with (
        file_lock(path),
        pytest.raises(_CallerTimeout, match=expected),
        file_lock(path, deadline=deadline, what="waiting for the namespace lock"),
    ):
        pass
    with file_lock(path), pytest.raises(LockHeldError) as raised, file_lock(path, deadline=Deadline(0)):
        pass
    assert raised.value.seconds == 0


def test_the_lock_is_released_when_the_block_raises(tmp_path: Path) -> None:
    path = tmp_path / "lock"
    with pytest.raises(RuntimeError), file_lock(path):
        raise RuntimeError("boom")
    with file_lock(path, timeout=0):
        pass


def test_timeout_and_deadline_together_are_an_argument_error(tmp_path: Path) -> None:
    with pytest.raises(ArgumentError), file_lock(tmp_path / "lock", timeout=1, deadline=Deadline(1)):
        pass


def test_symlinks_and_non_regular_files_are_never_locked(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.write_text("")
    link = tmp_path / "link"
    link.symlink_to(target)
    directory = tmp_path / "directory"
    directory.mkdir()
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    for path in (link, directory, fifo):
        with pytest.raises(UnsafePathError) as raised, file_lock(path):
            pass
        assert raised.value.code == "PATH_UNSAFE" and raised.value.target_files == (str(path),)
    assert target.read_text() == ""


def test_a_missing_directory_is_an_os_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError), file_lock(tmp_path / "missing" / "lock"):
        pass


def test_a_platform_without_flock_is_lock_unsupported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "fcntl", None)
    with pytest.raises(LockUnsupportedError) as raised, file_lock(tmp_path / "lock"):
        pass
    assert (raised.value.code, raised.value.mode) == ("LOCK_UNSUPPORTED", ActionMode.BLOCKED)
    assert not (tmp_path / "lock").exists()
