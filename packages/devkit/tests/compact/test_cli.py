"""``devkit run``: result lines, the excerpt on failure, relayed advisories, output options, interruptions and exit
codes."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
from click.testing import CliRunner, Result
from devkit.advisory import AdvisoryError, Level
from devkit.cli import cli

PY = sys.executable


def _run(*args: str, env: dict[str, str] | None = None) -> Result:
    return CliRunner().invoke(cli, ["run", *args], env=env)


def _python(code: str, *options: str, env: dict[str, str] | None = None) -> Result:
    return _run(*options, "--", PY, "-c", code, env=env)


def test_a_passing_command_prints_its_result_and_summaries_only() -> None:
    result = _python("print('noise ' * 50); print('4 passed in 0.2s'); print('a.py:3: UserWarning: old')")
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert lines[0].startswith('[RUN: "') and " outcome=passed exit=0 log=" in lines[0]
    assert lines[1:] == ['[RUN_SUMMARY: "4 passed in 0.2s"]', '[RUN_WARNING: "UserWarning: old" location=a.py:3]']
    assert len(lines) == 3 and result.stderr == ""


def test_a_passing_command_without_a_recognized_summary_shows_its_last_lines() -> None:
    result = _python("print('a.py:3: UserWarning: x'); print(); print('Success: no issues in 3 modules')")
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines()[1:] == [
        '[RUN_LAST_LINE: "a.py:3: UserWarning: x"]',
        '[RUN_LAST_LINE: "Success: no issues in 3 modules"]',
        '[RUN_WARNING: "UserWarning: x" location=a.py:3]',
    ]
    data = json.loads(_python("print('done')", "--format", "json").stdout)
    assert data["summaries"] == [] and data["last_lines"] == ["done"]


def test_a_failing_command_adds_the_excerpt_and_exits_1() -> None:
    result = _python("import sys; print('E   assert 1 == 2'); print('1 failed in 0.1s'); sys.exit(5)")
    assert result.exit_code == 1
    lines = result.stdout.splitlines()
    assert " outcome=failed exit=5 " in lines[0]
    assert lines[1] == '[RUN_SUMMARY: "1 failed in 0.1s"]'
    assert lines[2].startswith("[RUN_OUTPUT: shown=")
    assert lines[3:] == ["E   assert 1 == 2", "1 failed in 0.1s"]


def test_progress_is_filtered_out_of_the_excerpt_and_counted() -> None:
    code = (
        "import sys; print('tests/test_a.py ....F.. [ 50%]'); print('....... [100%]');"
        "print('FAILED tests/test_a.py::test_x - assert 1 == 2'); print('1 failed, 13 passed in 0.1s'); sys.exit(1)"
    )
    result = _python(code)
    lines = result.stdout.splitlines()
    assert lines[2].endswith(" filtered=1]")
    assert lines[3:] == [
        "tests/test_a.py ....F.. [ 50%]",
        "FAILED tests/test_a.py::test_x - assert 1 == 2",
        "1 failed, 13 passed in 0.1s",
    ]
    assert json.loads(_python(code, "--format", "json").stdout)["filtered"] == 1


def test_omissions_are_reported() -> None:
    result = _python("import sys; [print(f'{i:04d}' + 'x' * 75) for i in range(500)]; sys.exit(1)")
    assert "[RUN_OMITTED: summaries=0 failures=0 warnings=0 advisories=0 output=" in result.stdout
    assert "characters omitted, log lines " in result.stdout


def test_a_passing_command_does_not_count_the_excerpt_it_does_not_show() -> None:
    result = _python("[print(f'{i:04d}' + 'x' * 75) for i in range(500)]")
    assert result.exit_code == 0 and "RUN_OMITTED" not in result.stdout
    data = json.loads(_python("[print(f'{i:04d}' + 'x' * 75) for i in range(500)]", "--format", "json").stdout)
    assert data["omitted"]["output"] == 0 and data["output"] is None


def test_relayed_advisories_go_to_stderr_warnings_first_errors_last() -> None:
    error = AdvisoryError("broken", code="CONFIG_INVALID").render()
    warning = AdvisoryError("drift", code="OVERRIDE_DRIFT", level=Level.WARNING).render()
    notice = AdvisoryError("fyi", code="BUNDLE_UNSELECTED", level=Level.NOTICE).render()
    code = f"import sys; print({error!r}); print({notice!r}); print({warning!r}); sys.exit(2)"
    result = _python(code)
    assert result.exit_code == 1
    assert result.stderr == f"{notice}\n{warning}\n{error}\n"
    assert result.stdout.splitlines()[1:] == ["[RUN_OUTPUT: shown=0 omitted=0 filtered=0]"]
    quiet = _python(code, "-q")
    assert quiet.stderr == f"{warning}\n{error}\n"


def test_strict_counts_a_relayed_warning_even_when_the_command_passed() -> None:
    warning = AdvisoryError("drift", code="OVERRIDE_DRIFT", level=Level.WARNING).render()
    code = f"print({warning!r})"
    assert _python(code).exit_code == 0
    strict = _python(code, "--strict")
    assert strict.exit_code == 1 and strict.stderr == f"{warning}\n"


def test_the_output_options_reach_the_command_as_environment() -> None:
    code = "import os, sys; print(*(os.environ[n] for n in ('DEVKIT_QUIET', 'DEVKIT_VERBOSE', 'DEVKIT_STRICT'))); sys.exit(1)"
    assert _python(code, "-q", "--strict").stdout.splitlines()[-1] == "1 0 1"
    # A flag wins over the environment, for the command too.
    assert _python(code, "-v", env={"DEVKIT_QUIET": "1"}).stdout.splitlines()[-1] == "0 1 0"


def test_options_after_the_command_belong_to_it() -> None:
    result = _run(PY, "-c", "import sys; print(sys.argv[1:]); sys.exit(1)", "-q", "--format", "json")
    assert result.exit_code == 1
    assert result.stdout.splitlines()[-1] == "['-q', '--format', 'json']"


def test_json_is_one_object() -> None:
    result = _python("import sys; print('2 failed in 0.1s'); sys.exit(1)", "--format", "json")
    data = json.loads(result.stdout)
    assert data["outcome"] == "failed" and data["exit_code"] == 1
    assert data["command"][1:] == ["-c", "import sys; print('2 failed in 0.1s'); sys.exit(1)"]
    assert data["summaries"] == ["2 failed in 0.1s"] and data["output"] == "2 failed in 0.1s\n"
    assert data["omitted"] == {"summaries": 0, "failures": 0, "warnings": 0, "advisories": 0, "output": 0}
    assert data["notices"] == [] and data["advisories"] == [] and data["last_lines"] == []
    passed = json.loads(_python("pass", "--format", "json").stdout)
    assert passed["outcome"] == "passed" and passed["output"] is None and passed["last_lines"] == []


def test_a_slow_command_notice_follows_the_result_and_quiet_hides_it() -> None:
    code = "import time; time.sleep(0.2)"
    result = _python(code, "--slow-after", "0.1")
    assert result.exit_code == 0 and result.stderr.startswith("[NOTICE] (RUN_SLOW_COMMAND) ")
    assert _python(code, "-q", "--slow-after", "0.1").stderr == ""
    assert _python(code, "--strict", "--slow-after", "0.1").exit_code == 0  # a notice never fails a run


def test_a_command_that_cannot_start_exits_2() -> None:
    result = _run("--", "devkit-no-such-command")
    assert result.exit_code == 2
    assert result.stderr.startswith("[ERROR]  (RUN_COMMAND_NOT_STARTED) cannot start 'devkit-no-such-command'")


def test_a_removed_current_directory_is_an_input_error(tmp_path, monkeypatch) -> None:
    gone = tmp_path / "gone"
    gone.mkdir()
    monkeypatch.chdir(gone)
    gone.rmdir()
    result = _run("--", "true")
    assert result.exit_code == 2
    assert result.stderr.startswith("[ERROR]  (RUN_COMMAND_NOT_STARTED) cannot start 'true': working directory ")
    assert "the current directory no longer exists" in result.stderr


def test_invalid_slow_after_is_an_argument_error() -> None:
    for value in ("-1", "inf", "nan"):
        result = _run("--slow-after", value, "--", "true")
        assert result.exit_code == 2 and "(ARGUMENT_INVALID) --slow-after" in result.stderr


def test_a_command_is_required() -> None:
    assert _run().exit_code == 2


def test_verbose_reports_how_much_of_the_output_the_view_shows() -> None:
    result = _python("print('x' * 999)", "-v")
    assert "[RUN_LAST_LINE: " in result.stdout
    assert re.search(r"^\[INFO\] .*showed \d+ characters for 1000 of output \(\d+%\)$", result.stderr, re.MULTILINE)
    assert "showed" not in _python("print('x' * 999)").stderr


@pytest.mark.parametrize("signum", [signal.SIGINT, signal.SIGTERM, signal.SIGHUP])
def test_an_interrupted_run_reports_its_log_and_exits_128_plus_the_signal(tmp_path: Path, signum: int) -> None:
    started = tmp_path / "started"
    entry = "from devkit.compact.cli import run_cmd; run_cmd()"
    command = ["sh", "-c", f'echo partial; echo $$ > "{started}"; exec sleep 60']
    runner = subprocess.Popen(
        [PY, "-c", entry, "--", *command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=tmp_path,
        env={**os.environ, "TMPDIR": tempfile.gettempdir()},  # the test's own, as for the runs in this process
    )
    try:
        deadline = time.monotonic() + 30
        while not started.exists() or not started.read_text().strip():
            assert time.monotonic() < deadline and runner.poll() is None, "the command did not start"
            time.sleep(0.01)
        runner.send_signal(signum)
        stdout, stderr = runner.communicate(timeout=30)
    finally:
        runner.kill()
    assert runner.returncode == 128 + signum, stderr
    (line,) = stdout.splitlines()
    match = re.fullmatch(r'\[RUN: ".*" outcome=interrupted exit=143 log=(\S+)\]', line)
    assert match and Path(match[1]).read_text() == "partial\n"
    with pytest.raises(ProcessLookupError):  # the command was stopped with the run
        os.kill(int(started.read_text()), 0)
