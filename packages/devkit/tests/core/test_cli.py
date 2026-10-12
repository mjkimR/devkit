"""``devkit.core.cli``: the plumbing every command group shares, and the root command line."""

from __future__ import annotations

import json
from pathlib import Path

import click
import pytest
from click.testing import CliRunner
from devkit.advisory import AdvisoryError, ExitCode
from devkit.cli import cli as root_cli
from devkit.core.cli import (
    FORMAT_OPTION,
    Reported,
    boundary,
    echo_json,
    exit_on_problems,
    highest_exit_code,
    report_exit_code,
    resolve_root,
    workspace_option,
)
from devkit.core.errors import ArgumentError


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
    echo_json({"root": str(root), "text": "ü"})


def _invoke(*args: str):
    return CliRunner().invoke(probe, list(args))


def test_success_prints_one_object_without_escaping(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--format", "JSON")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"root": str(tmp_path.resolve()), "text": "ü"}
    assert '"ü"' in result.stdout


@pytest.mark.parametrize(("output_format", "on_stdout"), [("json", True), ("text", False)])
def test_errors_exit_with_their_code_and_print_json_only_in_json_mode(
    tmp_path: Path, output_format: str, on_stdout: bool
) -> None:
    result = _invoke("-w", str(tmp_path), "--format", output_format, "--mode", "fail")
    assert result.exit_code == int(ExitCode.FINDINGS)
    assert result.stderr.startswith("[ERROR]  (TEST_FINDING) refused")
    assert (json.loads(result.stdout)["error"]["code"] == "TEST_FINDING") if on_stdout else result.stdout == ""


def test_unexpected_errors_and_a_missing_workspace_root(tmp_path: Path) -> None:
    crash = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "crash")
    assert crash.exit_code == 2 and json.loads(crash.stdout)["error"]["code"] == "UNEXPECTED_ERROR"
    missing = _invoke("-w", str(tmp_path / "nope"), "--format", "json")
    assert missing.exit_code == 2
    error = json.loads(missing.stdout)["error"]
    assert (error["code"], error["advisory"]["mode"]) == ("ARGUMENT_INVALID", "INPUT_ERROR")
    assert missing.stderr.startswith("[ERROR]  (ARGUMENT_INVALID) --workspace-root")


def test_a_reported_error_keeps_stdout_to_the_result(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "reported")
    assert result.exit_code == 2 and json.loads(result.stdout) == {"result": "partial"}
    assert "after the result" in result.stderr


def test_collected_problems_exit_with_the_highest_code(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "problems")
    assert result.exit_code == 2 and json.loads(result.stdout) == {"errors": []}
    assert "(TEST_FINDING) one" in result.stderr and "(GENERAL_ERROR) two" in result.stderr
    assert highest_exit_code([]) == 0
    assert highest_exit_code([Finding("x")]) == 1
    assert highest_exit_code([Finding("x"), ArgumentError("y")]) == 2


def test_status_reports_with_problems_exit_one_whatever_their_codes(tmp_path: Path) -> None:
    result = _invoke("-w", str(tmp_path), "--format", "json", "--mode", "report")
    assert result.exit_code == 1 and json.loads(result.stdout) == {"errors": []}
    assert "(GENERAL_ERROR) two" in result.stderr
    assert report_exit_code([]) == 0
    assert report_exit_code([ArgumentError("y")]) == 1


def test_version_lives_only_on_the_root_group() -> None:
    runner = CliRunner()
    assert runner.invoke(root_cli, ["--version"]).exit_code == 0
    for group in ("rules", "workflow", "gate"):
        result = runner.invoke(root_cli, [group, "--version"])
        assert result.exit_code == 2 and "No such option" in result.output
    assert {"sync", "status", "list", "override", "bundle", "rules", "workflow", "gate"} <= set(root_cli.commands)
