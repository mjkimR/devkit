"""The distribution commands of ``devkit`` (``sync``, ``add``, ``remove``, ``list``, ``status``, ``config``, ...).

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
when it refuses to change committed files (the ``RECEIPT_STALE`` error), and from
``devkit status`` when the report shows a problem (a missing, stale, modified,
mode-mismatched, symlinked or non-regular managed file, a symlinked or
malformed root ``AGENTS.md``, a selected bundle whose package fails to load or is not installed,
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
from devkit_core.base.errors import ArgumentError

from devkit_dist.adapters.cli import (
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
from devkit_dist.features.distribution.models.results import OverrideChange, SyncResult
from devkit_dist.features.distribution.models.settings import (
    AGENT_NAMES,
    DEFAULT_PLAYBOOK_LIMIT,
    DEFAULT_PLAYBOOK_MAX_BYTES,
    DEFAULT_PLAYBOOK_MIN_SCORE,
    DEFAULT_PLAYBOOK_MIN_SIMILARITY,
    DEFAULT_PLAYBOOK_MODE,
    PLAYBOOK_LIMIT_MAX,
    PLAYBOOK_LIMIT_MIN,
    PLAYBOOK_MAX_BYTES_MAX,
    PLAYBOOK_MAX_BYTES_MIN,
)
from devkit_dist.features.distribution.usecases import commands as operations
from devkit_dist.features.distribution.usecases.commands import (
    _parse_selections,
    _sync_and_save,
    build_source,
    plan_source,
    preview_config_template,
    refresh_config_template,
    remove_selection,
    show_configuration,
    validate_source,
)
from devkit_dist.features.distribution.usecases.context import get_context
from devkit_dist.features.distribution.usecases.override_commands import (
    accept_override,
    create_override,
    diff_override,
    list_overrides,
    remove_override,
)
from devkit_dist.features.distribution.usecases.playbook_get import get_playbook, validate_playbook_id
from devkit_dist.features.distribution.usecases.playbook_search import search_playbooks
from devkit_dist.features.distribution.usecases.status import get_project_listing, get_project_status
from devkit_dist.features.distribution.usecases.sync import recover_project, sync_registrations
from devkit_dist.features.search import SearchMode


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


@playbook.command(name="get")
@click.argument("playbook_id")
@WORKSPACE
@_json_command
def playbook_get(playbook_id: str, workspace_root: str | None) -> object:
    """Return a complete synchronized playbook by exact bundle/asset ID without executing it."""
    validate_playbook_id(playbook_id)
    return get_playbook(resolve_root(workspace_root), playbook_id)


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
    help="Ranking: auto (hybrid with the search extra, devkit-dist[search] or devkit-agt[search], else lexical), lexical, dense or hybrid"
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
    return validate_source(source)


@bundle.command(name="plan")
@SOURCE
@click.option("--preset", default=None, help="Preset to plan (default: the bundle's default preset, else all).")
@click.option("--agent", "agents", multiple=True, type=click.Choice(AGENT_NAMES), help="Agents to project for.")
@_json_command
def plan(source: Path, preset: str | None, agents: tuple[str, ...]) -> object:
    """Preview every destination a bundle deploys, without a consumer project."""
    return plan_source(source, preset, agents)


@bundle.command()
@SOURCE
@click.option("--output", required=True, type=click.Path(dir_okay=False, path_type=Path))
@_json_command
def build(source: Path, output: Path) -> object:
    """Build a deterministic ZIP archive with a hashed inventory."""
    return build_source(source, output)


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
@click.option("--cloud", is_flag=True, help="Select cloud execution in this checkout.")
@click.option("--local", is_flag=True, help="Select local execution in this checkout.")
@click.option("--no-save", is_flag=True, help="Apply selection flags to this run without editing .devkit/config.toml.")
@click.option("--dry-run", is_flag=True, help="Report planned actions without writing files or configuration.")
@click.option("--check", is_flag=True, help="Read-only check; exit 1 when synchronization is needed, 2 on error.")
@click.option(
    "--registrations-only", is_flag=True, help="Reconcile only optional local MCP registration after asset restoration."
)
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
    cloud: bool,
    local: bool,
    dry_run: bool,
    check: bool,
    locked: bool,
    registrations_only: bool,
    output_format: str,
) -> None:
    """Synchronize the bundles selected in .devkit/config.toml into a project.

    `--locked` is for a fresh clone, a new worktree and CI: it restores the
    Git-ignored copies the committed receipt records and never changes the
    receipt, the root AGENTS.md block or seeded files.
    """
    if registrations_only:
        if any((agents, no_agents, presets, no_save, cloud, local, dry_run, check, locked)):
            raise ArgumentError("--registrations-only cannot be combined with other sync modes or selections")
        registration = sync_registrations(resolve_root(workspace_root))
        if is_json(output_format):
            echo_json({"actions": registration.changes, "notices": [item.to_dict() for item in registration.notices]})
        else:
            click.echo(f"[MCP_REGISTRATION: changes={len(registration.changes)}]")
        echo_notices(registration.notices)
        exit_on_warnings(registration.notices)
        return
    if cloud and local:
        raise ArgumentError("--cloud and --local cannot be combined", target_files=["--cloud", "--local"])
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
        environment="cloud" if cloud else "local" if local else None,
        save_environment=not no_save,
    )
    _report(result, output_format, check=check)


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
    _report(remove_selection(resolve_root(workspace_root), bundles, dry_run=dry_run), output_format)


@click.command(name="list")
@WORKSPACE
@_json_command
def list_resources(workspace_root: str | None) -> None:
    """List installed bundles, their selection state, and the project's synchronized asset paths.

    An installed package the project does not deploy that fails to load is a warning on stderr.
    """
    with operations.discover_bundles() as installed:
        listing = get_project_listing(resolve_root(workspace_root), installed)
    echo_json(listing.to_dict())
    echo_notices(listing.notices)
    exit_on_warnings(listing.notices)


@click.command()
@WORKSPACE
@_json_command
def status(workspace_root: str | None) -> None:
    """Report the installed state against the receipt without writing anything.

    Problems (a missing, stale, modified, mode-mismatched, symlinked or
    non-regular managed file, a symlinked or malformed root AGENTS.md, a selected bundle
    whose package fails to load, a pending journal, override drift) are listed
    under errors and rendered on stderr; any exits 1. A package the project
    does not deploy that fails to load is a warning under notices.
    """
    with operations.discover_bundles() as installed:
        report = get_project_status(resolve_root(workspace_root), installed)
    echo_json(report.to_dict())
    echo_notices(report.notices)
    exit_on_problems(report.errors, report=True)
    exit_on_warnings(report.notices)


@click.group()
def config() -> None:
    """Maintain the project configuration, .devkit/config.toml."""


@config.command(name="show")
@WORKSPACE
@click.option("--effective", is_flag=True, required=True, help="Show effective configuration and source paths.")
@FORMAT_OPTION
@boundary
def config_show(workspace_root: str | None, effective: bool, output_format: str) -> None:
    """Inspect effective checkout preferences without changing configuration."""
    echo_json(show_configuration(resolve_root(workspace_root)))


@config.command(name="template")
@WORKSPACE
@click.option(
    "--print",
    "print_only",
    is_flag=True,
    help="Write nothing; add the whole file the template would produce to the output as text.",
)
@_json_command
def config_template(workspace_root: str | None, print_only: bool) -> None:
    """Add the commented template to .devkit/config.toml: every key it lacks, at its default.

    devkit's top-level keys go after the file's last top-level key, the [tool.<name>] tables of installed tools
    (the devkit.config_template entry points) at the end. Existing lines are never changed. Prints path, state
    (created, updated or unchanged) and added; a tool whose template fails is a warning under notices. With
    --print nothing is written and text holds the resulting file.
    """
    root = resolve_root(workspace_root)
    result = preview_config_template(root) if print_only else refresh_config_template(root)
    echo_json(result.to_dict())
    echo_notices(result.notices)
    exit_on_warnings(result.notices)


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


COMMANDS: tuple[click.Command, ...] = (
    context,
    playbook,
    bundle,
    sync,
    add,
    remove,
    list_resources,
    status,
    config,
    recover,
    override,
)
