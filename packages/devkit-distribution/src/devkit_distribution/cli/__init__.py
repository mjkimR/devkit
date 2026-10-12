from __future__ import annotations

import json
from pathlib import Path

import click

from devkit_distribution.bundles import BundleError, build_bundle, load_bundle, plan_bundle
from devkit_distribution.bundles.manifest import SLUG
from devkit_distribution.installation.config import read_config, resolve_selection, update_config
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
@click.option(
    "--limit", default=None, type=click.IntRange(1, 20), help="Maximum candidates to return (default: 5 or config)."
)
@click.option(
    "--min-score", default=None, type=click.FloatRange(min=0), help="Minimum score threshold (default: 0.1 or config)."
)
@click.option(
    "--max-bytes",
    default=None,
    type=click.IntRange(1024, 65536),
    help="Maximum JSON response byte budget (default: 8192 or config).",
)
def search(query: str, target: Path, limit: int | None, min_score: float | None, max_bytes: int | None) -> None:
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


def _parse_selections(values: tuple[str, ...], param_hint: str) -> dict[str, list[str]]:
    """Parse ``bundle[:preset]`` values; repeating a bundle selects a union, a bare bundle its default preset."""
    selected: dict[str, list[str]] = {}
    for value in values:
        name, separator, preset = value.partition(":")
        if not SLUG.fullmatch(name) or (separator and not SLUG.fullmatch(preset)):
            raise click.BadParameter(f"expected bundle[:preset] slugs: {value}", param_hint=param_hint)
        presets = selected.setdefault(name, [])
        if preset and preset not in presets:
            presets.append(preset)
    return selected


def _report(result: dict[str, object]) -> None:
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
    stray = result.get("stray")
    if isinstance(stray, list) and stray:
        listed = ", ".join(str(item) for item in stray)
        click.echo(
            f"WARNING: unmanaged files under .devkit/managed/: {listed}. "
            "devkit does not deploy or remove them; move project-owned files out of the managed root.",
            err=True,
        )
    unprojected = result.get("unprojected")
    if isinstance(unprojected, list) and unprojected:
        items = ", ".join(
            f"{item['bundle']}:{item['asset']} ({item['agent']})" for item in unprojected if isinstance(item, dict)
        )
        click.echo(
            f"NOTICE: subagents without a native variant for a selected agent were not projected: {items}. "
            "Add the variant, ship a role contract, or narrow 'agents' in .devkit/config.toml.",
            err=True,
        )
    unselected = result.get("unselected")
    if isinstance(unselected, list) and unselected:
        names = ", ".join(str(item["bundle"]) for item in unselected if isinstance(item, dict))
        click.echo(
            f"NOTICE: installed bundles not selected: {names}. Select with 'devkit add <bundle>[:<preset>]'.",
            err=True,
        )


@cli.command()
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--agent", "agents", multiple=True, type=click.Choice(sorted(AGENTS)), help="Set agent targets.")
@click.option("--no-agents", is_flag=True, help="Clear agent targets.")
@click.option(
    "--preset",
    "presets",
    multiple=True,
    help="Select bundle[:preset]; a bare bundle uses its default preset; repeat a bundle for a union.",
)
@click.option("--no-save", is_flag=True, help="Apply selection flags to this run without editing .devkit/config.toml.")
@click.option("--dry-run", is_flag=True)
@click.option("--check", is_flag=True, help="Read-only check; exit 1 when synchronization is needed.")
def sync(
    target: Path,
    agents: tuple[str, ...],
    no_agents: bool,
    presets: tuple[str, ...],
    no_save: bool,
    dry_run: bool,
    check: bool,
) -> None:
    """Synchronize the bundles selected in .devkit/config.toml into a project."""
    if agents and no_agents:
        raise click.UsageError("--agent and --no-agents cannot be combined")
    requested = _parse_selections(presets, "--preset")
    active_agents = [] if no_agents else (list(agents) if agents else None)
    dry_run = dry_run or check
    try:
        with discover_bundles() as installed:
            selected = resolve_selection(installed, requested)
            result = sync_project(target, installed, agents=active_agents, presets=selected, dry_run=dry_run)
            if not (no_save or dry_run) and (selected or active_agents is not None):
                update_config(target.resolve(), agents=active_agents, presets=selected)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    _report(result)
    if check and result["actions"]:
        raise click.exceptions.Exit(1)


@cli.command()
@click.argument("selections", nargs=-1, required=True)
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Preview without editing configuration or files.")
def add(selections: tuple[str, ...], target: Path, dry_run: bool) -> None:
    """Select bundle[:preset] in .devkit/config.toml and synchronize.

    Without a preset, the bundle's default preset is recorded by name.
    """
    requested = _parse_selections(selections, "SELECTIONS")
    try:
        with discover_bundles() as installed:
            selected = resolve_selection(installed, requested)
            result = sync_project(target, installed, presets=selected, dry_run=dry_run)
            if not dry_run:
                update_config(target.resolve(), presets=selected)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    _report(result)


@cli.command()
@click.argument("bundles", nargs=-1, required=True)
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Preview without editing configuration or files.")
def remove(bundles: tuple[str, ...], target: Path, dry_run: bool) -> None:
    """Deselect bundles in .devkit/config.toml and synchronize."""
    try:
        configured = read_config(target.resolve()).presets
        missing = sorted(set(bundles) - set(configured))
        if missing:
            raise BundleError(f"bundle is not selected in .devkit/config.toml: {missing}")
        with discover_bundles() as installed:
            result = sync_project(target, installed, deselect=bundles, dry_run=dry_run)
            if not dry_run:
                update_config(target.resolve(), deselect=bundles)
    except (BundleError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    _report(result)


@cli.command(name="list")
@click.option("--target", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
def list_resources(target: Path) -> None:
    """List installed bundles, their selection state, and the project's synchronized asset paths."""
    root = target.resolve()
    try:
        with discover_bundles() as installed:
            receipt = read_receipt(root)
            configured = read_config(root).presets
            result = {
                "installed": [
                    {
                        "package": item.package,
                        "version": item.package_version,
                        "bundle": item.bundle.name,
                        "presets": item.bundle.preset_names,
                        "default_preset": item.bundle.default_preset,
                        "selected": configured.get(item.bundle.name),
                        "assets": [{"id": asset.id, "kind": asset.kind} for asset in item.bundle.assets],
                    }
                    for item in installed
                ],
                "synchronized_assets": receipt.get("assets", []),
                "seeded": receipt.get("seeded", []),
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
