"""Explicit Codex user registration; never invoked by asset synchronization."""

from __future__ import annotations

import importlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError
from devkit.host.errors import (
    HostMcpDependencyError,
    HostMcpRegistrationConflict,
    HostMcpRegistrationError,
    HostMcpRegistrationMissing,
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
    entry = _registration(root)
    state = "missing" if entry is None else "matching" if _matches(entry, desired) else "different"
    errors: list[AdvisoryError] = []
    if state == "missing":
        errors.append(HostMcpRegistrationMissing("Codex has no devkit MCP registration"))
    elif state == "different":
        errors.append(HostMcpRegistrationConflict("Codex devkit registration differs from this workspace/runtime"))
    available = _sdk_available()
    if not available:
        errors.append(HostMcpDependencyError("the running Python has no MCP SDK"))
    return {
        "host": "codex",
        "server": "devkit",
        "scope": "user",
        "state": state,
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
    if before["state"] == "matching":
        return before | {"action": "unchanged"}
    if before["state"] == "different" and not replace:
        raise HostMcpRegistrationConflict("Codex already has a different devkit registration; no settings changed")
    if not before["sdk_available"]:
        raise errors[-1]
    desired = configuration(root)
    _codex(root, "add", "devkit", "--", desired["command"], *desired["args"])
    after, _ = _report(root)
    if after["state"] != "matching":
        raise HostMcpRegistrationError(
            "Codex add completed but the effective devkit registration does not match; inspect before retrying"
        )
    return after | {"action": "registered" if before["state"] == "missing" else "replaced"}
