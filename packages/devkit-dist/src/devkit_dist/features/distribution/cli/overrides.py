"""Distribution overrides CLI adapters."""

from __future__ import annotations

import click

from devkit_dist.adapters.cli import (
    resolve_root,
)
from devkit_dist.features.distribution.usecases.commands import (
    accept_project_override,
    create_project_override,
    diff_project_override,
    list_project_overrides,
    remove_project_override,
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
    change = create_project_override(resolve_root(workspace_root), selector, force=force)
    _report_change(change)


@override.command(name="diff")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_diff(selector: str, workspace_root: str | None) -> object:
    """Per file: upstream vs override, and recorded baseline vs current upstream (bundle:asset)."""
    return diff_project_override(resolve_root(workspace_root), selector)


@override.command(name="accept")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_accept(selector: str, workspace_root: str | None) -> object:
    """Record the current upstream as the override's baseline (bundle:asset)."""
    return accept_project_override(resolve_root(workspace_root), selector)


@override.command(name="remove")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_remove(selector: str, workspace_root: str | None) -> None:
    """Remove a local override and synchronize the pristine upstream asset (bundle:asset)."""
    change = remove_project_override(resolve_root(workspace_root), selector)
    _report_change(change)


@override.command(name="list")
@WORKSPACE
@_json_command
def override_list(workspace_root: str | None) -> object:
    """List tracked overrides and their drift status."""
    return {"overrides": [item.to_dict() for item in list_project_overrides(resolve_root(workspace_root))]}
