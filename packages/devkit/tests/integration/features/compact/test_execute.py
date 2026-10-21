"""``devkit_agt.features.compact.usecases.execute``: the log file, exit codes, start failures, interruptions, notices and log retention."""

from __future__ import annotations

import contextlib
import importlib
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

import pytest
from devkit_agt.features.compact.models.errors import CommandNotStartedError, LogDirectoryError
from devkit_agt.features.compact.usecases.execute import (
    KEEP_LOGS,
    CommandInterrupted,
    default_log_dir,
    log_root,
    run_command,
)

execute = importlib.import_module("devkit_agt.features.compact.usecases.execute")

PY = sys.executable


def test_the_log_holds_the_complete_combined_output(tmp_path: Path) -> None:
    code = "import sys; print('out'); print('err', file=sys.stderr); print('3 passed in 0.1s')"
    run = run_command([PY, "-c", code], log_dir=tmp_path / "logs")
    assert run.passed and run.exit_code == 0
    assert run.log.parent == tmp_path / "logs"
    assert sorted(run.log.read_text().splitlines()) == sorted(["out", "err", "3 passed in 0.1s"])
    assert run.scan.summaries == ("3 passed in 0.1s",)
    assert run.notices == ()


def test_exit_codes_are_the_command_s_own_and_128_plus_a_signal() -> None:
    assert run_command([PY, "-c", "raise SystemExit(3)"]).exit_code == 3
    assert run_command(["sh", "-c", "kill -TERM $$"]).exit_code == 128 + 15


def test_stdin_is_closed_and_the_environment_is_passed() -> None:
    run = run_command(["sh", "-c", 'cat; echo "value=$PROBE"'], env={**os.environ, "PROBE": "42"})
    assert run.log.read_text() == "value=42\n"


def test_a_command_that_cannot_start_is_an_input_error_and_leaves_no_log(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    with pytest.raises(CommandNotStartedError) as caught:
        run_command(["devkit-no-such-command"], log_dir=logs)
    assert caught.value.code == "RUN_COMMAND_NOT_STARTED" and int(caught.value.exit_code) == 2
    assert list(logs.iterdir()) == []


def test_a_missing_working_directory_is_named_not_the_command(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(CommandNotStartedError) as caught:
        run_command(["true"], cwd=missing)
    assert "working directory" in str(caught.value) and caught.value.target_files == (str(missing.resolve()),)


def test_no_command_is_not_started() -> None:
    with pytest.raises(CommandNotStartedError, match="no command to start"):
        run_command([])


@pytest.mark.skipif(os.geteuid() == 0, reason="root can enter any directory")
def test_a_directory_that_cannot_be_entered_is_named_not_the_command(tmp_path: Path) -> None:
    locked = tmp_path / "locked"
    locked.mkdir(mode=0o000)
    try:
        with pytest.raises(CommandNotStartedError) as caught:
            run_command(["true"], cwd=locked, log_dir=tmp_path / "logs")
    finally:
        locked.chmod(0o755)
    assert "working directory" in str(caught.value) and caught.value.target_files == (str(locked.resolve()),)


def test_a_slow_command_returns_a_notice() -> None:
    run = run_command([PY, "-c", "import time; time.sleep(0.2)"], slow_after=0.1)
    assert [n.code for n in run.notices] == ["RUN_SLOW_COMMAND"]
    assert run_command([PY, "-c", "import time; time.sleep(0.2)"], slow_after=0).notices == ()


def test_only_the_newest_logs_are_kept(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    for i in range(KEEP_LOGS + 5):
        old = logs / f"old-{i}.log"
        old.write_text("")
        os.utime(old, (1_000 + i, 1_000 + i))
    run = run_command(["true"], log_dir=logs)
    kept = set(logs.glob("*.log"))
    assert len(kept) == KEEP_LOGS and run.log in kept
    assert logs / "old-0.log" not in kept and logs / f"old-{KEEP_LOGS + 4}.log" in kept


def test_logs_live_under_the_temporary_directory_one_directory_per_project(tmp_path: Path) -> None:
    first, second = tmp_path / "a", tmp_path / "b"
    first.mkdir()
    second.mkdir()
    assert default_log_dir(first).parent == log_root() == Path(tempfile.gettempdir()) / f"devkit-run-{os.getuid()}"
    assert default_log_dir(first) != default_log_dir(second)
    assert run_command(["true"], cwd=first).log.parent == default_log_dir(first)


def test_the_log_root_is_private_and_a_link_in_its_place_is_refused(tmp_path: Path) -> None:
    run_command(["true"])
    assert log_root().stat().st_mode & 0o777 == 0o700
    log_root().rename(tmp_path / "moved")
    log_root().symlink_to(tmp_path / "moved")
    with pytest.raises(LogDirectoryError) as caught:
        run_command(["true"])
    assert caught.value.code == "RUN_LOG_DIR_INVALID" and caught.value.target_files == (str(log_root()),)


def test_warning_locations_are_relative_to_the_working_directory(tmp_path: Path) -> None:
    code = "import os; print(os.path.join(os.getcwd(), 'pkg', 'mod.py') + ':7: UserWarning: careful')"
    run = run_command([PY, "-c", code], cwd=tmp_path)
    assert [w.location for w in run.scan.warnings] == ["pkg/mod.py:7"]


def _wait_for(path: Path, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while not path.exists():
        assert time.monotonic() < deadline, f"{path} did not appear"
        time.sleep(0.01)


def test_a_process_that_outlives_the_command_appends_to_the_log_and_never_moves_the_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    go, done = tmp_path / "go", tmp_path / "done"
    real_scan = execute.scan

    def scan_after_late_output(stream, **options):
        go.touch()  # the background process writes now, while the log is being read
        _wait_for(done)
        return real_scan(stream, **options)

    monkeypatch.setattr(execute, "scan", scan_after_late_output)
    script = f"seq 1 5000; (while [ ! -e {go} ]; do sleep 0.01; done; seq 1 1000 | sed s/^/LATE/; touch {done}) &"
    run = run_command(["sh", "-c", script], log_dir=tmp_path / "logs")
    assert run.scan.last_lines == ("4996", "4997", "4998", "4999", "5000")
    assert run.log.read_text().splitlines() == [str(i) for i in range(1, 5001)] + [f"LATE{i}" for i in range(1, 1001)]


def test_a_command_that_removes_its_working_directory_is_still_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gone = tmp_path / "gone"
    gone.mkdir()
    monkeypatch.chdir(gone)
    run = run_command(["sh", "-c", f"cd / && rmdir {gone} && echo removed"], log_dir=tmp_path / "logs")
    assert run.passed and run.scan.last_lines == ("removed",)


def test_a_signal_while_the_command_starts_still_stops_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    started: list[subprocess.Popen[Any]] = []
    popen = subprocess.Popen

    def popen_then_terminated(*args, **kwargs):
        started.append(popen(*args, **kwargs))
        os.kill(os.getpid(), signal.SIGTERM)  # handled before Popen returns, while nothing could stop the command
        return started[0]

    monkeypatch.setattr(execute.subprocess, "Popen", popen_then_terminated)
    with pytest.raises(CommandInterrupted) as caught:
        run_command(["sleep", "60"], log_dir=tmp_path / "logs")
    assert caught.value.code == 128 + signal.SIGTERM
    assert caught.value.run.interrupted == signal.SIGTERM and caught.value.run.exit_code == 128 + signal.SIGTERM
    assert caught.value.run.log.exists() and started[0].returncode is not None


def test_a_refused_sigterm_still_ends_in_command_interrupted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    started: list[subprocess.Popen[Any]] = []
    popen = subprocess.Popen
    killpg = os.killpg

    def popen_then_terminated(*args, **kwargs):
        started.append(popen(*args, **kwargs))
        os.kill(os.getpid(), signal.SIGTERM)
        return started[0]

    def refuse_sigterm(pgid: int, signum: int) -> None:
        killpg(pgid, signum)
        if signum == signal.SIGTERM:
            raise PermissionError(1, "Operation not permitted")  # macOS, for a group left with zombies only

    monkeypatch.setattr(execute.subprocess, "Popen", popen_then_terminated)
    monkeypatch.setattr(execute.os, "killpg", refuse_sigterm)
    with pytest.raises(CommandInterrupted) as caught:
        run_command(["sleep", "60"], log_dir=tmp_path / "logs")
    assert caught.value.run.interrupted == signal.SIGTERM
    assert started[0].returncode is not None  # the leader was reaped


def test_a_reaped_leader_s_group_is_never_signalled(monkeypatch: pytest.MonkeyPatch) -> None:
    process = subprocess.Popen(["true"], start_new_session=True)
    process.wait()  # its group ID may name another group by now
    sent: list[int] = []
    monkeypatch.setattr(execute.os, "killpg", lambda pgid, signum: sent.append(signum))
    execute._stop(process)
    assert sent == []


def _gone(pid: int, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.02)
    return False


def test_an_interrupt_kills_a_group_member_that_ignores_sigterm_after_the_leader_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(execute, "STOP_GRACE", 0.5)
    pidfile = tmp_path / "member.pid"
    # The leader exits on SIGTERM at once; its background member ignores it (and so do the sleeps it starts).
    script = f"(trap '' TERM; while :; do sleep 0.05; done) & echo $! > {pidfile}.tmp; mv {pidfile}.tmp {pidfile}; wait"

    def interrupt() -> None:
        _wait_for(pidfile)
        os.kill(os.getpid(), signal.SIGTERM)

    timer = threading.Thread(target=interrupt)
    timer.start()
    try:
        with pytest.raises(CommandInterrupted) as caught:
            run_command(["sh", "-c", script], log_dir=tmp_path / "logs")
    finally:
        timer.join()
    assert caught.value.run.interrupted == signal.SIGTERM
    member = int(pidfile.read_text())
    try:
        assert _gone(member), "a group member that ignores SIGTERM outlived the run"
    finally:
        with contextlib.suppress(ProcessLookupError):
            os.kill(member, signal.SIGKILL)


LINUX_PROC = pytest.mark.skipif(
    not Path("/proc/self/stat").exists() or not hasattr(os, "waitid"), reason="needs /proc and os.waitid (Linux)"
)


def _exited(process: subprocess.Popen[Any], timeout: float = 5.0) -> None:
    """Wait until ``process`` has exited, leaving it unreaped (a zombie)."""
    deadline = time.monotonic() + timeout
    while not execute._leader_exited(process.pid):
        assert time.monotonic() < deadline, "the leader did not exit"
        time.sleep(0.02)


@LINUX_PROC
def test_the_stop_ends_its_wait_once_only_the_unreaped_leader_is_left() -> None:
    process = subprocess.Popen(["sleep", "60"], start_new_session=True)  # sleep exits at once on SIGTERM
    started = time.monotonic()
    execute._stop(process)
    assert time.monotonic() - started < execute.STOP_GRACE / 2, "the zombie leader held the wait to STOP_GRACE"
    assert process.returncode == -signal.SIGTERM  # still unreaped when the wait ended: it was SIGTERM, not SIGKILL


@LINUX_PROC
def test_a_live_member_keeps_the_group_of_an_exited_leader_running() -> None:
    process = subprocess.Popen(["sh", "-c", "sleep 60 & exit 0"], start_new_session=True)
    try:
        _exited(process)
        assert execute._live_members(process.pid) is True and not execute._only_zombies_left(process.pid)
        assert process.returncode is None  # checking did not reap the leader
    finally:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def test_without_proc_the_group_never_counts_as_done(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_proc(path: str) -> list[str]:
        raise FileNotFoundError(path)

    process = subprocess.Popen(["true"], start_new_session=True)
    try:
        if hasattr(os, "waitid"):
            _exited(process)
        monkeypatch.setattr(execute.os, "listdir", no_proc)  # macOS: the wait keeps relying on signal 0
        assert execute._live_members(process.pid) is None and not execute._only_zombies_left(process.pid)
    finally:
        process.wait()


def test_a_log_root_others_can_enter_is_made_private(tmp_path: Path) -> None:
    log_root().mkdir(mode=0o700)
    log_root().chmod(0o777)
    run_command(["true"])
    assert log_root().stat().st_mode & 0o777 == 0o700
    assert default_log_dir(Path.cwd()).stat().st_mode & 0o777 == 0o700


def test_a_project_log_directory_that_is_a_link_is_refused_and_its_target_left_alone(tmp_path: Path) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    planted = [elsewhere / f"{i}.log" for i in range(KEEP_LOGS + 5)]
    for path in planted:
        path.write_text("keep")
    log_root().mkdir(mode=0o700)
    default_log_dir(Path.cwd()).symlink_to(elsewhere)
    with pytest.raises(LogDirectoryError) as caught:
        run_command(["true"])
    assert caught.value.target_files == (str(default_log_dir(Path.cwd())),)
    assert all(path.exists() for path in planted) and len(list(elsewhere.iterdir())) == len(planted)


def test_a_project_log_directory_that_is_a_file_is_refused() -> None:
    log_root().mkdir(mode=0o700)
    default_log_dir(Path.cwd()).write_text("")
    with pytest.raises(LogDirectoryError) as caught:
        run_command(["true"])
    assert caught.value.code == "RUN_LOG_DIR_INVALID" and int(caught.value.exit_code) == 2


@pytest.mark.skipif(os.geteuid() == 0, reason="root can write to any directory")
def test_a_log_directory_that_cannot_be_written_is_a_log_directory_error(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir(mode=0o500)
    try:
        with pytest.raises(LogDirectoryError) as caught:
            run_command(["true"], log_dir=logs)
    finally:
        logs.chmod(0o700)
    assert caught.value.code == "RUN_LOG_DIR_INVALID" and caught.value.target_files == (str(logs),)
    (tmp_path / "file").write_text("")
    with pytest.raises(LogDirectoryError):
        run_command(["true"], log_dir=tmp_path / "file" / "logs")


def test_a_nested_devkit_root_does_not_stop_a_run(tmp_path: Path) -> None:
    from devkit_agt.features.compact.usecases.execute import default_log_dir

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    nested = tmp_path / "pkg"
    (nested / ".devkit").mkdir(parents=True)
    assert default_log_dir(nested) == default_log_dir(tmp_path)
