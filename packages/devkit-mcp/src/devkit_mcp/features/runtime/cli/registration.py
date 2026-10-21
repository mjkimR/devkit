"""MCP registration commands."""

from __future__ import annotations

import click
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    resolve_root,
    workspace_option,
)

from devkit_mcp.features.runtime.cli.output import report
from devkit_mcp.features.runtime.usecases import registration


@click.command()
@workspace_option()
@click.option("--executable", type=click.Path())
@click.option("--host", multiple=True, type=click.Choice(["codex", "claude", "antigravity"]))
@FORMAT_OPTION
@boundary
def setup(workspace_root: str | None, executable: str | None, host: tuple[str, ...], output_format: str) -> None:
    """Reconcile exact owned project entries; never mutate user settings or adopt foreign entries."""
    planned = registration.setup(resolve_root(workspace_root), host, executable=executable)
    report({"action": "setup", "registrations": planned.states}, output_format, planned.notices)


@click.command()
@workspace_option()
@FORMAT_OPTION
@boundary
def remove(workspace_root: str | None, output_format: str) -> None:
    """Remove only exact owned project entries; retain clone-local exclusions."""
    planned = registration.remove(resolve_root(workspace_root))
    report({"action": "remove", "registrations": planned.states}, output_format, planned.notices)


@click.command()
@workspace_option()
@FORMAT_OPTION
@boundary
def status(workspace_root: str | None, output_format: str) -> None:
    """Inspect local registration facts; connection, effective enablement, forms and trust remain unknown."""
    data = registration.status(resolve_root(workspace_root))
    notices = data.pop("notices")
    report({"action": "status", **data}, output_format, notices)
