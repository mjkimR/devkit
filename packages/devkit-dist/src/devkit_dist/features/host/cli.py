"""Host commands; the hook subcommand's stdout follows the native protocol."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from devkit.advisory import AdvisoryError, Level

from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    is_json,
    report_exit_code,
    resolve_root,
    workspace_option,
)
from devkit_dist.features.host.models.errors import HookDispatchError
from devkit_dist.features.host.usecases.runner import DispatchHostHook
from devkit_dist.features.host.usecases.status import InspectHost
from devkit_dist.features.project.usecases.workspace import find_project_root

MAX_EVENT_BYTES = 1024 * 1024


@click.group()
def cli() -> None:
    """Host adapters: inspect lifecycle hooks and DispatchHostHook native events to services."""


@cli.command()
@click.option("--host", default="codex", help="Host adapter (currently codex)")
@workspace_option()
@FORMAT_OPTION
@boundary
def status(host: str, workspace_root: str | None, output_format: str) -> None:
    """Inspect installed hooks and metadata-only observations; trust and permissions remain host-owned."""
    report = InspectHost().execute(resolve_root(workspace_root), host)
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


@cli.command(hidden=True)
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
        response = DispatchHostHook().execute(root, host, asset, payload)
    except AdvisoryError as exc:
        echo_notices([exc.with_level(Level.WARNING)])
    except (ValueError, UnicodeError, OSError, RecursionError) as exc:
        echo_notices(
            [HookDispatchError(f"cannot process native hook event ({type(exc).__name__})").with_level(Level.WARNING)]
        )
    echo_json(response)
