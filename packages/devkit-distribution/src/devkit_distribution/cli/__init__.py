from __future__ import annotations

import json
from pathlib import Path

import click

from devkit_distribution.bundles import BundleError, build_bundle, load_bundle, plan_bundle


@click.group()
@click.version_option(package_name="devkit-distribution")
def cli() -> None:
    """Devkit agent asset distribution tools."""


@cli.group()
def bundle() -> None:
    """Validate and package local bundles."""


def _run(action: str, source: Path, output: Path | None = None, preset: str | None = None) -> None:
    try:
        loaded = load_bundle(source)
        if action == "build" and output is not None:
            result = build_bundle(loaded, output)
        elif action == "plan":
            result = plan_bundle(loaded, preset)
        else:
            result = {"name": loaded.name, "version": loaded.version, "assets": len(loaded.assets)}
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))


@bundle.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))
def validate(source: Path) -> None:
    """Validate bundle.toml and every declared source."""
    _run("validate", source)


@bundle.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", required=True, type=click.Path(dir_okay=False, path_type=Path))
def build(source: Path, output: Path) -> None:
    """Build a deterministic ZIP archive with a hashed inventory."""
    _run("build", source, output)


@cli.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--preset", default=None)
def plan(source: Path, preset: str | None) -> None:
    """Preview managed inventory without writing a consumer project."""
    _run("plan", source, preset=preset)
