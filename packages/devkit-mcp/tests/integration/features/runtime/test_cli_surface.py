"""Public discovery omits protocol entrypoints while preserving explicit transport invocation."""

import importlib
import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit_mcp.features.runtime.cli.app import cli


def test_mcp_help_and_internal_serve_are_separate() -> None:
    runner = CliRunner()
    help_result = runner.invoke(cli, ["--help"])
    assert help_result.exit_code == 0
    assert "  serve " not in help_result.stdout and "  config " not in help_result.stdout
    assert runner.invoke(cli, ["serve", "--help"]).exit_code == 0
    assert runner.invoke(cli, ["config"]).exit_code == 2


def test_descriptor_view_is_read_only_and_honors_explicit_executable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = importlib.import_module("devkit_mcp.features.runtime.cli.registration")

    @dataclass
    class Descriptor:
        command: str

    observed = []

    def descriptor(_self, root, *, executable=None):
        assert executable is not None
        observed.append((root, executable))
        return Descriptor(executable)

    monkeypatch.setattr(module.BuildLaunchDescriptorUseCase, "execute", descriptor)
    monkeypatch.setattr(
        module.registration.InspectMcpUseCase,
        "execute",
        lambda *_: pytest.fail("descriptor view must not inspect registrations"),
    )
    runner = CliRunner()
    result = runner.invoke(
        cli, ["status", "--descriptor", "--executable", "/runtime/python", "-w", str(tmp_path), "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["descriptor"] == {"command": "/runtime/python"}
    assert observed == [(tmp_path, "/runtime/python")]
    result = runner.invoke(cli, ["status", "--executable", "/runtime/python", "-w", str(tmp_path), "--format", "json"])
    assert result.exit_code == 2 and json.loads(result.stdout)["error"]["code"] == "ARGUMENT_INVALID"
