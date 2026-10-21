"""Distribution bundles CLI adapters."""

from __future__ import annotations

from pathlib import Path

import click

from devkit_dist.features.distribution.models.settings import (
    AGENT_NAMES,
)
from devkit_dist.features.distribution.usecases.commands import (
    plan_source,
    validate_source,
)

from .output import SOURCE, _json_command


@click.group()
def bundle() -> None:
    """Validate, plan and package local bundle sources."""


@bundle.command()
@SOURCE
@_json_command
def validate(source: Path) -> object:
    """Validate bundle.toml and every declared source."""
    return validate_source(source)


@bundle.command(name="plan")
@SOURCE
@click.option("--preset", default=None, help="Preset to plan (default: the bundle's default preset, else all).")
@click.option("--agent", "agents", multiple=True, type=click.Choice(AGENT_NAMES), help="Agents to project for.")
@_json_command
def plan(source: Path, preset: str | None, agents: tuple[str, ...]) -> object:
    """Preview every destination a bundle deploys, without a consumer project."""
    return plan_source(source, preset, agents)
