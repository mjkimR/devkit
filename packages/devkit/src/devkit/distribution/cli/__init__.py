"""The distribution commands of ``devkit`` (``sync``, ``add``, ``remove``, ``list``, ``status``, ...).

Every command prints JSON on stdout. Exit codes: ``0`` success; ``1`` only
from ``devkit sync --check`` when a synchronization is needed; ``2`` for any
error (invalid input, a conflict, an unreadable receipt or configuration).
"""

from __future__ import annotations

import functools
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import click

from devkit.core.errors import DevkitCoreError
from devkit.core.project import find_project_root

from ..bundles import BundleError, build_bundle, load_bundle
from ..bundles.common import AGENT_NAMES, SLUG
from ..installation.config import effective_selection, prepare_config_update, read_config, resolve_selection
from ..installation.context import get_context
from ..installation.discovery import InstalledBundle, discover_bundles
from ..installation.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from ..installation.plan import plan_bundle
from ..installation.playbook_search import search_playbooks
from ..installation.results import SyncResult
from ..installation.status import project_listing, project_status
from ..installation.sync import recover_project, sync_project


class DistributionError(click.ClickException):
    """Any failed distribution command; exit code 2 keeps 1 free for ``sync --check``."""

    exit_code = 2


def _json_command(fn: Callable[..., Any]) -> Callable[..., None]:
    """Run ``fn``, print its result as JSON, and report devkit errors as exit code 2."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            result = fn(*args, **kwargs)
        except (BundleError, DevkitCoreError, OSError) as exc:
            raise DistributionError(str(exc)) from exc
        if result is not None:
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))

    return wrapper


def _workspace(value: str | None) -> Path:
    return Path(value).resolve() if value is not None else find_project_root(Path.cwd())


WORKSPACE = click.option(
    "--workspace-root",
    "-w",
    "workspace",
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Project root (default: the nearest directory with .devkit/, else the Git top level, else the current one).",
)
SOURCE = click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))


@click.group(name="devkit")
@click.version_option(package_name="devkit")
def cli() -> None:
    """Devkit agent asset distribution tools."""


@cli.command(name="get-context")
@click.argument("bundle_name")
@WORKSPACE
@_json_command
def context(bundle_name: str, workspace: str | None) -> object:
    """Return the full constitution and instruction headers for a synced bundle."""
    return get_context(_workspace(workspace), bundle_name)


@cli.group()
def playbook() -> None:
    """Discover occasional procedures after explicit devkit-playbook invocation."""


@playbook.command(name="search")
@click.argument("query")
@WORKSPACE
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
@_json_command
def search(
    query: str, workspace: str | None, limit: int | None, min_score: float | None, max_bytes: int | None
) -> object:
    """Search synchronized playbook metadata with an English query; return headers only."""
    return search_playbooks(_workspace(workspace), query, limit=limit, min_score=min_score, max_bytes=max_bytes)


@cli.group()
def bundle() -> None:
    """Validate, plan and package local bundle sources."""


@bundle.command()
@SOURCE
@_json_command
def validate(source: Path) -> object:
    """Validate bundle.toml and every declared source."""
    loaded = load_bundle(source)
    return {"name": loaded.name, "version": loaded.version, "assets": len(loaded.assets)}


@bundle.command(name="plan")
@SOURCE
@click.option("--preset", default=None, help="Preset to plan (default: the bundle's default preset, else all).")
@click.option("--agent", "agents", multiple=True, type=click.Choice(AGENT_NAMES), help="Agents to project for.")
@_json_command
def plan(source: Path, preset: str | None, agents: tuple[str, ...]) -> object:
    """Preview every destination a bundle deploys, without a consumer project."""
    return plan_bundle(load_bundle(source), preset, list(agents) or None)


@bundle.command()
@SOURCE
@click.option("--output", required=True, type=click.Path(dir_okay=False, path_type=Path))
@_json_command
def build(source: Path, output: Path) -> object:
    """Build a deterministic ZIP archive with a hashed inventory."""
    return build_bundle(load_bundle(source), output)


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


def _report(result: SyncResult) -> None:
    """Print the result, then its warnings and notices on stderr."""
    click.echo(json.dumps(result, indent=2))
    for item in result["drift"]:
        click.echo(
            f"WARNING: upstream drift detected for {item['bundle']}:{item['asset']}. "
            f"Run 'devkit override diff {item['bundle']}:{item['asset']}' to review.",
            err=True,
        )
    if result["stray"]:
        click.echo(
            f"WARNING: unmanaged files under .devkit/managed/: {', '.join(result['stray'])}. "
            "devkit does not deploy or remove them; move project-owned files out of the managed root.",
            err=True,
        )
    if result["unprojected"]:
        items = ", ".join(f"{item['bundle']}:{item['asset']} ({item['agent']})" for item in result["unprojected"])
        click.echo(
            f"NOTICE: subagents without a native variant for a selected agent were not projected: {items}. "
            "Add the variant, ship a role contract, or narrow 'agents' in .devkit/config.toml.",
            err=True,
        )
    if result["unselected"]:
        names = ", ".join(item["bundle"] for item in result["unselected"])
        click.echo(
            f"NOTICE: installed bundles not selected: {names}. Select with 'devkit add <bundle>[:<preset>]'.",
            err=True,
        )
    for text in result["notices"]:
        click.echo(f"NOTICE: {text}", err=True)


# Builds the configuration edit for a command from the installed bundles and the resolved selection.
ConfigEdit = Callable[[list[InstalledBundle], dict[str, list[str]]], dict[str, Any]]


def _sync_and_save(
    root: Path,
    *,
    save: ConfigEdit | None,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    deselect: tuple[str, ...] = (),
    dry_run: bool = False,
) -> SyncResult:
    """Synchronize; ``save`` builds a configuration edit, checked before the sync and written after it."""
    with discover_bundles() as installed:
        selected = resolve_selection(installed, presets or {})
        edit = save(installed, selected) if save is not None else None
        update = prepare_config_update(root, **edit) if edit is not None and not dry_run else None
        result = sync_project(root, installed, agents=agents, presets=selected, deselect=deselect, dry_run=dry_run)
    if update is not None:
        update.apply()
    return result


@cli.command()
@WORKSPACE
@click.option("--agent", "agents", multiple=True, type=click.Choice(AGENT_NAMES), help="Set agent targets.")
@click.option("--no-agents", is_flag=True, help="Clear agent targets.")
@click.option(
    "--preset",
    "presets",
    multiple=True,
    help="Select bundle[:preset]; a bare bundle uses its default preset; repeat a bundle for a union.",
)
@click.option("--no-save", is_flag=True, help="Apply selection flags to this run without editing .devkit/config.toml.")
@click.option("--dry-run", is_flag=True, help="Report planned actions without writing files or configuration.")
@click.option("--check", is_flag=True, help="Read-only check; exit 1 when synchronization is needed, 2 on error.")
def sync(
    workspace: str | None,
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
    persist = not no_save and (bool(requested) or active_agents is not None)

    @_json_command
    def run() -> None:
        result = _sync_and_save(
            _workspace(workspace),
            save=(lambda _installed, selected: {"agents": active_agents, "presets": selected}) if persist else None,
            agents=active_agents,
            presets=requested,
            dry_run=dry_run or check,
        )
        _report(result)
        if check and result["actions"]:
            raise click.exceptions.Exit(1)

    run()


@cli.command()
@click.argument("selections", nargs=-1, required=True)
@WORKSPACE
@click.option("--dry-run", is_flag=True, help="Preview without editing configuration or files.")
def add(selections: tuple[str, ...], workspace: str | None, dry_run: bool) -> None:
    """Select bundle[:preset] in .devkit/config.toml and synchronize.

    Without a preset, the bundle's default preset is recorded by name.
    """
    requested = _parse_selections(selections, "SELECTIONS")

    @_json_command
    def run() -> None:
        _report(
            _sync_and_save(
                _workspace(workspace),
                save=lambda _installed, selected: {"presets": selected},
                presets=requested,
                dry_run=dry_run,
            )
        )

    run()


@cli.command()
@click.argument("bundles", nargs=-1, required=True)
@WORKSPACE
@click.option("--dry-run", is_flag=True, help="Preview without editing configuration or files.")
def remove(bundles: tuple[str, ...], workspace: str | None, dry_run: bool) -> None:
    """Deselect bundles in .devkit/config.toml and synchronize.

    A built-in bundle is recorded as ``<bundle> = false`` so it is not selected
    by default again; ``devkit add`` selects it again.
    """

    root = _workspace(workspace)

    def save(installed: list[InstalledBundle], _selected: dict[str, list[str]]) -> dict[str, Any]:
        missing = sorted(set(bundles) - set(effective_selection(installed, read_config(root))))
        if missing:
            raise BundleError(f"bundle is not selected: {missing}")
        builtin = {item.bundle.name for item in installed if item.builtin}
        return {
            "deselect": [name for name in bundles if name not in builtin],
            "opt_out": [name for name in bundles if name in builtin],
        }

    @_json_command
    def run() -> None:
        _report(_sync_and_save(root, save=save, deselect=bundles, dry_run=dry_run))

    run()


@cli.command(name="list")
@WORKSPACE
@_json_command
def list_resources(workspace: str | None) -> object:
    """List installed bundles, their selection state, and the project's synchronized asset paths."""
    with discover_bundles() as installed:
        return project_listing(_workspace(workspace), installed)


@cli.command()
@WORKSPACE
@_json_command
def status(workspace: str | None) -> object:
    """Report the installed state against the receipt without writing anything."""
    with discover_bundles() as installed:
        return project_status(_workspace(workspace), installed)


@cli.command()
@WORKSPACE
@_json_command
def recover(workspace: str | None) -> object:
    """Roll back an interrupted synchronization without overwriting later edits."""
    return {"recovered_files": recover_project(_workspace(workspace))}


@cli.group()
def override() -> None:
    """Manage local project asset overrides and upstream drift review."""


@override.command(name="create")
@click.argument("selector")
@WORKSPACE
@click.option("--force", is_flag=True, help="Overwrite existing override files.")
@_json_command
def override_create(selector: str, workspace: str | None, force: bool) -> object:
    """Copy an installed asset (bundle:asset) into .devkit/overrides/ and synchronize."""
    with discover_bundles() as installed:
        return create_override(_workspace(workspace), installed, selector, force=force)


@override.command(name="diff")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_diff(selector: str, workspace: str | None) -> object:
    """Per file: upstream vs override, and recorded baseline vs current upstream (bundle:asset)."""
    with discover_bundles() as installed:
        return diff_override(_workspace(workspace), installed, selector)


@override.command(name="accept")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_accept(selector: str, workspace: str | None) -> object:
    """Record the current upstream as the override's baseline (bundle:asset)."""
    with discover_bundles() as installed:
        return accept_override(_workspace(workspace), installed, selector)


@override.command(name="remove")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_remove(selector: str, workspace: str | None) -> object:
    """Remove a local override and synchronize the pristine upstream asset (bundle:asset)."""
    with discover_bundles() as installed:
        return remove_override(_workspace(workspace), installed, selector)


@override.command(name="list")
@WORKSPACE
@_json_command
def override_list(workspace: str | None) -> object:
    """List tracked overrides and their drift status."""
    with discover_bundles() as installed:
        return list_overrides(_workspace(workspace), installed)
