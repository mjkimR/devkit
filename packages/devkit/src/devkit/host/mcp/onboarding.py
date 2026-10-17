"""Explicit Codex user registration; never invoked by asset synchronization."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit.host.errors import (
    HostMcpDependencyError,
    HostMcpRegistrationConflict,
    HostMcpRegistrationError,
    HostMcpRegistrationMissing,
    HostMcpRegistrationShadowed,
    HostMcpRuntimeError,
)
from devkit.host.mcp.configuration import configuration

HOST_TIMEOUT = 15


def _codex(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["codex", "mcp", *args],
            cwd=root,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=HOST_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        raise HostMcpRegistrationError(f"Codex MCP {args[0]} could not run ({type(exc).__name__})") from exc
    if result.returncode:
        # Host configuration errors can contain credentials; never echo captured output.
        raise HostMcpRegistrationError(f"Codex MCP {args[0]} exited with status {result.returncode}")
    return result.stdout


def _json(root: Path, *args: str) -> Any:
    try:
        return json.loads(_codex(root, *args))
    except (ValueError, RecursionError) as exc:
        raise HostMcpRegistrationError("Codex returned invalid MCP registration JSON") from exc


def _registration(root: Path) -> dict | None:
    entries = _json(root, "list", "--json")
    if not isinstance(entries, list) or any(
        not isinstance(e, dict) or not isinstance(e.get("name"), str) for e in entries
    ):
        raise HostMcpRegistrationError("Codex returned an invalid MCP server list")
    selected = [entry for entry in entries if entry["name"] == "devkit"]
    if not selected:
        return None
    if len(selected) != 1:
        raise HostMcpRegistrationError("Codex returned duplicate devkit registrations")
    entry = _json(root, "get", "devkit", "--json")
    if not isinstance(entry, dict) or entry.get("name") != "devkit" or not isinstance(entry.get("transport"), dict):
        raise HostMcpRegistrationError("Codex returned an invalid devkit registration")
    return entry


def _config_entry(path: Path) -> dict | None:
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError, UnicodeError) as exc:
        raise HostMcpRegistrationError(
            "cannot inspect Codex configuration; correct configuration access and syntax"
        ) from exc
    servers = config.get("mcp_servers", {})
    if not isinstance(servers, dict):
        raise HostMcpRegistrationError("Codex mcp_servers must be a table")
    entry = servers.get("devkit")
    if entry is not None and not isinstance(entry, dict):
        raise HostMcpRegistrationError("Codex devkit registration must be a table")
    return entry


def _user_config() -> Path:
    home = os.environ.get("CODEX_HOME")
    return (Path(home).expanduser() if home else Path.home() / ".codex") / "config.toml"


def _user_registration() -> dict | None:
    entry = _config_entry(_user_config())
    if entry is None:
        return None
    return {
        "name": "devkit",
        "enabled": entry.get("enabled", True),
        "transport": {
            "type": "stdio" if "command" in entry else "streamable_http",
            "command": entry.get("command"),
            "args": entry.get("args", []),
            "env": entry.get("env"),
            "env_vars": entry.get("env_vars"),
            "cwd": entry.get("cwd"),
        },
        "enabled_tools": entry.get("enabled_tools"),
        "disabled_tools": entry.get("disabled_tools"),
    }


def _project_registration(root: Path) -> bool:
    user_path = _user_config().resolve()
    # Ancestor project layers can shadow the named user server. Never replace a hidden user entry.
    return any(
        path.resolve() != user_path and _config_entry(path) is not None
        for parent in (root.resolve(), *root.resolve().parents)
        for path in [parent / ".codex" / "config.toml"]
    )


def _matches(entry: dict, desired: dict) -> bool:
    transport = entry["transport"]
    return (
        entry.get("enabled") is True
        and transport.get("type") == "stdio"
        and transport.get("command") == desired["command"]
        and transport.get("args") == desired["args"]
        and not transport.get("env")
        and not transport.get("env_vars")
        and not transport.get("cwd")
        and entry.get("enabled_tools") is None
        and entry.get("disabled_tools") in (None, [])
    )


def _sdk_available() -> bool:
    return importlib.util.find_spec("mcp") is not None


def _report(root: Path) -> tuple[dict, list[AdvisoryError]]:
    desired = configuration(root)
    entry = _user_registration()
    effective = _registration(root)
    project_override = _project_registration(root)
    effective_state = "missing" if effective is None else "matching" if _matches(effective, desired) else "different"
    state = "missing" if entry is None else "matching" if _matches(entry, desired) else "different"
    errors: list[AdvisoryError] = []
    if state == "missing":
        errors.append(HostMcpRegistrationMissing("Codex has no devkit MCP registration"))
    elif state == "different":
        errors.append(HostMcpRegistrationConflict("Codex devkit registration differs from this workspace/runtime"))
    if project_override:
        errors.append(
            HostMcpRegistrationShadowed(
                "a project Codex configuration declares devkit; user setup cannot manage that entry"
            )
        )
    elif effective_state != state:
        errors.append(HostMcpRegistrationShadowed("effective Codex registration differs from the user configuration"))
    available = _sdk_available()
    if not available:
        errors.append(HostMcpDependencyError("the running Python has no MCP SDK"))
    return {
        "host": "codex",
        "server": "devkit",
        "scope": "user",
        "state": state,
        "effective_state": effective_state,
        "project_override": project_override,
        "workspace_root": str(root.resolve()),
        "command": desired["command"],
        "args": desired["args"],
        "sdk_available": available,
        "connection": "unknown",
        "approval_ui": "unknown",
        "trust": "unknown",
        "execution_permissions": "unknown",
        "errors": [error.to_dict() for error in errors],
        "notices": [],
    }, errors


def inspect_registration(root: Path) -> tuple[dict, list[AdvisoryError]]:
    """Read effective registration only; do not connect or start a server."""
    return _report(root)


def _retained(root: Path) -> None:
    # Keep the venv executable's lexical path: resolving its symlink loses the venv location.
    executable = Path(sys.executable).absolute()
    for path in {root.absolute(), root.resolve(), executable, executable.parent.resolve()}:
        for ancestor in (path, *path.parents):
            if (ancestor / ".git").is_file():
                raise HostMcpRuntimeError(
                    "workspace and Python must be outside linked worktrees and submodule checkouts"
                )
    if not executable.is_file():
        raise HostMcpRuntimeError("the running Python executable is not retained on disk")


def setup_registration(root: Path, *, replace: bool = False) -> dict:
    """Register once through Codex's writer and verify, preserving matching settings."""
    _retained(root)
    if not _sdk_available():
        raise HostMcpDependencyError("the running Python has no MCP SDK")
    try:
        importlib.import_module("devkit.host.mcp.server")
    except ImportError as exc:
        raise HostMcpDependencyError("the running Python cannot import the MCP server and SDK") from exc
    before, errors = _report(root)
    shadowed = next((error for error in errors if isinstance(error, HostMcpRegistrationShadowed)), None)
    if shadowed is not None:
        raise shadowed
    if before["state"] == "matching":
        return before | {"action": "unchanged"}
    if before["state"] == "different" and not replace:
        raise HostMcpRegistrationConflict("Codex already has a different devkit registration; no settings changed")
    if not before["sdk_available"]:
        raise errors[-1]
    desired = configuration(root)
    _codex(root, "add", "devkit", "--", desired["command"], *desired["args"])
    after, _ = _report(root)
    if after["state"] != "matching" or after["errors"]:
        raise HostMcpRegistrationError(
            "Codex add completed but the effective devkit registration does not match; inspect before retrying"
        )
    return after | {"action": "registered" if before["state"] == "missing" else "replaced"}
