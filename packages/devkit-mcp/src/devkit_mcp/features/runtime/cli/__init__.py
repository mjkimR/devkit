"""Optional MCP command plugin. Runtime configuration is explicit, never inferred from client roots."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import click
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    is_json,
    resolve_root,
    workspace_option,
)

from devkit_mcp.features.runtime.usecases import registration
from devkit_mcp.features.runtime.usecases.configuration import descriptor


@click.group()
def cli() -> None:
    """Configure and serve optional MCP services with Host-owned native approval."""


def _report(data: dict, output_format: str, notices=()) -> None:
    if is_json(output_format):
        echo_json({**data, "notices": [item.to_dict() for item in notices]})
    else:
        click.echo(f"[MCP: action={data['action']} connection=unknown form=unknown trust=unknown permissions=unknown]")
        echo_notices(notices)


@cli.command()
@workspace_option()
@click.option("--executable", type=click.Path())
@FORMAT_OPTION
@boundary
def config(workspace_root: str | None, executable: str | None, output_format: str) -> None:
    """Print a verified retained launch descriptor without registering it."""
    launch = descriptor(resolve_root(workspace_root), executable=executable)
    _report({"action": "config", "descriptor": asdict(launch) if launch else None}, output_format)


@cli.command()
@workspace_option()
@click.option("--executable", type=click.Path())
@click.option("--host", multiple=True, type=click.Choice(["codex", "claude", "antigravity"]))
@FORMAT_OPTION
@boundary
def setup(workspace_root: str | None, executable: str | None, host: tuple[str, ...], output_format: str) -> None:
    """Reconcile exact owned project entries; never mutate user settings or adopt foreign entries."""
    planned = registration.setup(resolve_root(workspace_root), host, executable=executable)
    _report({"action": "setup", "registrations": planned.states}, output_format, planned.notices)


@cli.command()
@workspace_option()
@FORMAT_OPTION
@boundary
def remove(workspace_root: str | None, output_format: str) -> None:
    """Remove only exact owned project entries; retain clone-local exclusions."""
    planned = registration.remove(resolve_root(workspace_root))
    _report({"action": "remove", "registrations": planned.states}, output_format, planned.notices)


@cli.command()
@workspace_option()
@FORMAT_OPTION
@boundary
def status(workspace_root: str | None, output_format: str) -> None:
    """Inspect local registration facts; connection, effective enablement, forms and trust remain unknown."""
    report = registration.status(resolve_root(workspace_root))
    notices = report.pop("notices")
    _report({"action": "status", **report}, output_format, notices)


@cli.command()
@click.option("--workspace-root", required=True, type=click.Path(path_type=Path, exists=True, file_okay=False))
@click.option("--configuration-workspace", required=True, type=click.Path(path_type=Path, exists=True, file_okay=False))
@click.option("--profile", type=click.Choice(["local", "read-only"]), default="local")
@boundary
def serve(workspace_root: Path, configuration_workspace: Path, profile: str) -> None:
    """Serve native MCP stdio; stdout belongs exclusively to the protocol."""
    from devkit_mcp.features.runtime.mcp.server import serve as run

    run(workspace_root, configuration_workspace, profile=profile)
