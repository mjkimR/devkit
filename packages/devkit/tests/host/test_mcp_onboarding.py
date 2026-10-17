"""Registration behavior and isolated Codex CLI checks; no native UI claim."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from copy import deepcopy
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from devkit.cli import cli
from devkit.host.errors import HostMcpRegistrationError, HostMcpRuntimeError
from devkit.host.mcp import onboarding as m
from devkit.host.mcp.configuration import configuration


def entry(root):
    desired = configuration(root)
    return {
        "name": "devkit",
        "enabled": True,
        "transport": {
            "type": "stdio",
            "command": desired["command"],
            "args": desired["args"],
            "env": None,
            "env_vars": [],
            "cwd": None,
        },
    }


@pytest.fixture
def host(tmp_path, monkeypatch):
    state = {"entry": None, "writes": []}

    def codex(root, *args):
        if args[0] == "list":
            return json.dumps([] if state["entry"] is None else [{"name": "devkit"}])
        if args[0] == "get":
            return json.dumps(state["entry"])
        assert args[:3] == ("add", "devkit", "--")
        state["writes"].append(args)
        state["entry"] = entry(root)
        return "host progress must never appear on devkit stdout"

    monkeypatch.setattr(m, "_codex", codex)
    monkeypatch.setattr(m, "_retained", lambda root: None)
    monkeypatch.setattr(m, "_sdk_available", lambda: True)
    return tmp_path, state


def invoke(root, command, *args):
    return CliRunner().invoke(cli, ["host", "mcp", command, "--host", "codex", "-w", str(root), *args])


def test_setup_registers_then_preserves_matching_settings(host):
    root, state = host
    result = invoke(root, "setup", "--format", "json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert data["action"] == "registered" and data["scope"] == "user"
    assert data["connection"] == data["approval_ui"] == data["trust"] == "unknown"
    assert len(state["writes"]) == 1 and result.stderr == ""
    state["entry"]["tool_timeout_sec"] = 90
    original = deepcopy(state["entry"])
    result = invoke(root, "setup", "--format", "json")
    assert json.loads(result.stdout)["action"] == "unchanged"
    assert len(state["writes"]) == 1 and state["entry"] == original


@pytest.mark.parametrize(
    "change", ["command", "args", "env", "env_vars", "cwd", "disabled", "enabled_tools", "disabled_tools", "http"]
)
def test_conflicts_need_explicit_replacement(host, change):
    root, state = host
    saved = entry(root)
    if change == "disabled":
        saved["enabled"] = False
    elif change in {"enabled_tools", "disabled_tools"}:
        saved[change] = ["integration_status"]
    else:
        saved["transport"]["type" if change == "http" else change] = {
            "command": "/foreign/python",
            "args": ["other"],
            "env": {"TOKEN": "never-print-this"},
            "env_vars": ["TOKEN"],
            "cwd": "/other",
            "http": "streamable_http",
        }[change]
    state["entry"] = saved
    result = invoke(root, "setup", "--format", "json")
    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]["code"] == "HOST_MCP_REGISTRATION_CONFLICT"
    assert not state["writes"] and state["entry"] == saved
    assert "never-print-this" not in result.output
    result = invoke(root, "setup", "--replace", "--format", "json")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["action"] == "replaced" and len(state["writes"]) == 1


def test_status_missing_different_matching_and_missing_sdk(host, monkeypatch):
    root, state = host
    result = invoke(root, "status", "--format", "json")
    assert result.exit_code == 1 and json.loads(result.stdout)["state"] == "missing"
    state["entry"] = entry(root)
    result = invoke(root, "status")
    assert result.exit_code == 0 and result.stdout.startswith("[HOST_MCP_STATUS:") and result.stderr == ""
    state["entry"]["enabled"] = False
    result = invoke(root, "status", "--format", "json")
    assert result.exit_code == 1 and json.loads(result.stdout)["state"] == "different"
    state["entry"]["enabled"] = True
    monkeypatch.setattr(m, "_sdk_available", lambda: False)
    result = invoke(root, "status", "--format", "json")
    assert result.exit_code == 1
    assert json.loads(result.stdout)["errors"][0]["code"] == "HOST_MCP_EXTRA_REQUIRED"
    assert not state["writes"]


def test_missing_sdk_prevents_setup(host, monkeypatch):
    root, state = host
    monkeypatch.setattr(m, "_sdk_available", lambda: False)
    result = invoke(root, "setup", "--format", "json")
    assert result.exit_code == 2 and json.loads(result.stdout)["error"]["code"] == "HOST_MCP_EXTRA_REQUIRED"
    assert not state["writes"]


@pytest.mark.parametrize("value", ["broken", "{}", "[{}]", '[{"name":"devkit"},{"name":"devkit"}]'])
def test_invalid_host_responses_cannot_be_mistaken_for_absence(tmp_path, monkeypatch, value):
    monkeypatch.setattr(m, "_codex", lambda *args: value)
    result = invoke(tmp_path, "status", "--format", "json")
    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]["code"] == "HOST_MCP_REGISTRATION_FAILED"


@pytest.mark.parametrize("failure", [OSError("secret"), subprocess.TimeoutExpired("codex", 15), UnicodeError("secret")])
def test_process_failures_are_bounded_and_sanitized(tmp_path, monkeypatch, failure):
    monkeypatch.setattr(m.subprocess, "run", Mock(side_effect=failure))
    with pytest.raises(HostMcpRegistrationError) as exc:
        m._codex(tmp_path, "list", "--json")
    assert "secret" not in str(exc.value)


def test_add_or_verification_failure_never_claims_success(host, monkeypatch):
    root, state = host
    original = m._codex

    def failed_add(root, *args):
        if args[0] == "add":
            raise HostMcpRegistrationError("write failed")
        return original(root, *args)

    monkeypatch.setattr(m, "_codex", failed_add)
    result = invoke(root, "setup", "--format", "json")
    assert result.exit_code == 2 and "action" not in json.loads(result.stdout)
    monkeypatch.setattr(m, "_codex", lambda *args: "[]")
    result = invoke(root, "setup", "--format", "json")
    assert result.exit_code == 2 and "action" not in json.loads(result.stdout)
    assert not state["writes"]


def test_linked_workspace_and_runtime_are_rejected(tmp_path, monkeypatch):
    base = tmp_path / "base"
    linked = tmp_path / "linked"
    base.mkdir()
    linked.mkdir()
    (base / ".git").mkdir()
    (linked / ".git").write_text("gitdir: /missing/worktree")
    executable = linked / ".venv/bin/python"
    executable.parent.mkdir(parents=True)
    executable.symlink_to(sys.executable)
    monkeypatch.setattr(m.sys, "executable", str(executable))
    with pytest.raises(HostMcpRuntimeError):
        m._retained(base)
    monkeypatch.setattr(m.sys, "executable", "/usr/bin/python3")
    with pytest.raises(HostMcpRuntimeError):
        m._retained(linked)
    alias = tmp_path / "alias"
    alias.symlink_to(linked, target_is_directory=True)
    with pytest.raises(HostMcpRuntimeError):
        m._retained(alias)


@pytest.mark.skipif(shutil.which("codex") is None, reason="Codex CLI is optional")
def test_real_codex_registration_in_isolated_home(tmp_path, monkeypatch):
    root = tmp_path / "base"
    root.mkdir()
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    # This test runs in a development worktree; production checks are exercised separately above.
    monkeypatch.setattr(m, "_retained", lambda root: None)
    monkeypatch.setattr(m, "_sdk_available", lambda: True)
    initial = m.setup_registration(root)
    assert initial["action"] == "registered"
    settings = codex_home / "config.toml"
    saved = settings.read_bytes()
    assert m.setup_registration(root)["action"] == "unchanged"
    assert settings.read_bytes() == saved
    assert m.inspect_registration(root)[0]["state"] == "matching"
    # Register a foreign target, then exercise explicit replacement through the actual CLI.
    m._codex(root, "add", "devkit", "--env", "EXAMPLE=foreign", "--", "/foreign/python")
    assert m.inspect_registration(root)[0]["state"] == "different"
    assert m.setup_registration(root, replace=True)["action"] == "replaced"
    assert os.environ["CODEX_HOME"] == str(codex_home)
