"""``devkit.compact.execute``: the log file, exit codes, start failures, notices and log retention."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest
from devkit.compact.errors import CommandNotStartedError, LogDirectoryError
from devkit.compact.execute import KEEP_LOGS, default_log_dir, log_root, run_command

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
