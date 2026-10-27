"""``devkit_dist.adapters.cli``: the plumbing every command group shares, and the root command line."""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import click
import pytest
from click.testing import CliRunner
from devkit.advisory import AdvisoryError, ExitCode, Level
from devkit_core.base.errors import ArgumentError
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    OutputSettings,
    Reported,
    boundary,
    echo_json,
    echo_notices,
    exit_on_problems,
    exit_on_warnings,
    highest_exit_code,
    output_settings,
    report_exit_code,
    resolve_root,
    workspace_option,
)
from devkit_dist.base.errors import DevkitRootNestedError
from devkit_dist.cli import cli as root_cli


class Finding(AdvisoryError):
    code = "TEST_FINDING"
    exit_code = ExitCode.FINDINGS


@click.command()
@workspace_option()
@FORMAT_OPTION
@click.option("--mode", default="ok")
@boundary
def probe(workspace_root: str | None, output_format: str, mode: str) -> None:
    root = resolve_root(workspace_root)
    if mode == "fail":
        raise Finding("refused")
    if mode == "reported":
        echo_json({"result": "partial"})
        raise Reported(AdvisoryError("after the result"))
    if mode == "problems":
        echo_json({"errors": []})
        exit_on_problems([Finding("one"), AdvisoryError("two")])
    if mode == "report":
        echo_json({"errors": []})
        exit_on_problems([Finding("one"), AdvisoryError("two")], report=True)
    if mode == "crash":
        raise RuntimeError("boom")
    if mode == "notices-then-fail":  # warnings collected before the command fails
        echo_notices([AdvisoryError("left behind", code="TEST_WARNING", level=Level.WARNING)])
        raise Finding("refused")
    if mode == "notices":
        notices = [
            AdvisoryError("fyi", code="TEST_NOTICE", level=Level.NOTICE),
            AdvisoryError("left behind", code="TEST_WARNING", level=Level.WARNING),
        ]
        echo_json({"notices": [n.to_dict() for n in notices]})
        echo_notices(notices)
        exit_on_warnings(notices)
        return
    if mode == "log":
        logging.getLogger("devkit.probe").info("checked %d files", 3)
        try:
            raise ValueError("kept for -v")
        except ValueError:
            logging.getLogger("devkit.probe").exception("a rule raised")
        echo_json({"logged": True})
        return
    if mode == "settings":
        echo_json(vars(output_settings()))
        return
    if mode == "surrogate":  # a Git path decoded with surrogateescape
        name = b"bad\xffname.md".decode("utf-8", errors="surrogateescape")
        if output_format == "json":
            echo_json({"files": [name, "ü"]})
        else:
            click.echo(f"[FILE: {name} ü]")
        return
    echo_json({"root": str(root), "text": "ü"})


def _invoke(*args: str):
    return CliRunner().invoke(probe, list(args))


def test_success_prints_one_utf8_object(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--format", "JSON")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"root": str(tmp_path.resolve()), "text": "ü"}
    # Text stays as written: an escaped "ü" costs the agent context and has to be decoded back.
    assert '"text":"ü"' in result.stdout and "\\u00fc" not in result.stdout


def test_surrogate_escaped_paths_print_deterministically(tmp_path: Path) -> None:
    as_json = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "surrogate")
    assert as_json.exit_code == 0, as_json.stderr
    # The lone surrogate becomes a \udcff escape, which is valid JSON; other text stays UTF-8.
    assert json.loads(as_json.stdout) == {"files": ["bad\udcffname.md", "ü"]}
    assert as_json.stdout_bytes == '{"files":["bad\\udcffname.md","ü"]}\n'.encode()  # compact: no indentation
    as_text = _invoke("-w", str(tmp_path), "--mode", "surrogate")
    assert as_text.exit_code == 0, as_text.stderr
    assert as_text.stdout_bytes == "[FILE: bad\\udcffname.md ü]\n".encode()


def _run_python(code: str, **env: str) -> subprocess.CompletedProcess[bytes]:
    """Run ``code`` in a fresh interpreter with the given environment additions."""
    assert code.isascii(), "a C locale on Linux cannot pass non-ASCII -c code (macOS can, so check here)"
    return subprocess.run([sys.executable, "-c", code], capture_output=True, env={**os.environ, **env}, timeout=60)


# ASCII only, non-ASCII text as escapes: under a C locale on Linux, CPython decodes ``-c`` with ASCII and refuses
# any other byte before the probe runs.
_PROBE = textwrap.dedent("""
    import click
    from devkit_dist.adapters.cli import FORMAT_OPTION, boundary, echo_json

    @click.command()
    @FORMAT_OPTION
    @click.option("--mode")
    @boundary
    def cmd(output_format, mode):
        if mode == "advisory":
            raise RuntimeError("caf\\u00e9")
        if mode == "lines":
            for i in range(200_000):
                click.echo(f"[LINE: {i}]")
        if mode == "json":
            echo_json({"x": ["y" * 100] * 100_000})
        if mode == "surrogate":
            echo_json({"files": [b"bad\\xffname.md".decode("utf-8", errors="surrogateescape"), "caf\\u00e9"]})
""")


def test_output_is_utf8_whatever_the_locale() -> None:
    script = _PROBE + "cmd(['--mode', 'advisory', '--format', 'json'])\n"
    result = _run_python(script, LC_ALL="C", PYTHONIOENCODING="latin-1", PYTHONUTF8="0")
    assert result.returncode == 2
    assert json.loads(result.stdout)["error"]["message"] == "RuntimeError: café"
    assert '"RuntimeError: café"'.encode() in result.stdout  # JSON text in UTF-8, not an escape
    assert result.stderr == b""  # the JSON document is the whole report
    text = _run_python(_PROBE + "cmd(['--mode', 'advisory'])\n", LC_ALL="C", PYTHONIOENCODING="latin-1", PYTHONUTF8="0")
    assert text.stderr.decode("utf-8").startswith("[ERROR]  (UNEXPECTED_ERROR) RuntimeError: café\n[ACTION] ")
    assert "— " in text.stderr.decode("utf-8")  # the ACTION text's em dash, in UTF-8


def test_json_with_a_lone_surrogate_stays_valid_whatever_the_locale() -> None:
    script = _PROBE + "cmd(['--mode', 'surrogate', '--format', 'json'])\n"
    result = _run_python(script, LC_ALL="C", PYTHONIOENCODING="latin-1", PYTHONUTF8="0")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"files": ["bad\udcffname.md", "café"]}
    assert b'"bad\\udcffname.md"' in result.stdout and '"café"'.encode() in result.stdout


@pytest.mark.parametrize("mode", ["lines", "json"])
def test_a_closed_stdout_ends_the_command_quietly(mode: str) -> None:
    process = subprocess.Popen(
        [sys.executable, "-c", _PROBE + f"cmd(['--mode', '{mode}'])\n"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None and process.stderr is not None
    process.stdout.read(1)  # compact JSON is one long line, so read a byte rather than a line
    process.stdout.close()  # the reader goes away, as `devkit ... | head -c 1` does
    stderr = process.stderr.read()
    assert process.wait(timeout=60) == int(ExitCode.ERROR)
    assert stderr == b""  # no advisory, no "Exception ignored" noise


def test_errors_go_to_exactly_one_channel(tmp_path: Path) -> None:
    # A host that merges stdout and stderr must read each advisory once: JSON on stdout, or the block on stderr.
    as_json = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "fail")
    assert as_json.exit_code == int(ExitCode.FINDINGS) and as_json.stderr == ""
    error = json.loads(as_json.stdout)["error"]
    assert error["code"] == "TEST_FINDING" and error["advisory"]["action"].startswith("HALT — ")
    as_text = _invoke("-w", str(tmp_path), "--format", "text", "--mode", "fail")
    assert as_text.exit_code == int(ExitCode.FINDINGS) and as_text.stdout == ""
    assert as_text.stderr.startswith("[ERROR]  (TEST_FINDING) refused\n[ACTION] HALT — ")


def test_notices_collected_before_a_json_failure_are_in_the_error_document(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "notices-then-fail")
    assert result.exit_code == int(ExitCode.FINDINGS) and result.stderr == ""
    document = json.loads(result.stdout)
    assert document["error"]["code"] == "TEST_FINDING"
    assert [notice["code"] for notice in document["notices"]] == ["TEST_WARNING"]
    as_text = _invoke("-w", str(tmp_path), "--mode", "notices-then-fail")
    assert (
        as_text.stderr.startswith("[WARN]   (TEST_WARNING) left behind") and "[ERROR]  (TEST_FINDING)" in as_text.stderr
    )


def test_unexpected_errors_and_a_missing_workspace_root(tmp_path: Path) -> None:
    crash = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "crash")
    assert crash.exit_code == 2 and json.loads(crash.stdout)["error"]["code"] == "UNEXPECTED_ERROR"
    missing = _invoke("-w", str(tmp_path / "nope"), "--format", "json")
    assert missing.exit_code == 2
    error = json.loads(missing.stdout)["error"]
    assert (error["code"], error["advisory"]["mode"]) == ("ARGUMENT_INVALID", "INPUT_ERROR")
    assert error["message"].startswith("--workspace-root") and missing.stderr == ""


@pytest.mark.parametrize("value", ["", "  "])
def test_an_empty_workspace_root_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.chdir(tmp_path)
    result = _invoke("-w", value, "--format", "json")
    assert result.exit_code == 2 and json.loads(result.stdout)["error"]["code"] == "ARGUMENT_INVALID"
    assert json.loads(result.stdout)["error"]["message"] == "--workspace-root is empty"


def test_a_looping_workspace_root_is_an_argument_error(tmp_path: Path) -> None:
    (tmp_path / "a").symlink_to(tmp_path / "b")
    (tmp_path / "b").symlink_to(tmp_path / "a")
    result = _invoke("-w", str(tmp_path / "a"), "--format", "json")
    assert result.exit_code == 2 and json.loads(result.stdout)["error"]["code"] == "ARGUMENT_INVALID"
    assert "cannot be resolved" in json.loads(result.stdout)["error"]["message"]


def test_resolve_root_applies_require_devkit_root_to_the_workspace_root(repo: Path) -> None:
    (repo / ".devkit").mkdir()
    (repo / "sub").mkdir()
    assert resolve_root(str(repo)) == repo
    with pytest.raises(ArgumentError, match="is inside the Git work tree"):
        resolve_root(str(repo / "sub"))
    (repo / ".devkit").rmdir()
    (repo / "sub/.devkit").mkdir()
    with pytest.raises(DevkitRootNestedError):
        resolve_root(repo / "sub")


def test_a_reported_error_keeps_stdout_to_the_result(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "reported")
    assert result.exit_code == 2 and json.loads(result.stdout) == {"result": "partial"}
    assert result.stderr == ""  # the JSON result carries the error; text mode renders it
    as_text = _invoke("-w", str(tmp_path), "--mode", "reported")
    assert as_text.exit_code == 2 and "(GENERAL_ERROR) after the result" in as_text.stderr


def test_collected_problems_exit_with_the_highest_code(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "problems")
    assert result.exit_code == 2 and json.loads(result.stdout) == {"errors": []} and result.stderr == ""
    as_text = _invoke("-w", str(tmp_path), "--mode", "problems")
    assert "(TEST_FINDING) one" in as_text.stderr and "(GENERAL_ERROR) two" in as_text.stderr
    assert highest_exit_code([]) == 0
    assert highest_exit_code([Finding("x")]) == 1
    assert highest_exit_code([Finding("x"), ArgumentError("y")]) == 2


def test_status_reports_with_problems_exit_one_whatever_their_codes(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "report")
    assert result.exit_code == 1 and json.loads(result.stdout) == {"errors": []} and result.stderr == ""
    as_text = _invoke("-w", str(tmp_path), "--mode", "report")
    assert as_text.exit_code == 1 and "(GENERAL_ERROR) two" in as_text.stderr
    assert report_exit_code([]) == 0
    assert report_exit_code([ArgumentError("y")]) == 1


def test_version_lives_only_on_the_root_group() -> None:
    runner = CliRunner()
    version = runner.invoke(root_cli, ["--version"])
    assert version.exit_code == 0 and re.fullmatch(r"\[VERSION: devkit \S+\]\n", version.stdout)
    for group in ("host", "override", "bundle"):
        result = runner.invoke(root_cli, [group, "--version"])
        assert result.exit_code == 2 and "No such option" in result.output
    names = set(root_cli.list_commands(click.Context(root_cli)))
    assert {"sync", "status", "list", "override", "bundle", "host"} <= names


def test_internal_commands_are_callable_but_not_discovered_and_archive_cli_is_removed() -> None:
    runner = CliRunner()
    root = runner.invoke(root_cli, ["--help"])
    assert root.exit_code == 0 and "  recover " not in root.stdout
    assert runner.invoke(root_cli, ["recover", "--help"]).exit_code == 0
    host = runner.invoke(root_cli, ["host", "--help"])
    assert "  hook " not in host.stdout
    assert runner.invoke(root_cli, ["host", "hook", "--help"]).exit_code == 0
    bundle = runner.invoke(root_cli, ["bundle", "--help"])
    assert "validate" in bundle.stdout and "plan" in bundle.stdout and "  build " not in bundle.stdout
    assert runner.invoke(root_cli, ["bundle", "build"]).exit_code == 2


def _leaf_commands(command: click.Command, path: str = "devkit"):
    if isinstance(command, click.Group):
        ctx = click.Context(command)
        for name in command.list_commands(ctx):
            sub = command.get_command(ctx, name)
            assert sub is not None, f"{path} {name}"
            yield from _leaf_commands(sub, f"{path} {name}")
    else:
        yield path, command


def test_every_command_has_the_output_options() -> None:
    missing = [
        path
        for path, command in _leaf_commands(root_cli)
        if not {"quiet", "verbose", "strict"} <= {param.name for param in command.params}
    ]
    # Native host protocol transport emits only host JSON; verbosity and strictness cannot alter its response.
    assert missing == ["devkit host hook"]


def test_notices_follow_the_result_and_respect_quiet_and_strict(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--mode", "notices")
    assert result.exit_code == 0 and len(json.loads(result.stdout)["notices"]) == 2
    # Collected as notice, warning: stderr puts the warning first, JSON keeps the collected order.
    assert result.stderr.startswith("[WARN]   (TEST_WARNING) left behind\n[ACTION] CONTINUE — ")
    assert [n["code"] for n in json.loads(result.stdout)["notices"]] == ["TEST_NOTICE", "TEST_WARNING"]
    assert "[NOTICE] (TEST_NOTICE) fyi\n[ACTION] NOTE — " in result.stderr
    quiet = _invoke("-w", str(tmp_path), "--mode", "notices", "-q")
    assert quiet.exit_code == 0 and "TEST_WARNING" in quiet.stderr and "TEST_NOTICE" not in quiet.stderr
    assert json.loads(quiet.stdout) == json.loads(result.stdout)  # JSON is never filtered
    assert _invoke("-w", str(tmp_path), "--mode", "notices", "--strict").exit_code == 1
    assert CliRunner().invoke(probe, ["--mode", "notices"], env={"DEVKIT_STRICT": "1"}).exit_code == 1


def test_quiet_and_verbose_conflict_and_flags_win_over_the_environment(tmp_path: Path) -> None:
    both = _invoke("-w", str(tmp_path), "--format", "json", "-q", "-v")
    assert both.exit_code == 2 and json.loads(both.stdout)["error"]["code"] == "ARGUMENT_INVALID"
    assert json.loads(both.stdout)["error"]["message"] == "--quiet and --verbose cannot be combined"
    env = {"DEVKIT_QUIET": "1", "DEVKIT_VERBOSE": "1"}
    from_env = CliRunner().invoke(probe, ["--mode", "settings"], env=env)
    assert from_env.exit_code == 2 and "DEVKIT_QUIET=1 and DEVKIT_VERBOSE=1 cannot be combined" in from_env.stderr
    flag = CliRunner().invoke(probe, ["--mode", "settings", "-q"], env=env)
    assert json.loads(flag.stdout) == {"quiet": True, "verbose": False, "strict": False, "json": False}
    off = CliRunner().invoke(probe, ["--mode", "settings"], env={"DEVKIT_VERBOSE": "true"})
    # Only "1" turns an option on.
    assert json.loads(off.stdout) == {"quiet": False, "verbose": False, "strict": False, "json": False}
    assert output_settings() == OutputSettings()  # reset after the command


def test_logs_are_silent_by_default_and_info_lines_under_verbose(tmp_path: Path) -> None:
    quiet = _invoke("-w", str(tmp_path), "--mode", "log")
    assert quiet.exit_code == 0 and quiet.stderr == ""  # the NullHandler keeps logger.exception off stderr
    verbose = _invoke("-w", str(tmp_path), "--mode", "log", "-v")
    lines = verbose.stderr.splitlines()
    assert lines[:2] == ["[INFO]   probe: checked 3 files", "[INFO]   probe: a rule raised"]
    assert lines[2] == "         Traceback (most recent call last):"
    assert all(line.startswith(("[INFO]   ", " " * 9)) for line in lines)
    assert not logging.getLogger("devkit").handlers[1:]  # the stderr handler is removed after the command
    crash = _invoke("-w", str(tmp_path), "--mode", "crash", "-v")
    assert (
        "[INFO]   devkit_dist.adapters.cli: unexpected error" in crash.stderr and "RuntimeError: boom" in crash.stderr
    )
    assert crash.stderr.index("[INFO]   devkit_dist.adapters.cli:") < crash.stderr.index(
        "[ERROR]  (UNEXPECTED_ERROR) RuntimeError: boom"
    )


def test_stdout_never_uses_an_advisory_sentinel_as_a_kind() -> None:
    reserved = re.compile(r"\[(ERROR|WARN|WARNING|NOTICE|INFO|DEBUG|ACTION|WHEN|TARGET|FIX|REPORT|DETAIL):")
    source = Path(__file__).parents[3] / "src/devkit_dist"
    offenders = [
        f"{path.relative_to(source)}:{number}"
        for path in sorted(source.rglob("*.py"))
        for number, line in enumerate(path.read_text("utf-8").splitlines(), 1)
        if reserved.search(line)
    ]
    assert offenders == []
