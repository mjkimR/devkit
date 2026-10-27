"""Distribution selection CLI adapters."""

from __future__ import annotations

import click
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
)
from devkit_dist.features.distribution.models.settings import (
    AGENT_NAMES,
    DEFAULT_PRESET,
    SLUG,
)
from devkit_dist.features.distribution.usecases.commands import (
    AddSelection,
    InspectProject,
    ListProject,
    RemoveSelection,
    SyncSelection,
)
from devkit_dist.features.distribution.usecases.sync import RecoverProject, SyncRegistrations
from devkit_dist.features.project.models.invocation import devkit_command

from .output import WORKSPACE, _json_command, _report


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
                fix="Pass lowercase bundle slugs, each optionally followed by a colon and a lowercase preset slug, such as starter:extra",
            )
        presets = selected.setdefault(name, [])
        entry = preset if separator else DEFAULT_PRESET
        if entry not in presets:
            presets.append(entry)
    return selected


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
        registration = SyncRegistrations().execute(resolve_root(workspace_root))
        if is_json(output_format):
            actions = [{"path": path, "action": kind} for path, kind in registration.actions]
            echo_json({"actions": actions, "notices": [item.to_dict() for item in registration.notices]})
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
                fix=f"Run `{devkit_command('sync --locked')}` alone; `{devkit_command('sync --check')}` previews"
                " without writing",
            )
    requested = _parse_selections(presets, "--preset")
    active_agents = [] if no_agents else (list(agents) if agents else None)
    result = SyncSelection().execute(
        resolve_root(workspace_root),
        save=not no_save,
        agents=active_agents,
        presets=requested,
        dry_run=dry_run or check,
        check=check,
        locked=locked,
        environment="cloud" if cloud else "local" if local else None,
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
        AddSelection().execute(
            resolve_root(workspace_root),
            requested,
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
    _report(RemoveSelection().execute(resolve_root(workspace_root), bundles, dry_run=dry_run), output_format)


@click.command(name="list")
@WORKSPACE
@_json_command
def list_resources(workspace_root: str | None) -> None:
    """List installed bundles, their selection state, and the project's synchronized asset paths.

    An installed package the project does not deploy that fails to load is a
    warning under notices in the JSON result.
    """
    listing = ListProject().execute(resolve_root(workspace_root))
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
    whose package fails to load, a pending journal, override drift under
    override_drift = "block") are listed under errors in the JSON result; any
    exits 1. Warnings and notices (override drift under the default "warn", a
    package the project does not deploy that fails to load, MCP registration
    still to set up) are listed under notices. Output is JSON only: nothing is
    repeated on stderr.
    """
    report = InspectProject().execute(resolve_root(workspace_root))
    echo_json(report.to_dict())
    echo_notices(report.notices)
    exit_on_problems(report.errors, report=True)
    exit_on_warnings(report.notices)


@click.command(hidden=True)
@WORKSPACE
@_json_command
def recover(workspace_root: str | None) -> object:
    """Roll back an interrupted synchronization without overwriting later edits."""
    return {"recovered_files": RecoverProject().execute(resolve_root(workspace_root))}
