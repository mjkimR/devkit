"""A tool's commands through ``devkit_cli.Boundary``: the output contract of ``ARCH-08-1-agent-output``."""

from __future__ import annotations

import logging
import subprocess
import sys
import textwrap

import click
import pytest
from devkit.advisory import AdvisoryError, ExitCode, Level
from devkit_cli import FORMAT_OPTION, Boundary, Reported, echo_json, echo_notices, exit_on_warnings
from devkit_cli.testing import invoke

boundary = Boundary("mytool")


class ThingMissingError(AdvisoryError):
    code = "THING_MISSING"
    exit_code = ExitCode.FINDINGS


WARNING = AdvisoryError("upstream changed", code="DRIFTED", level=Level.WARNING)
NOTICE = AdvisoryError("a bundle is not selected", code="UNSELECTED", level=Level.NOTICE)


@click.command()
@FORMAT_OPTION
@boundary
def failing(output_format: str) -> None:
    echo_notices([NOTICE])
    raise ThingMissingError("thing.toml is missing")


@click.command()
@boundary
def reporting() -> None:
    click.echo("[SCAN: files=1]")
    echo_notices([NOTICE, WARNING])
    exit_on_warnings([NOTICE, WARNING])


@click.command()
@boundary
def logging_command() -> None:
    logging.getLogger("mytool.scan").debug("checked 3 files")
    click.echo("[OK: done]")


@click.command()
@boundary
def crashing() -> None:
    raise RuntimeError("boom")


@click.command()
@boundary(json_only=True)
def json_only() -> None:
    raise ThingMissingError("thing.toml is missing")


@click.command()
@FORMAT_OPTION
@boundary
def reported(output_format: str) -> None:
    error = ThingMissingError("thing.toml is missing")
    echo_json({"errors": [error.to_dict()]})
    raise Reported(error)


def test_a_failure_is_one_advisory_block_and_its_exit_code() -> None:  # AC-01
    outcome = invoke(failing)
    assert (outcome.exit_code, outcome.stdout) == (1, "")
    assert outcome.stderr.count("(THING_MISSING)") == 1
    assert outcome.codes() == ["UNSELECTED", "THING_MISSING"]


def test_json_mode_carries_the_error_and_the_notices_in_one_document() -> None:  # AC-02
    outcome = invoke(failing, ["--format", "json"])
    document = outcome.json()
    assert (outcome.exit_code, outcome.stderr) == (1, "")
    assert document["error"]["code"] == "THING_MISSING"
    assert [notice["code"] for notice in document["notices"]] == ["UNSELECTED"]


def test_json_only_and_reported_errors_keep_one_document() -> None:
    only = invoke(json_only)
    assert (only.exit_code, only.stderr, only.json()["error"]["code"]) == (1, "", "THING_MISSING")
    text = invoke(reported)
    assert text.codes() == ["THING_MISSING"] and text.exit_code == 1
    as_json = invoke(reported, ["--format", "JSON"])
    assert as_json.json() == {"errors": [ThingMissingError("thing.toml is missing").to_dict()]}
    assert as_json.stderr == ""


def test_output_options_follow_the_tool_prefix() -> None:  # AC-03
    plain = invoke(reporting)
    assert (plain.exit_code, plain.codes()) == (0, ["DRIFTED", "UNSELECTED"])  # warnings first
    quiet = invoke(reporting, env={"MYTOOL_QUIET": "1"})
    assert (quiet.exit_code, quiet.codes()) == (0, ["DRIFTED"])
    assert invoke(reporting, env={"MYTOOL_STRICT": "1"}).exit_code == 1
    assert invoke(reporting, ["--strict"]).exit_code == 1
    assert invoke(reporting, env={"MYTOOL_STRICT": "yes"}).exit_code == 0  # only exactly "1" turns it on
    assert invoke(reporting, env={"DEVKIT_STRICT": "1"}).exit_code == 0  # another tool's variable


def test_quiet_and_verbose_together_are_an_argument_error() -> None:  # AC-03
    flags = invoke(reporting, ["-q", "-v"])
    assert (flags.exit_code, flags.codes(), flags.stdout) == (2, ["ARGUMENT_INVALID"], "")
    env = invoke(reporting, env={"MYTOOL_QUIET": "1", "MYTOOL_VERBOSE": "1"})
    assert env.codes() == ["ARGUMENT_INVALID"] and "MYTOOL_QUIET=1 and MYTOOL_VERBOSE=1" in env.stderr
    assert invoke(reporting, ["-q"], env={"MYTOOL_VERBOSE": "1"}).exit_code == 0  # a flag wins


def test_verbose_prints_the_tool_log_records() -> None:  # AC-04
    verbose = invoke(logging_command, ["-v"])
    assert "[INFO]   scan: checked 3 files" in verbose.stderr.splitlines()
    assert "[INFO]" not in invoke(logging_command).stderr
    assert "[INFO]" not in invoke(logging_command, env={"MYTOOL_VERBOSE": "0"}).stderr


def test_an_unexpected_exception_is_unexpected_error_with_its_traceback_under_verbose() -> None:  # AC-05
    crash = invoke(crashing)
    assert (crash.exit_code, crash.codes()) == (2, ["UNEXPECTED_ERROR"])
    assert "RuntimeError: boom" in crash.stderr and "[INFO]" not in crash.stderr
    verbose = invoke(crashing, ["-v"])
    assert "[INFO]   cli: unexpected error" in verbose.stderr
    assert verbose.stderr.index("[INFO]") < verbose.stderr.index("[ERROR]")


def test_the_boundary_log_can_be_the_tool_own_logger() -> None:
    own = Boundary("mytool", log=logging.getLogger("mytool.adapters.cli"))

    @click.command()
    @own
    def crash() -> None:
        raise RuntimeError("boom")

    assert "[INFO]   adapters.cli: unexpected error" in invoke(crash, ["-v"]).stderr


def test_a_closed_reader_ends_the_command_with_exit_2_and_no_advisory(tmp_path) -> None:  # AC-05
    script = tmp_path / "tool.py"
    script.write_text(
        textwrap.dedent(
            """
            import click
            from devkit_cli import Boundary

            @click.command()
            @Boundary("mytool")
            def main() -> None:
                for index in range(200000):
                    click.echo(f"[LINE: {index}]")

            main()
            """
        )
    )
    process = subprocess.Popen([sys.executable, str(script)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert process.stdout is not None
    process.stdout.readline()
    process.stdout.close()
    _, stderr = process.communicate(timeout=30)
    assert (process.returncode, stderr) == (2, "")


def test_output_is_utf8_whatever_the_locale(tmp_path) -> None:
    script = tmp_path / "tool.py"
    script.write_text(
        "import click\nfrom devkit_cli import Boundary\n\n"
        "@click.command()\n@Boundary('mytool')\ndef main() -> None:\n    click.echo('[PATH: 문서.md]')\n\nmain()\n"
    )
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C", "PYTHONIOENCODING": "ascii"}
    result = subprocess.run([sys.executable, str(script)], capture_output=True, env=env, check=False)
    assert (result.returncode, result.stdout) == (0, "[PATH: 문서.md]\n".encode())


@pytest.mark.parametrize(
    ("name", "prefix", "variable"),
    [("mytool", None, "MYTOOL_QUIET"), ("my-tool", None, "MY_TOOL_QUIET"), ("mytool", "MT", "MT_QUIET")],
)
def test_environment_names_derive_from_the_tool(name: str, prefix: str | None, variable: str) -> None:
    assert Boundary(name, env_prefix=prefix).quiet_env == variable


@pytest.mark.parametrize(("name", "prefix"), [("", None), (" tool", None), ("mytool", "1X"), ("mytool", "MY TOOL")])
def test_invalid_names_are_refused(name: str, prefix: str | None) -> None:
    with pytest.raises(ValueError):
        Boundary(name, env_prefix=prefix)


def test_help_names_the_tool_variables() -> None:
    help_text = invoke(reporting, ["--help"]).stdout
    assert all(variable in help_text for variable in ("MYTOOL_QUIET=1", "MYTOOL_VERBOSE=1", "MYTOOL_STRICT=1"))
