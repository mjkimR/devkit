"""The distribution commands of ``devkit`` (``sync``, ``add``, ``remove``, ``list``, ``status``, ...).

``COMMANDS`` lists them; the root ``devkit`` group loads each one by name. ``sync``, ``add`` and
``remove`` print text by default: one ``[SYNC: ...]`` line counting the writes,
one ``[CHANGE: <action> <path>]`` line per write, and ``[OK: ...]`` when there
was nothing to write; their warnings and notices follow on stderr as
advisory blocks (``--strict`` exits 1 on a warning). Their ``--format json``,
and every other command, prints exactly one JSON object on stdout: the
result's ``to_dict()`` (``override list`` wraps its entries as
``{"overrides": [...]}``), or ``{"error": {...}}`` when it fails. A JSON
result carries its errors, warnings and notices, so nothing is rendered on
stderr in JSON mode. Exit
codes follow ``devkit.advisory.ExitCode``: ``0`` success; ``1`` from
``devkit sync --check`` when a synchronization is needed, from ``devkit sync --locked``
when it would change committed files (``RECEIPT_STALE``), and from
``devkit status`` when the report shows a problem (a missing, modified,
mode-mismatched, symlinked or non-regular managed file, a symlinked or
malformed root ``AGENTS.md``, a selected bundle whose package fails to load,
a pending journal, override drift); ``2`` for any error
(an invalid argument, a conflict, a held lock, an unreadable receipt or
configuration).
"""

from __future__ import annotations

import functools
import json
import sys
from collections import Counter
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Protocol

import click

from devkit.advisory import ExitCode
from devkit.core.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    exit_on_problems,
    exit_on_warnings,
    is_json,
    resolve_root,
    workspace_option,
)
from devkit.core.errors import ArgumentError
from devkit.distribution.bundles import build_bundle, load_bundle
from devkit.distribution.bundles.common import AGENT_NAMES, SLUG
from devkit.distribution.errors import SelectionError
from devkit.distribution.installation.config import (
    DEFAULT_PLAYBOOK_LIMIT,
    DEFAULT_PLAYBOOK_MAX_BYTES,
    DEFAULT_PLAYBOOK_MIN_SCORE,
    DEFAULT_PLAYBOOK_MIN_SIMILARITY,
    DEFAULT_PLAYBOOK_MODE,
    DEFAULT_PRESET,
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
from devkit.distribution.installation.discovery import InstalledBundle, discover_bundles, unusable_bundles
from devkit.distribution.installation.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from devkit.distribution.installation.plan import plan_bundle
from devkit.distribution.installation.playbook_search import search_playbooks
from devkit.distribution.installation.receipt import read_receipt
from devkit.distribution.installation.results import OverrideChange, SyncResult
from devkit.distribution.installation.status import get_project_listing, get_project_status
from devkit.distribution.installation.sync import recover_project, sync_project
from devkit.search import SearchMode


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
    help=f"Minimum nonnegative lexical (BM25) score (default: [playbooks] min_score, else {DEFAULT_PLAYBOOK_MIN_SCORE}).",
)
@click.option(
    "--min-similarity",
    default=None,
    type=float,
    help="Minimum cosine similarity, 0..1, for the dense ranking"
    f" (default: [playbooks] min_similarity, else {DEFAULT_PLAYBOOK_MIN_SIMILARITY}).",
)
@click.option(
    "--mode",
    default=None,
    type=click.Choice([mode.value for mode in SearchMode], case_sensitive=False),
    help="Ranking: auto (hybrid with the devkit[search] extra, else lexical), lexical, dense or hybrid"
    f" (default: [playbooks] mode, else {DEFAULT_PLAYBOOK_MODE}).",
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
    query: str,
    workspace_root: str | None,
    limit: int | None,
    min_score: float | None,
    min_similarity: float | None,
    mode: str | None,
    max_bytes: int | None,
) -> object:
    """Search synchronized playbook metadata with an English query; return headers only."""
    return search_playbooks(
        resolve_root(workspace_root),
        query,
        limit=limit,
        min_score=min_score,
        min_similarity=min_similarity,
        max_bytes=max_bytes,
        mode=mode,
    )


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
    """Parse ``bundle[:preset]`` values; repeating a bundle selects a union, a bare bundle its default preset.

    A bare bundle is recorded as ``DEFAULT_PRESET``, so ``starter starter:extra`` keeps the default preset.
    """
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
        entry = preset if separator else DEFAULT_PRESET
        if entry not in presets:
            presets.append(entry)
    return selected


def _text_value(value: str) -> str:
    """``value`` bare, or as a JSON string when it would not stay one token of a sentinel line."""
    return json.dumps(value, ensure_ascii=False) if not value or any(c in value for c in ' "[]\\\n') else value


def _echo_sync_text(result: SyncResult) -> None:
    """The text form of a synchronization: what it wrote (or would write), never the deployed state it kept.

    The state (selection, packages, assets) is the same on every run, so it is left to
    ``--format json`` and ``devkit list``; drift, stray files, unprojected subagents and
    unselected bundles reach the agent as the advisories ``echo_notices`` prints.
    """
    counts = Counter(item.action for item in result.actions)
    fields = " ".join(f"{name}={counts[name]}" for name in ("create", "update", "remove", "seed"))
    click.echo(f"[SYNC: {fields} dry_run={'yes' if result.dry_run else 'no'}]")
    for item in result.actions:
        click.echo(f"[CHANGE: {item.action} {_text_value(item.path)}]")
    if not result.actions:
        click.echo("[OK: the workspace matches the selection]")


def _report(result: SyncResult, output_format: str, *, check: bool = False) -> None:
    """Print the result, then its warnings and notices on stderr.

    Exits 1 when ``check`` finds a synchronization needed, or under ``--strict`` when there is a warning.
    """
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        _echo_sync_text(result)
    echo_notices(result.notices)
    if check and result.actions:
        sys.exit(int(ExitCode.FINDINGS))
    exit_on_warnings(result.notices)


def _report_change(change: OverrideChange) -> None:
    """Print an override change, then the warnings and notices of the synchronization it ran."""
    echo_json(change.to_dict())
    echo_notices(change.notices)
    exit_on_warnings(change.notices)


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
    locked: bool = False,
) -> SyncResult:
    """Synchronize; ``save`` builds a configuration edit that the sync renders and writes under the project lock.

    ``merge`` joins ``presets`` with what each bundle already deploys, read
    from the configuration when the edit is rendered, instead of replacing it.
    Without ``save``, or on ``dry_run``, the selection applies to this run only.
    ``deselect`` applies to the run in either case, so a bundle the edit cannot
    name (one the receipt keeps deployed without an installed package) leaves
    the receipt.
    """
    with discover_bundles() as installed:
        requested = resolve_selection(installed, presets or {})

        def selected() -> dict[str, list[str]]:
            return merge_selection(installed, read_config(root), requested) if merge else requested

        if save is not None and not dry_run:
            return sync_project(
                root,
                installed,
                deselect=deselect,
                save=lambda: prepare_config_update(root, **save(installed, selected())),
            )
        selection = selected()
        if save is not None:
            save(installed, selection)  # a preview refuses what the command would refuse
        return sync_project(
            root, installed, agents=agents, presets=selection, deselect=deselect, dry_run=dry_run, locked=locked
        )


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
@click.option(
    "--locked",
    is_flag=True,
    help="Only restore files the receipt records; write nothing and exit 1 when committed files would change.",
)
@FORMAT_OPTION
@boundary
def sync(
    workspace_root: str | None,
    agents: tuple[str, ...],
    no_agents: bool,
    presets: tuple[str, ...],
    no_save: bool,
    dry_run: bool,
    check: bool,
    locked: bool,
    output_format: str,
) -> None:
    """Synchronize the bundles selected in .devkit/config.toml into a project.

    `--locked` is for a fresh clone, a new worktree and CI: it restores the
    Git-ignored copies the committed receipt records and never changes the
    receipt, the root AGENTS.md block or seeded files.
    """
    if agents and no_agents:
        raise ArgumentError(
            "--agent and --no-agents cannot be combined",
            target_files=["--agent", "--no-agents"],
            fix="Pass --agent to set agent targets or --no-agents to clear them, not both",
        )
    if locked:
        combined = [
            flag
            for flag, value in (
                ("--agent", agents),
                ("--no-agents", no_agents),
                ("--preset", presets),
                ("--no-save", no_save),
                ("--dry-run", dry_run),
                ("--check", check),
            )
            if value
        ]
        if combined:
            raise ArgumentError(
                f"--locked cannot be combined with {', '.join(combined)}",
                target_files=["--locked", *combined],
                fix="Run `devkit sync --locked` alone; `devkit sync --check` previews without writing",
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
        locked=locked,
    )
    _report(result, output_format, check=check or (locked and result.dry_run))


@click.command()
@click.argument("selections", nargs=-1, required=True)
@WORKSPACE
@click.option("--dry-run", is_flag=True, help="Preview without editing configuration or files.")
@FORMAT_OPTION
@boundary
def add(selections: tuple[str, ...], workspace_root: str | None, dry_run: bool, output_format: str) -> None:
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
        ),
        output_format,
    )


@click.command()
@click.argument("bundles", nargs=-1, required=True)
@WORKSPACE
@click.option("--dry-run", is_flag=True, help="Preview without editing configuration or files.")
@FORMAT_OPTION
@boundary
def remove(bundles: tuple[str, ...], workspace_root: str | None, dry_run: bool, output_format: str) -> None:
    """Deselect bundles in .devkit/config.toml and synchronize.

    An auto-selected bundle is recorded as `<bundle> = false` so it is not
    selected by default again; `devkit add` selects it again. A deployed bundle
    whose package is no longer installed only leaves the receipt.
    """
    root = resolve_root(workspace_root)

    def save(installed: list[InstalledBundle], _selected: dict[str, list[str]]) -> dict[str, Any]:
        config = read_config(root)
        selected = effective_selection(installed, config, read_receipt(root))
        missing = sorted(set(bundles) - set(selected))
        if missing:
            raise SelectionError(f"bundle is not selected: {missing}", fix="List selected bundles with `devkit list`")
        # Deleting an entry would not deselect a bundle selected without one (auto-selected, or kept deployed
        # because its package no longer loads), so those are opted out. One kept deployed without an installed
        # package needs no entry: the run's deselection drops it from the receipt, and nothing selects it again.
        absent = set(selected) - set(config.presets) - {item.bundle.name for item in installed}
        absent -= unusable_bundles(installed).keys()
        automatic = {item.bundle.name for item in installed if item.auto_selected} | (
            set(selected) - set(config.presets) - absent
        )
        return {
            "deselect": [name for name in bundles if name not in automatic | absent],
            "opt_out": [name for name in bundles if name in automatic],
        }

    _report(_sync_and_save(root, save=save, deselect=bundles, dry_run=dry_run), output_format)


@click.command(name="list")
@WORKSPACE
@_json_command
def list_resources(workspace_root: str | None) -> None:
    """List installed bundles, their selection state, and the project's synchronized asset paths.

    An installed package the project does not deploy that fails to load is a warning on stderr.
    """
    with discover_bundles() as installed:
        listing = get_project_listing(resolve_root(workspace_root), installed)
    echo_json(listing.to_dict())
    echo_notices(listing.notices)
    exit_on_warnings(listing.notices)


@click.command()
@WORKSPACE
@_json_command
def status(workspace_root: str | None) -> None:
    """Report the installed state against the receipt without writing anything.

    Problems (a missing, modified, mode-mismatched, symlinked or non-regular
    managed file, a symlinked or malformed root AGENTS.md, a selected bundle
    whose package fails to load, a pending journal, override drift) are listed
    under errors and rendered on stderr; any exits 1. A package the project
    does not deploy that fails to load is a warning under notices.
    """
    with discover_bundles() as installed:
        report = get_project_status(resolve_root(workspace_root), installed)
    echo_json(report.to_dict())
    echo_notices(report.notices)
    exit_on_problems(report.errors, report=True)
    exit_on_warnings(report.notices)


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
