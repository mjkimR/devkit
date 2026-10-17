"""Host commands; the hook subcommand's stdout follows the native protocol."""

from __future__ import annotations

import json
import sys
from contextlib import chdir
from pathlib import Path

import click

from devkit.advisory import AdvisoryError, Level
from devkit.core.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    is_json,
    report_exit_code,
    resolve_root,
    workspace_option,
)
from devkit.core.project import find_project_root
from devkit.host import HookDispatchError, dispatch, inspect_host
from devkit.host.errors import HostMcpDependencyError

MAX_EVENT_BYTES = 1024 * 1024


@click.group()
def cli() -> None:
    """Host adapters: inspect lifecycle hooks and dispatch native events to services."""


@cli.command()
@click.option("--host", default="codex", help="Host adapter (currently codex)")
@workspace_option()
@FORMAT_OPTION
@boundary
def status(host: str, workspace_root: str | None, output_format: str) -> None:
    """Inspect installed hooks and metadata-only observations; trust and permissions remain host-owned."""
    report = inspect_host(resolve_root(workspace_root), host)
    if is_json(output_format):
        echo_json(report.to_dict())
    else:
        click.echo(
            f"[HOST_STATUS: {report.host} hooks={len(report.hooks)} ok={'yes' if not report.errors else 'no'} trust=unknown]"
        )
        for item in report.hooks:
            received = item["last_received"]
            click.echo(
                f"[HOST_HOOK: {item['asset']} event={item['event']} state={item['state']} observed={'yes' if received else 'no'}]"
            )
        echo_notices(report.errors)
    sys.exit(report_exit_code(report.errors))


@cli.command()
@click.option("--host", required=True)
@click.option("--asset", required=True, help="Receipt-selected bundle:hook asset")
@workspace_option()
def hook(host: str, asset: str, workspace_root: str | None) -> None:
    """Read one native event from stdin; emit native JSON only. Advisory failures leave the host operation running."""
    response: dict = {}
    try:
        raw = sys.stdin.buffer.read(MAX_EVENT_BYTES + 1)
        if len(raw) > MAX_EVENT_BYTES:
            raise HookDispatchError("hook event exceeds the 1 MiB input limit")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise HookDispatchError("hook event must be a JSON object")
        cwd = payload.get("cwd")
        if workspace_root is not None:
            root = resolve_root(workspace_root)
        elif isinstance(cwd, str) and Path(cwd).is_absolute():
            root = find_project_root(Path(cwd))
        else:
            raise HookDispatchError("hook event must include an absolute cwd")
        response = dispatch(root, host, asset, payload)
    except AdvisoryError as exc:
        echo_notices([exc.with_level(Level.WARNING)])
    except (ValueError, UnicodeError, OSError, RecursionError) as exc:
        echo_notices(
            [HookDispatchError(f"cannot process native hook event ({type(exc).__name__})").with_level(Level.WARNING)]
        )
    echo_json(response)


@cli.group()
def mcp() -> None:
    """MCP service transport, explicit registration and registration diagnostics."""


@mcp.command(name="config")
@workspace_option()
@FORMAT_OPTION
@boundary
def mcp_config(workspace_root: str | None, output_format: str) -> None:
    """Print Codex registration, inspection and removal commands; changes no host settings."""
    from devkit.host.mcp.configuration import configuration

    result = configuration(resolve_root(workspace_root))
    if is_json(output_format):
        echo_json(result)
    else:
        click.echo("[HOST_MCP_CONFIG: codex server=devkit transport=stdio]")
        click.echo(result["toml"], nl=False)


@mcp.command(name="setup")
@click.option("--host", type=click.Choice(["codex"]), default="codex", show_default=True)
@click.option("--replace", is_flag=True, help="Replace a different user-scoped devkit registration")
@workspace_option()
@FORMAT_OPTION
@boundary
def mcp_setup(host: str, replace: bool, workspace_root: str | None, output_format: str) -> None:
    """Register this retained runtime/base with Codex; matching registrations are unchanged."""
    from devkit.host.mcp.onboarding import setup_registration

    result = setup_registration(resolve_root(workspace_root), replace=replace)
    if is_json(output_format):
        echo_json(result)
    else:
        click.echo(f"[HOST_MCP_SETUP: {host} server=devkit scope=user action={result['action']} connection=unknown]")


@mcp.command(name="status")
@click.option("--host", type=click.Choice(["codex"]), default="codex", show_default=True)
@workspace_option()
@FORMAT_OPTION
@boundary
def mcp_status(host: str, workspace_root: str | None, output_format: str) -> None:
    """Read registration and SDK status; connection and approval UI remain unknown."""
    from devkit.host.mcp.onboarding import inspect_registration

    result, errors = inspect_registration(resolve_root(workspace_root))
    if is_json(output_format):
        echo_json(result)
    else:
        click.echo(
            f"[HOST_MCP_STATUS: {host} server=devkit scope=user state={result['state']} effective={result['effective_state']} sdk={'yes' if result['sdk_available'] else 'no'} connection=unknown]"
        )
        echo_notices(errors)
    sys.exit(report_exit_code(errors))


@mcp.command(name="serve")
@workspace_option()
def mcp_serve(workspace_root: str | None) -> None:
    """Serve installed tools over native MCP stdio. Requires the devkit-agt[mcp] extra."""
    try:
        try:
            from devkit.host.mcp.server import serve
        except ImportError as exc:
            raise HostMcpDependencyError("the MCP SDK transport is not installed in this runtime") from exc
        root = resolve_root(workspace_root)
        with chdir(root):
            serve(root)
    except AdvisoryError as exc:
        echo_notices([exc])
        sys.exit(int(exc.exit_code))
