"""Distribution context CLI adapters."""

from __future__ import annotations

import click

from devkit_dist.adapters.cli import (
    resolve_root,
)
from devkit_dist.features.distribution.usecases.context import GetContext

from .output import WORKSPACE, _json_command


@click.command(name="get-context")
@click.argument("bundle_name")
@WORKSPACE
@_json_command
def context(bundle_name: str, workspace_root: str | None) -> object:
    """Return the full constitution and instruction headers for a synced bundle."""
    return GetContext().execute(resolve_root(workspace_root), bundle_name)
