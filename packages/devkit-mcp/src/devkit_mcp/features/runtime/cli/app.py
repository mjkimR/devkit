"""Optional MCP command group assembly."""

import click

from devkit_mcp.features.runtime.cli.registration import remove, setup, status
from devkit_mcp.features.runtime.cli.serve import serve


@click.group()
def cli() -> None:
    """Configure and serve optional MCP services with Host-owned native approval."""


for command in (setup, remove, status, serve):
    cli.add_command(command)
