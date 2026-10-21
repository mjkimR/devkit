"""MCP stdio serving command."""

from __future__ import annotations

from pathlib import Path

import click
from devkit_dist.adapters.cli import boundary


@click.command()
@click.option("--workspace-root", required=True, type=click.Path(path_type=Path, exists=True, file_okay=False))
@click.option("--configuration-workspace", required=True, type=click.Path(path_type=Path, exists=True, file_okay=False))
@click.option("--profile", type=click.Choice(["local", "read-only"]), default="local")
@boundary
def serve(workspace_root: Path, configuration_workspace: Path, profile: str) -> None:
    """Serve native MCP stdio; stdout belongs exclusively to the protocol."""
    from devkit_mcp.features.runtime.mcp.server import serve as run

    run(workspace_root, configuration_workspace, profile=profile)
