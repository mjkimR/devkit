from __future__ import annotations

import builtins
import io
import os
import subprocess
import sys
from pathlib import Path

import pytest
from scope.support import record, registry

from devkit_spec.base.errors import ScopeSharedPathError, ScopeTimeoutError
from devkit_spec.features.scope import Deadline, Event, FlockLocker
from devkit_spec.features.scope.repositories.localfs import ReadFlockLocker


@pytest.mark.parametrize("operation", ["query", "history"])
def test_absence_and_missing_lock(tmp_path: Path, operation: str) -> None:
    fs = registry(tmp_path / "missing")
    call = getattr(fs, operation)
    assert call("ns", Deadline(1)) == ([], [])
    assert not fs.shared.exists()
    (fs.shared / "ns").mkdir(parents=True)
    with pytest.raises(ScopeSharedPathError):
        call("ns", Deadline(1))
    assert list((fs.shared / "ns").iterdir()) == []


@pytest.mark.parametrize("kind", ["fifo", "directory", "symlink"])
@pytest.mark.parametrize("operation", ["query", "history"])
def test_unsafe_lock_rejected_without_blocking(tmp_path: Path, kind: str, operation: str) -> None:
    directory = tmp_path / "ns"
    directory.mkdir()
    lock = directory / ".lock"
    if kind == "fifo":
        os.mkfifo(lock)
    elif kind == "directory":
        lock.mkdir()
    else:
        lock.symlink_to(tmp_path / "target")
    # A separate process with a timeout catches a blocking FIFO open without hanging pytest.
    code = (
        "from pathlib import Path; from devkit_spec.features.scope import LocalRegistry, Deadline; "
        f"LocalRegistry(Path({str(tmp_path)!r})).{operation}('ns', Deadline(.2))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=3)
    assert result.returncode != 0
    assert "ScopeSharedPathError" in result.stderr


@pytest.mark.parametrize("operation", ["query", "history"])
def test_permission_failure_is_not_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str) -> None:
    fs = registry(tmp_path)
    fs.register(record("a", "/wt/a"), Deadline(1))
    original = Path.stat

    def denied(path: Path, *args: object, **kwargs: object):
        if path == tmp_path / "ns":
            raise PermissionError("denied namespace")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", denied)
    with pytest.raises(ScopeSharedPathError):
        getattr(fs, operation)("ns", Deadline(1))


def guard_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    original_open = os.open
    original_io = io.open
    original_builtin = builtins.open

    def fail(*args: object, **kwargs: object):
        pytest.fail(f"query attempted filesystem mutation: {args}")

    def os_read(path, flags, *args, **kwargs):
        if os.fspath(path) == os.devnull:
            return original_open(path, flags, *args, **kwargs)
        assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        return original_open(path, flags, *args, **kwargs)

    def checked_open(original):
        def read(path, mode="r", *args, **kwargs):
            assert not any(flag in mode for flag in "wax+")
            return original(path, mode, *args, **kwargs)

        return read

    monkeypatch.setattr(os, "open", os_read)
    monkeypatch.setattr(io, "open", checked_open(original_io))
    monkeypatch.setattr(builtins, "open", checked_open(original_builtin))
    for name in ("mkdir", "unlink", "remove", "rename", "replace"):
        monkeypatch.setattr(os, name, fail)


def test_read_snapshot_and_mutation_cleanup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fs = registry(tmp_path)
    token, stored = fs.register(record("a", "/wt/a"), Deadline(1))
    fs.append("ns", [Event(event="register", task="a")], Deadline(1))
    leftover = tmp_path / "ns/.a.json.devkit-crash.tmp"
    leftover.write_text("partial")
    before = {p.name: p.read_bytes() for p in (tmp_path / "ns").iterdir()}
    with monkeypatch.context() as guarded:
        guard_writes(guarded)
        assert fs.query("ns", Deadline(1))[0] == [stored]
        assert fs.history("ns", Deadline(1))[0][0].task == "a"
    assert {p.name: p.read_bytes() for p in (tmp_path / "ns").iterdir()} == before
    fs.update(token, 1, "next", stored, Deadline(1))
    assert not leftover.exists()


@pytest.mark.parametrize("operation", ["query", "history"])
def test_reader_times_out_behind_writer(tmp_path: Path, operation: str) -> None:
    fs = registry(tmp_path)
    fs.register(record("a", "/wt/a"), Deadline(1))
    unlock = FlockLocker().acquire(tmp_path / "ns/.lock", Deadline(1))
    try:
        with pytest.raises(ScopeTimeoutError):
            getattr(fs, operation)("ns", Deadline(0.05))
    finally:
        unlock()
    getattr(fs, operation)("ns", Deadline(1))


@pytest.mark.parametrize("operation", ["register", "update", "release", "append"])
def test_shared_reader_excludes_writer_process(tmp_path: Path, operation: str) -> None:
    fs = registry(tmp_path)
    token, stored = fs.register(record("a", "/wt/a"), Deadline(1))
    lock = tmp_path / "ns/.lock"
    unlock = ReadFlockLocker().acquire(lock, Deadline(1))
    other_reader = ReadFlockLocker().acquire(lock, Deadline(1))
    other_reader()
    code = f"""
from pathlib import Path
from devkit_spec.features.scope import LocalRegistry
from devkit_spec.features.scope import Deadline
from devkit_spec.features.scope import Record
from devkit_spec.features.scope import Event
fs = LocalRegistry(Path({str(tmp_path)!r}))
record = Record(namespace='ns', task_id='b', worktree='/wt/b')
print('ready', flush=True)
operation = {operation!r}
if operation == 'register': fs.register(record, Deadline(3))
elif operation == 'update':
    record = fs.query('ns', Deadline(3))[0][0]
    fs.update({token!r}, 1, 'update', record, Deadline(3))
elif operation == 'release': fs.release('ns', 'a', {token!r}, Deadline(3))
else: fs.append('ns', [Event(event='update', task='a')], Deadline(3))
print('done', flush=True)
"""
    process = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert process.stdout is not None
        assert process.stdout.readline().strip() == "ready"
        with pytest.raises(subprocess.TimeoutExpired):
            process.communicate(timeout=0.1)
        assert fs.query("ns", Deadline(1))[0] == [stored]
    finally:
        unlock()
        stdout, stderr = process.communicate(timeout=5)
    assert process.returncode == 0, stderr
    assert "done" in stdout


def test_read_lock_released_after_read_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fs = registry(tmp_path)
    fs.register(record("a", "/wt/a"), Deadline(1))
    with monkeypatch.context() as patch:

        def fail(directory: Path):
            raise PermissionError("scan denied")

        patch.setattr(fs, "_read_all", fail)
        with pytest.raises(ScopeSharedPathError):
            fs.query("ns", Deadline(1))
    unlock = FlockLocker().acquire(tmp_path / "ns/.lock", Deadline(1))
    unlock()


@pytest.mark.parametrize("operation", ["query", "history"])
def test_unreadable_lock_fails_and_unsupported_is_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    from devkit_spec.base.errors import ScopeLockUnsupportedError

    fs = registry(tmp_path)
    fs.register(record("a", "/wt/a"), Deadline(1))
    with monkeypatch.context() as patch:

        def denied(*args: object, **kwargs: object):
            raise PermissionError("lock denied")

        patch.setattr(os, "open", denied)
        with pytest.raises(ScopeSharedPathError):
            getattr(fs, operation)("ns", Deadline(1))
    with monkeypatch.context() as patch:
        patch.setitem(sys.modules, "fcntl", None)
        with pytest.raises(ScopeLockUnsupportedError):
            getattr(fs, operation)("ns", Deadline(1))
