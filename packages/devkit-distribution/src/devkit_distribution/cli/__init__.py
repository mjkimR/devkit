from __future__ import annotations

import json
from pathlib import Path

import click

from devkit_distribution.bundles import BundleError, build_bundle, load_bundle, plan_bundle
from devkit_distribution.installation.context import get_context
from devkit_distribution.installation.discovery import discover_bundles
from devkit_distribution.installation.inventory import AGENTS
from devkit_distribution.installation.overrides import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from devkit_distribution.installation.playbook_search import search_playbooks
from devkit_distribution.installation.sync import read_receipt, recover_project, sync_project


@click.group()
@click.version_option(package_name="devkit-distribution")
def cli() -> None:
    """Devkit agent asset distribution tools."""


@cli.command(name="get-context")
@click.argument("bundle_name")
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def context(bundle_name: str, target: Path) -> None:
    """Return the full constitution and instruction headers for a synced bundle."""
    try:
        result = get_context(target, bundle_name)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


@cli.group()
def playbook() -> None:
    """Discover occasional procedures after explicit devkit-playbook invocation."""


@playbook.command(name="search")
@click.argument("query")
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--limit", default=5, show_default=True, type=click.IntRange(1, 20))
@click.option("--min-score", default=0.1, show_default=True, type=click.FloatRange(min=0))
@click.option("--max-bytes", default=8192, show_default=True, type=click.IntRange(1024, 65536))
def search(query: str, target: Path, limit: int, min_score: float, max_bytes: int) -> None:
    """Search synchronized playbook metadata with an English query; return headers only."""
    try:
        result = search_playbooks(target, query, limit=limit, min_score=min_score, max_bytes=max_bytes)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))


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


@cli.command()
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--agent", "agents", multiple=True, type=click.Choice(sorted(AGENTS)))
@click.option("--no-agents", is_flag=True, help="Clear recorded native agent selections.")
@click.option("--preset", "presets", multiple=True, help="Select bundle:preset; repeat for multiple bundles.")
@click.option("--all-assets", is_flag=True, help="Clear recorded preset restrictions.")
@click.option("--dry-run", is_flag=True)
@click.option("--check", is_flag=True, help="Read-only check; exit 1 when synchronization is needed.")
def sync(
    target: Path,
    agents: tuple[str, ...],
    no_agents: bool,
    presets: tuple[str, ...],
    all_assets: bool,
    dry_run: bool,
    check: bool,
) -> None:
    """Synchronize resources from installed content packages into a project."""
    if agents and no_agents:
        raise click.UsageError("--agent and --no-agents cannot be combined")
    selected = {}
    for value in presets:
        name, separator, preset = value.partition(":")
        if not separator or not name or not preset or name in selected:
            raise click.BadParameter("expected unique bundle:preset selections", param_hint="--preset")
        selected[name] = preset
    try:
        with discover_bundles() as installed:
            result = sync_project(
                target,
                installed,
                agents=[] if no_agents else (list(agents) if agents else None),
                presets=selected,
                all_assets=all_assets,
                dry_run=dry_run or check,
            )
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))
    drift = result.get("drift")
    if isinstance(drift, list):
        for item in drift:
            if isinstance(item, dict):
                bundle_name = item.get("bundle")
                asset_id = item.get("asset")
                click.echo(
                    f"WARNING: upstream drift detected for {bundle_name}:{asset_id}. "
                    f"Run 'devkit override diff {bundle_name}:{asset_id}' to review.",
                    err=True,
                )
    if check and result["actions"]:
        raise click.exceptions.Exit(1)


@cli.command(name="list")
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def list_resources(target: Path) -> None:
    """List installed bundle metadata and the project's synchronized asset paths."""
    try:
        with discover_bundles() as installed:
            receipt = read_receipt(target.resolve())
            result = {
                "installed": [
                    {
                        "package": item.package,
                        "version": item.package_version,
                        "bundle": item.bundle.name,
                        "presets": sorted(item.bundle.presets),
                        "assets": [{"id": asset.id, "kind": asset.kind} for asset in item.bundle.assets],
                    }
                    for item in installed
                ],
                "synchronized_assets": receipt.get("assets", []),
                "overrides": receipt.get("overrides", {}),
            }
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def recover(target: Path) -> None:
    """Roll back an interrupted synchronization without overwriting later edits."""
    try:
        count = recover_project(target)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps({"recovered_files": count}))


@cli.group()
def override() -> None:
    """Manage local project asset overrides and upstream drift review."""


@override.command(name="create")
@click.argument("selector")
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--force", is_flag=True, help="Overwrite existing override files.")
def override_create(selector: str, target: Path, force: bool) -> None:
    """Create a local override for an installed bundle asset (bundle:asset)."""
    try:
        with discover_bundles() as installed:
            result = create_override(target, installed, selector, force=force)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))


@override.command(name="diff")
@click.argument("selector")
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def override_diff(selector: str, target: Path) -> None:
    """Display 3-way or upstream diff for an overridden asset (bundle:asset)."""
    try:
        with discover_bundles() as installed:
            result = diff_override(target, installed, selector)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))


@override.command(name="accept")
@click.argument("selector")
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def override_accept(selector: str, target: Path) -> None:
    """Accept upstream updates and advance the baseline digest (bundle:asset)."""
    try:
        with discover_bundles() as installed:
            result = accept_override(target, installed, selector)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))


@override.command(name="remove")
@click.argument("selector")
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def override_remove(selector: str, target: Path) -> None:
    """Remove a local override and restore pristine upstream asset (bundle:asset)."""
    try:
        with discover_bundles() as installed:
            result = remove_override(target, installed, selector)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))


@override.command(name="list")
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def override_list_cmd(target: Path) -> None:
    """List active overrides and their drift status."""
    try:
        with discover_bundles() as installed:
            result = list_overrides(target, installed)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2))
