"""The distribution commands of ``devkit`` (``sync``, ``add``, ``remove``, ``list``, ``status``, ...).

``register`` adds them to the root ``devkit`` group. Every command prints
exactly one JSON object on stdout: its result's ``to_dict()`` (``override
list`` wraps its entries as ``{"overrides": [...]}``), or ``{"error": {...}}``
when it fails. A failure is also rendered as an Agent Advisory Protocol block
on stderr. Synchronizing commands print warnings and coded notices on stderr
as ``[WARNING: (CODE) ...]`` and ``[NOTICE: (CODE) ...]`` lines; ``devkit
status`` renders each problem of its ``errors`` as an advisory block. Exit
codes follow ``devkit.advisory.ExitCode``: ``0`` success; ``1`` from
``devkit sync --check`` when a synchronization is needed and from
``devkit status`` when the report shows a problem (a missing, modified or
mode-mismatched file, a pending journal, override drift); ``2`` for any error
(an invalid argument, a conflict, a held lock, an unreadable receipt or
configuration).
"""

from __future__ import annotations

import functools
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Protocol

import click

from devkit.advisory import AdvisoryError, ExitCode
from devkit.core.cli import boundary, echo_json, exit_on_problems, resolve_root, workspace_option
from devkit.core.errors import ArgumentError
from devkit.distribution.bundles import build_bundle, load_bundle
from devkit.distribution.bundles.common import AGENT_NAMES, SLUG
from devkit.distribution.errors import OverrideDriftError, SelectionError
from devkit.distribution.installation.config import (
    DEFAULT_PLAYBOOK_LIMIT,
    DEFAULT_PLAYBOOK_MAX_BYTES,
    DEFAULT_PLAYBOOK_MIN_SCORE,
    PLAYBOOK_LIMIT_MAX,
    PLAYBOOK_LIMIT_MIN,
    PLAYBOOK_MAX_BYTES_MAX,
    PLAYBOOK_MAX_BYTES_MIN,
    effective_selection,
    merge_selection,
    prepare_config_update,
    read_config,
    resolve_selection,
)
from devkit.distribution.installation.context import get_context
from devkit.distribution.installation.discovery import InstalledBundle, discover_bundles
from devkit.distribution.installation.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from devkit.distribution.installation.plan import plan_bundle
from devkit.distribution.installation.playbook_search import search_playbooks
from devkit.distribution.installation.results import OverrideChange, SyncResult
from devkit.distribution.installation.status import get_project_listing, get_project_status
from devkit.distribution.installation.sync import recover_project, sync_project

# Code of the stderr warning for files under the managed root that nothing owns.
STRAY_CODE = "MANAGED_FILE_STRAY"


class _Result(Protocol):
    def to_dict(self) -> dict[str, Any]: ...


def _json_command(fn: Callable[..., Any]) -> Callable[..., None]:
    """Run ``fn`` through the JSON-only error boundary and print its result, when it returns one.

    A result is a mapping or an object with ``to_dict()``.
    """

    @boundary(json_only=True)
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        result: Mapping[str, object] | _Result | None = fn(*args, **kwargs)
        if result is not None:
            echo_json(result if isinstance(result, Mapping) else result.to_dict())

    return wrapper


WORKSPACE = workspace_option(
    "Project root (default: the nearest directory with .devkit/, else the Git top level, else the current one)."
)
SOURCE = click.argument("source", type=click.Path(path_type=Path))


@click.command(name="get-context")
@click.argument("bundle_name")
@WORKSPACE
@_json_command
def context(bundle_name: str, workspace_root: str | None) -> object:
    """Return the full constitution and instruction headers for a synced bundle."""
    return get_context(resolve_root(workspace_root), bundle_name)


@click.group()
def playbook() -> None:
    """Discover occasional procedures after explicit devkit-playbook invocation."""


@playbook.command(name="search")
@click.argument("query")
@WORKSPACE
@click.option(
    "--limit",
    default=None,
    type=int,
    help=f"Maximum candidates to return, {PLAYBOOK_LIMIT_MIN}..{PLAYBOOK_LIMIT_MAX}"
    f" (default: [playbooks] limit, else {DEFAULT_PLAYBOOK_LIMIT}).",
)
@click.option(
    "--min-score",
    default=None,
    type=float,
    help=f"Minimum nonnegative score (default: [playbooks] min_score, else {DEFAULT_PLAYBOOK_MIN_SCORE}).",
)
@click.option(
    "--max-bytes",
    default=None,
    type=int,
    help=f"JSON response byte budget, {PLAYBOOK_MAX_BYTES_MIN}..{PLAYBOOK_MAX_BYTES_MAX}"
    f" (default: [playbooks] max_bytes, else {DEFAULT_PLAYBOOK_MAX_BYTES}).",
)
@_json_command
def search(
    query: str, workspace_root: str | None, limit: int | None, min_score: float | None, max_bytes: int | None
) -> object:
    """Search synchronized playbook metadata with an English query; return headers only."""
    return search_playbooks(resolve_root(workspace_root), query, limit=limit, min_score=min_score, max_bytes=max_bytes)


@click.group()
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
            raise ArgumentError(
                f"{param_hint}: expected bundle[:preset] slugs: {value}",
                target_files=[param_hint],
                fix="Pass lowercase bundle slugs, optionally with :<preset>",
            )
        presets = selected.setdefault(name, [])
        if preset and preset not in presets:
            presets.append(preset)
    return selected


def _echo_notices(notices: list[AdvisoryError]) -> None:
    for notice in notices:
        click.echo(f"[NOTICE: ({notice.code}) {notice.message}]", err=True)


def _report(result: SyncResult) -> None:
    """Print the result, then its warnings and notices on stderr."""
    echo_json(result.to_dict())
    for item in result.drift:
        selector = f"{item.bundle}:{item.asset}"
        click.echo(
            f"[WARNING: ({OverrideDriftError.code}) upstream drift behind the override of {selector};"
            f" review it with `devkit override diff {selector}`]",
            err=True,
        )
    if result.stray:
        click.echo(
            f"[WARNING: ({STRAY_CODE}) unmanaged files under .devkit/managed/: {', '.join(result.stray)};"
            " devkit does not deploy or remove them, move project-owned files out of the managed root]",
            err=True,
        )
    if result.unprojected:
        items = ", ".join(f"{item.bundle}:{item.asset} ({item.agent})" for item in result.unprojected)
        click.echo(
            f"[NOTICE: subagents without a native variant for a selected agent were not projected: {items};"
            " add the variant, ship a role contract, or narrow agents in .devkit/config.toml]",
            err=True,
        )
    if result.unselected:
        names = ", ".join(item.bundle for item in result.unselected)
        click.echo(
            f"[NOTICE: installed bundles not selected: {names}; select one with `devkit add <bundle>[:<preset>]`]",
            err=True,
        )
    _echo_notices(result.notices)


def _report_change(change: OverrideChange) -> None:
    """Print an override change, then the notices of the synchronization it ran on stderr."""
    echo_json(change.to_dict())
    _echo_notices(change.notices)


# Builds the configuration edit for a command from the installed bundles and the resolved selection.
ConfigEdit = Callable[[list[InstalledBundle], dict[str, list[str]]], dict[str, Any]]


def _sync_and_save(
    root: Path,
    *,
    save: ConfigEdit | None,
    agents: list[str] | None = None,
    presets: dict[str, list[str]] | None = None,
    merge: bool = False,
    deselect: tuple[str, ...] = (),
    dry_run: bool = False,
) -> SyncResult:
    """Synchronize; ``save`` builds a configuration edit, checked before the sync and written after it.

    ``merge`` joins ``presets`` with what each bundle already deploys instead of replacing it.
    """
    with discover_bundles() as installed:
        selected = resolve_selection(installed, presets or {})
        if merge:
            selected = merge_selection(installed, read_config(root), selected)
        edit = save(installed, selected) if save is not None else None
        update = prepare_config_update(root, **edit) if edit is not None and not dry_run else None
        result = sync_project(root, installed, agents=agents, presets=selected, deselect=deselect, dry_run=dry_run)
    if update is not None:
        update.apply()
    return result


@click.command()
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
@_json_command
def sync(
    workspace_root: str | None,
    agents: tuple[str, ...],
    no_agents: bool,
    presets: tuple[str, ...],
    no_save: bool,
    dry_run: bool,
    check: bool,
) -> None:
    """Synchronize the bundles selected in .devkit/config.toml into a project."""
    if agents and no_agents:
        raise ArgumentError(
            "--agent and --no-agents cannot be combined",
            target_files=["--agent", "--no-agents"],
            fix="Pass --agent to set agent targets or --no-agents to clear them, not both",
        )
    requested = _parse_selections(presets, "--preset")
    active_agents = [] if no_agents else (list(agents) if agents else None)
    persist = not no_save and (bool(requested) or active_agents is not None)
    result = _sync_and_save(
        resolve_root(workspace_root),
        save=(lambda _installed, selected: {"agents": active_agents, "presets": selected}) if persist else None,
        agents=active_agents,
        presets=requested,
        dry_run=dry_run or check,
    )
    _report(result)
    if check and result.actions:
        sys.exit(int(ExitCode.FINDINGS))


@click.command()
@click.argument("selections", nargs=-1, required=True)
@WORKSPACE
@click.option("--dry-run", is_flag=True, help="Preview without editing configuration or files.")
@_json_command
def add(selections: tuple[str, ...], workspace_root: str | None, dry_run: bool) -> None:
    """Add bundle[:preset] to the selection in .devkit/config.toml and synchronize.

    Presets join those the bundle already deploys; `sync --preset` replaces a
    bundle's presets instead. Without a preset, the bundle's default preset is
    recorded by name.
    """
    requested = _parse_selections(selections, "SELECTIONS")
    _report(
        _sync_and_save(
            resolve_root(workspace_root),
            save=lambda _installed, selected: {"presets": selected},
            presets=requested,
            merge=True,
            dry_run=dry_run,
        )
    )


@click.command()
@click.argument("bundles", nargs=-1, required=True)
@WORKSPACE
@click.option("--dry-run", is_flag=True, help="Preview without editing configuration or files.")
@_json_command
def remove(bundles: tuple[str, ...], workspace_root: str | None, dry_run: bool) -> None:
    """Deselect bundles in .devkit/config.toml and synchronize.

    An auto-selected built-in bundle is recorded as `<bundle> = false` so it is
    not selected by default again; `devkit add` selects it again.
    """
    root = resolve_root(workspace_root)

    def save(installed: list[InstalledBundle], _selected: dict[str, list[str]]) -> dict[str, Any]:
        missing = sorted(set(bundles) - set(effective_selection(installed, read_config(root))))
        if missing:
            raise SelectionError(f"bundle is not selected: {missing}", fix="List selected bundles with `devkit list`")
        automatic = {item.bundle.name for item in installed if item.auto_selected}
        return {
            "deselect": [name for name in bundles if name not in automatic],
            "opt_out": [name for name in bundles if name in automatic],
        }

    _report(_sync_and_save(root, save=save, deselect=bundles, dry_run=dry_run))


@click.command(name="list")
@WORKSPACE
@_json_command
def list_resources(workspace_root: str | None) -> object:
    """List installed bundles, their selection state, and the project's synchronized asset paths."""
    with discover_bundles() as installed:
        return get_project_listing(resolve_root(workspace_root), installed)


@click.command()
@WORKSPACE
@_json_command
def status(workspace_root: str | None) -> None:
    """Report the installed state against the receipt without writing anything.

    Problems (a missing, modified or mode-mismatched file, a pending journal,
    override drift) are listed under errors and rendered on stderr; any exits 1.
    """
    with discover_bundles() as installed:
        report = get_project_status(resolve_root(workspace_root), installed)
    echo_json(report.to_dict())
    exit_on_problems(report.errors, report=True)


@click.command()
@WORKSPACE
@_json_command
def recover(workspace_root: str | None) -> object:
    """Roll back an interrupted synchronization without overwriting later edits."""
    return {"recovered_files": recover_project(resolve_root(workspace_root))}


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
    with discover_bundles() as installed:
        change = create_override(resolve_root(workspace_root), installed, selector, force=force)
    _report_change(change)


@override.command(name="diff")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_diff(selector: str, workspace_root: str | None) -> object:
    """Per file: upstream vs override, and recorded baseline vs current upstream (bundle:asset)."""
    with discover_bundles() as installed:
        return diff_override(resolve_root(workspace_root), installed, selector)


@override.command(name="accept")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_accept(selector: str, workspace_root: str | None) -> object:
    """Record the current upstream as the override's baseline (bundle:asset)."""
    with discover_bundles() as installed:
        return accept_override(resolve_root(workspace_root), installed, selector)


@override.command(name="remove")
@click.argument("selector")
@WORKSPACE
@_json_command
def override_remove(selector: str, workspace_root: str | None) -> None:
    """Remove a local override and synchronize the pristine upstream asset (bundle:asset)."""
    with discover_bundles() as installed:
        change = remove_override(resolve_root(workspace_root), installed, selector)
    _report_change(change)


@override.command(name="list")
@WORKSPACE
@_json_command
def override_list(workspace_root: str | None) -> object:
    """List tracked overrides and their drift status."""
    with discover_bundles() as installed:
        return {"overrides": [item.to_dict() for item in list_overrides(resolve_root(workspace_root), installed)]}


COMMANDS: tuple[click.Command, ...] = (
    context,
    playbook,
    bundle,
    sync,
    add,
    remove,
    list_resources,
    status,
    recover,
    override,
)


def register(group: click.Group) -> None:
    """Add every distribution command to ``group`` (the root ``devkit`` group)."""
    for command in COMMANDS:
        group.add_command(command)
