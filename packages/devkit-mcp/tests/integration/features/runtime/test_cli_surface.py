"""Public discovery omits protocol entrypoints while preserving explicit transport invocation."""

import importlib
import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import AdvisoryError, Level
from devkit_cli.testing import invoke
from devkit_dist.features.host.usecases.registrations import (
    RegistrationError,
    RegistrationPlan,
    RegistrationUnavailable,
)
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
    assert result.exit_code == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["descriptor"] == {"command": "/runtime/python"}
    assert observed == [(tmp_path, "/runtime/python")]
    result = runner.invoke(cli, ["status", "--executable", "/runtime/python", "-w", str(tmp_path), "--format", "json"])
    assert result.exit_code == 2 and json.loads(result.stdout)["error"]["code"] == "ARGUMENT_INVALID"


def _warning() -> AdvisoryError:
    return RegistrationUnavailable(".mcp.json: tracked or visible foreign host file left unchanged").with_level(
        Level.WARNING
    )


def _inspection(**overrides) -> dict:
    return {
        "desired": {"claude": {"command": "/runtime/python"}},
        "recorded": ["claude"],
        "project": {
            "claude": {"state": "owned", "collisions": ["user/local"]},
            "codex": {"state": "absent", "collisions": []},
        },
        "package": "installed",
        "runtime": "available",
        "effective": "unknown",
        "connection": "unknown",
        "form": "unknown",
        "trust": "unknown",
        "permissions": "unknown",
        "errors": [],
        "notices": [],
        **overrides,
    }


@pytest.mark.parametrize("command", ["setup", "remove"])
def test_registration_warnings_fail_only_under_strict(
    command: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = importlib.import_module("devkit_mcp.features.runtime.cli.registration")
    planned = RegistrationPlan(tmp_path, None, notices=[_warning()], states={"claude": "unavailable"})
    use_case = module.registration.SetupMcpUseCase if command == "setup" else module.registration.RemoveMcpUseCase
    monkeypatch.setattr(use_case, "execute", lambda *_a, **_k: planned)
    plain = invoke(cli, [command, "-w", str(tmp_path)])
    assert (plain.exit_code, plain.codes()) == (0, ["MCP_REGISTRATION_UNAVAILABLE"])
    assert "[MCP_HOST: claude state=unavailable]" in plain.stdout.splitlines()
    assert invoke(cli, [command, "-w", str(tmp_path), "--strict"]).exit_code == 1
    assert invoke(cli, [command, "-w", str(tmp_path)], env={"DEVKIT_STRICT": "1"}).exit_code == 1


def test_status_text_distinguishes_runtime_and_each_host(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("devkit_mcp.features.runtime.cli.registration")
    monkeypatch.setattr(module.registration.InspectMcpUseCase, "execute", lambda *_: _inspection())
    result = invoke(cli, ["status", "-w", str(tmp_path)])
    assert result.exit_code == 0, result.stderr
    assert result.stdout.splitlines() == [
        "[MCP: action=status package=installed runtime=available]",
        "[MCP_HOST: claude state=owned desired=yes recorded=yes collisions=user/local]",
        "[MCP_HOST: codex state=absent desired=no recorded=no collisions=none]",
    ]


def test_status_reports_a_failed_inspection_as_an_error_with_exit_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = importlib.import_module("devkit_mcp.features.runtime.cli.registration")
    error = RegistrationError(".mcp.json: the devkit entry devkit registered was edited or removed")
    monkeypatch.setattr(
        module.registration.InspectMcpUseCase, "execute", lambda *_: _inspection(errors=[error], notices=[_warning()])
    )
    text = invoke(cli, ["status", "-w", str(tmp_path)])
    assert (text.exit_code, text.codes()) == (1, ["MCP_REGISTRATION_CONFLICT", "MCP_REGISTRATION_UNAVAILABLE"])
    as_json = invoke(cli, ["status", "-w", str(tmp_path), "--format", "json"])
    document = as_json.json()
    assert (as_json.exit_code, as_json.stderr) == (1, "")
    assert [item["code"] for item in document["errors"]] == ["MCP_REGISTRATION_CONFLICT"]
    assert [item["level"] for item in document["notices"]] == ["WARNING"]
    monkeypatch.setattr(module.registration.InspectMcpUseCase, "execute", lambda *_: _inspection(notices=[_warning()]))
    assert invoke(cli, ["status", "-w", str(tmp_path)]).exit_code == 0
    assert invoke(cli, ["status", "-w", str(tmp_path), "--strict"]).exit_code == 1


def _project(root: Path) -> Path:
    import subprocess

    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    (root / ".devkit").mkdir()
    (root / ".devkit/config.toml").write_text("schema = 1\n")
    return root


@pytest.mark.parametrize("command", ["setup", "remove"])
def test_setup_and_remove_refuse_outside_a_checkout_before_any_lock(
    command: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    for args in ([command], [command, "-w", str(outside)]):
        result = invoke(cli, [*args, "--format", "json"])
        assert result.exit_code == 2, result.stdout + result.stderr
        advisory = result.json()["error"]["advisory"]
        assert advisory["mode"] == "INPUT_ERROR" and advisory["target_files"] == ["--workspace-root"]
    assert not (outside / ".devkit").exists()
    project = tmp_path / "plain"
    project.mkdir()
    (project / ".devkit").mkdir()
    result = invoke(cli, [command, "-w", str(project), "--format", "json"])
    assert result.exit_code == 2 and result.json()["error"]["code"] == "MCP_CHECKOUT_REQUIRED"
    assert list((project / ".devkit").iterdir()) == []


def test_setup_fails_when_no_runtime_can_be_registered(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_dist.features.host.usecases import registrations

    root = _project(tmp_path / "repo")

    def unavailable(*_args, **_kwargs):
        raise registrations.RuntimeUnavailable("no verified retained interpreter")

    monkeypatch.setattr(registrations, "provider", unavailable)
    result = invoke(cli, ["setup", "-w", str(root), "--executable", "/nonexistent", "--format", "json"])
    assert result.exit_code == 2, result.stdout + result.stderr
    error = result.json()["error"]
    assert error["code"] == "MCP_RUNTIME_UNAVAILABLE" and error["advisory"]["target_files"] == ["--executable"]


def test_descriptor_text_prints_the_descriptor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from devkit_dist.features.host.usecases.registrations import LaunchDescriptor

    module = importlib.import_module("devkit_mcp.features.runtime.cli.registration")
    launch = LaunchDescriptor("/runtime/python", ("-m", "devkit_dist"), "/base", "/work", "local")
    monkeypatch.setattr(module.BuildLaunchDescriptorUseCase, "execute", lambda *_a, **_k: launch)
    result = invoke(cli, ["status", "--descriptor", "-w", str(tmp_path)])
    assert result.exit_code == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "[MCP_DESCRIPTOR: command=/runtime/python profile=local executor=/base workspace=/work]"
    ]


def test_setup_help_defines_host_as_a_limit() -> None:
    text = CliRunner().invoke(cli, ["setup", "--help"]).output
    assert "Limit registration to these hosts" in " ".join(text.split())
