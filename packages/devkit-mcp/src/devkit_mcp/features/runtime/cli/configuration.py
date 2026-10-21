"""MCP launch descriptor command."""

from __future__ import annotations

from dataclasses import asdict

import click
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    resolve_root,
    workspace_option,
)

from devkit_mcp.features.runtime.cli.output import report
from devkit_mcp.features.runtime.usecases.configuration import descriptor


@click.command()
@workspace_option()
@click.option("--executable", type=click.Path())
@FORMAT_OPTION
@boundary
def config(workspace_root: str | None, executable: str | None, output_format: str) -> None:
    """Print a verified retained launch descriptor without registering it."""
    launch = descriptor(resolve_root(workspace_root), executable=executable)
    report({"action": "config", "descriptor": asdict(launch) if launch else None}, output_format)
