"""Distribution overrides CLI adapters."""

from __future__ import annotations

import click

from devkit_dist.adapters.cli import (
    resolve_root,
)
from devkit_dist.features.distribution.usecases import commands as operations
from devkit_dist.features.distribution.usecases.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)

from .output import WORKSPACE, _json_command, _report_change


@click.group()
def override() -> None:
    """Manage local project asset overrides and upstream drift review."""


@override.command(name="create")
@click.argument("selector")
@WORKSPACE
@click.option("--force", is_flag=True, help="Overwrite existing override files.")
@_json_command
def override_create(selector: str, workspace_root: str | None, force: bool) -> None:
    """Copy an installed asset (bundle:asset) into .devkit/overrides/ and synchronize."""
    with operations.discover_bundles() as installed:
        change = create_override(resolve_root(workspace_root), installed, selector, force=force)
    _report_change(change)


@override.command(name="diff")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_diff(selector: str, workspace_root: str | None) -> object:
    """Per file: upstream vs override, and recorded baseline vs current upstream (bundle:asset)."""
    with operations.discover_bundles() as installed:
        return diff_override(resolve_root(workspace_root), installed, selector)


@override.command(name="accept")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_accept(selector: str, workspace_root: str | None) -> object:
    """Record the current upstream as the override's baseline (bundle:asset)."""
    with operations.discover_bundles() as installed:
        return accept_override(resolve_root(workspace_root), installed, selector)


@override.command(name="remove")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_remove(selector: str, workspace_root: str | None) -> None:
    """Remove a local override and synchronize the pristine upstream asset (bundle:asset)."""
    with operations.discover_bundles() as installed:
        change = remove_override(resolve_root(workspace_root), installed, selector)
    _report_change(change)


@override.command(name="list")
@WORKSPACE
@_json_command
def override_list(workspace_root: str | None) -> object:
    """List tracked overrides and their drift status."""
    with operations.discover_bundles() as installed:
        return {"overrides": [item.to_dict() for item in list_overrides(resolve_root(workspace_root), installed)]}
