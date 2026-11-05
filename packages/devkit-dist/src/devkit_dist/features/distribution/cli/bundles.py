"""Distribution bundles CLI adapters."""

from __future__ import annotations

from pathlib import Path

import click

from devkit_dist.adapters.cli import resolve_root
from devkit_dist.features.distribution.models.settings import (
    AGENT_NAMES,
)
from devkit_dist.features.distribution.usecases.commands import (
    PlanSource,
    ValidateSource,
)
from devkit_dist.features.distribution.usecases.snapshots import CreateBundleSnapshot, RefreshBundleSnapshot

from .output import SOURCE, WORKSPACE, _json_command


@click.group()
def bundle() -> None:
    """Validate, plan and package local bundle sources."""


@bundle.command()
@SOURCE
@_json_command
def validate(source: Path) -> object:
    """Validate bundle.toml and every declared source."""
    return ValidateSource().execute(source)


@bundle.command(name="plan")
@SOURCE
@click.option("--preset", default=None, help="Preset to plan (default: the bundle's default preset, else all).")
@click.option("--agent", "agents", multiple=True, type=click.Choice(AGENT_NAMES), help="Agents to project for.")
@_json_command
def plan(source: Path, preset: str | None, agents: tuple[str, ...]) -> object:
    """Preview every destination a bundle deploys, without a consumer project."""
    return PlanSource().execute(source, preset, agents)


@bundle.command(name="snapshot")
@SOURCE
@click.option(
    "--to",
    "destination",
    required=True,
    type=click.Path(path_type=Path),
    help="New local package directory relative to the consumer root.",
)
@click.option("--package", "package_name", required=True, help="Distinct local wrapper distribution name.")
@WORKSPACE
@_json_command
def snapshot(source: Path, destination: Path, package_name: str, workspace_root: str | None) -> object:
    """Copy every bundle of a supported local content checkout into a repository package."""
    return CreateBundleSnapshot().execute(resolve_root(workspace_root), source, destination, package_name)


@bundle.command(name="refresh")
@click.argument("destination", type=click.Path(path_type=Path))
@click.option("--source", required=True, type=click.Path(path_type=Path), help="Accessible source content checkout.")
@click.option("--check", is_flag=True, help="Preview differences and digests without writing.")
@click.option("--expect", default=None, help="Current digest returned by preview; required for apply.")
@click.option("--candidate", default=None, help="Reviewed candidate digest returned by preview; required for apply.")
@WORKSPACE
@_json_command
def refresh(
    destination: Path, source: Path, check: bool, expect: str | None, candidate: str | None, workspace_root: str | None
) -> object:
    """Preview or explicitly adopt source changes without overwriting local edits."""
    return RefreshBundleSnapshot().execute(
        resolve_root(workspace_root), destination, source, check=check, expect=expect, candidate=candidate
    )
