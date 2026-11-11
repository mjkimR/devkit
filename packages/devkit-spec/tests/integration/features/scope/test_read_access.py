from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from spec_support.scope import record, registry
from spec_support.scope_read_access import guard_writes

from devkit_spec.base.errors import ScopeSharedPathError, ScopeTimeoutError
from devkit_spec.features.scope import Deadline, FlockLocker
from devkit_spec.features.scope.repositories.localfs import ReadFlockLocker


def test_absence_and_missing_lock(tmp_path: Path) -> None:
    fs = registry(tmp_path / "missing")
    call = fs.query
    assert call("ns", Deadline(1)) == ([], [])
    assert not fs.shared.exists()
    (fs.shared / "ns").mkdir(parents=True)
    with pytest.raises(ScopeSharedPathError):
        call("ns", Deadline(1))
    assert list((fs.shared / "ns").iterdir()) == []


@pytest.mark.parametrize("kind", ["fifo", "directory", "symlink"])
def test_unsafe_lock_rejected_without_blocking(tmp_path: Path, kind: str) -> None:
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
        f"LocalRegistry(Path({str(tmp_path)!r})).query('ns', Deadline(.2))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=3)
    assert result.returncode != 0
    assert "ScopeSharedPathError" in result.stderr


def test_permission_failure_is_not_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fs = registry(tmp_path)
    fs.register(record("a", "/wt/a"), Deadline(1))
    original = Path.stat

    def denied(path: Path, *args: object, **kwargs: object):
        if path == tmp_path / "ns":
            raise PermissionError("denied namespace")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", denied)
    with pytest.raises(ScopeSharedPathError):
        fs.query("ns", Deadline(1))


def test_read_snapshot_and_mutation_cleanup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fs = registry(tmp_path)
    _, stored = fs.register(record("a", "/wt/a"), Deadline(1))
    (tmp_path / "ns/journal.jsonl").write_text('{"event": "register", "task": "a"}\n')  # an earlier version's
    leftover = tmp_path / "ns/.a.json.devkit-crash.tmp"
    leftover.write_text("partial")
    before = {p.name: p.read_bytes() for p in (tmp_path / "ns").iterdir()}
    with monkeypatch.context() as guarded:
        guard_writes(guarded)
        assert fs.query("ns", Deadline(1))[0] == [stored]
    assert {p.name: p.read_bytes() for p in (tmp_path / "ns").iterdir()} == before
    fs.register(record("b", "/wt/b"), Deadline(1))
    assert not leftover.exists()


def test_reader_times_out_behind_writer(tmp_path: Path) -> None:
    fs = registry(tmp_path)
    fs.register(record("a", "/wt/a"), Deadline(1))
    unlock = FlockLocker().acquire(tmp_path / "ns/.lock", Deadline(1))
    try:
        with pytest.raises(ScopeTimeoutError):
            fs.query("ns", Deadline(0.05))
    finally:
        unlock()
    fs.query("ns", Deadline(1))


@pytest.mark.parametrize("operation", ["register", "release", "sweep"])
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
fs = LocalRegistry(Path({str(tmp_path)!r}))
record = Record(namespace='ns', task_id='b', worktree='/wt/b')
print('ready', flush=True)
operation = {operation!r}
if operation == 'register': fs.register(record, Deadline(3))
elif operation == 'release': fs.release('ns', 'a', {token!r}, Deadline(3))
else: fs.sweep('ns', False, {{}}, Deadline(3))
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


def test_unreadable_lock_fails_and_unsupported_is_preserved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_spec.base.errors import ScopeLockUnsupportedError

    fs = registry(tmp_path)
    fs.register(record("a", "/wt/a"), Deadline(1))
    with monkeypatch.context() as patch:

        def denied(*args: object, **kwargs: object):
            raise PermissionError("lock denied")

        patch.setattr(os, "open", denied)
        with pytest.raises(ScopeSharedPathError):
            fs.query("ns", Deadline(1))
    with monkeypatch.context() as patch:
        patch.setitem(sys.modules, "fcntl", None)
        with pytest.raises(ScopeLockUnsupportedError):
            fs.query("ns", Deadline(1))
