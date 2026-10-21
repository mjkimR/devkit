"""``devkit generated`` commands: list the registered artifacts, check, regenerate, and resolve their conflicts.

Text output: ``list`` prints one ``[GENERATED: <id> source= seed= paths= command=]`` line per artifact; ``regen``
one ``[GENERATED_REGENERATED: <id> changed=]`` line per artifact, ``check`` one ``[GENERATED_CURRENT: ...]`` or
``[GENERATED_STALE: ...]`` line (``[GENERATED_SKIPPED: ...]`` for an optional artifact with nothing tracked), each
followed by a ``[SUMMARY: ...]``; ``resolve`` one ``[GENERATED_RESOLVED: <id> conflicts=
changed=]`` line per artifact (``GENERATED_PLANNED`` under ``--dry-run``), ``[SUMMARY: ...]`` and, when nothing
is left to resolve, ``[NEXT_CMD: git <operation> --continue]``. ``--format json`` prints the result object.
``check`` exits ``1`` when an artifact is stale (``GENERATED_STALE``).
"""

from __future__ import annotations

import json
import re
import shlex

import click
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    Reported,
    boundary,
    echo_json,
    echo_notices,
    exit_on_warnings,
    is_json,
    resolve_root,
    workspace_option,
)

from devkit_agt.features.generated.models.errors import StaleError
from devkit_agt.features.generated.usecases.engine import (
    ArtifactRun,
    RunResult,
    check,
    list_artifacts,
    regenerate,
    resolve,
)

WORKSPACE = workspace_option()
IDS = click.argument("ids", nargs=-1)
_BARE = re.compile(r'[^\s"\]=]+')


def _value(value: object) -> str:
    """``-`` when empty, ``yes``/``no`` for a boolean, bare without spaces, quotes or brackets, else a JSON string."""
    if value is None or value == "":
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    text = str(value)
    return text if _BARE.fullmatch(text) else json.dumps(text, ensure_ascii=False)


@click.group(name="generated")
def cli() -> None:
    """Tracked generated files: regenerate them, check them, and settle their merge conflicts by regenerating."""


@cli.command(name="list")
@WORKSPACE
@FORMAT_OPTION
@boundary
def list_cmd(workspace_root: str | None, output_format: str) -> None:
    """List the registered artifacts: devkit's built-in ones and those of .devkit/generated.toml."""
    artifacts = list_artifacts(resolve_root(workspace_root))
    if is_json(output_format):
        echo_json({"artifacts": [item.to_dict() for item in artifacts]})
        return
    for item in artifacts:
        click.echo(
            f"[GENERATED: {item.id} source={'builtin' if item.builtin else 'project'} seed={item.seed}"
            f" paths={_value(','.join(item.paths))} command={_value(item.command)}]"
        )


def _run_lines(runs: list[ArtifactRun], changed_kind: str, current_kind: str) -> None:
    for item in runs:
        kind = "GENERATED_SKIPPED" if item.skipped else changed_kind if item.changed else current_kind
        click.echo(f"[{kind}: {item.id} changed={len(item.changed)}]")


@cli.command(name="regen")
@IDS
@WORKSPACE
@FORMAT_OPTION
@boundary
def regen_cmd(ids: tuple[str, ...], workspace_root: str | None, output_format: str) -> None:
    """Run the commands of IDS and of the artifacts after them (default: every artifact) in place.

    Stages nothing; refused while the index has unmerged paths (use resolve).
    """
    result = regenerate(resolve_root(workspace_root), ids)
    if is_json(output_format):
        echo_json(result.to_dict())
        return
    _run_lines(result.artifacts, "GENERATED_REGENERATED", "GENERATED_REGENERATED")
    changed = sum(len(item.changed) for item in result.artifacts)
    skipped = sum(item.skipped for item in result.artifacts)
    click.echo(f"[SUMMARY: regenerated={len(result.artifacts) - skipped} changed={changed} skipped={skipped}]")


def _stale_error(result: RunResult) -> StaleError:
    ids = " ".join(shlex.quote(item.id) for item in result.stale)
    paths = [path for item in result.stale for path in item.changed]
    return StaleError(
        f"{len(result.stale)} generated artifact(s) differ from what their command produces at {result.commit}",
        *paths[:20],
        *([f"... and {len(paths) - 20} more"] if len(paths) > 20 else []),
        fix=f"Run `devkit generated regen {ids}` and commit the regenerated files",
    )


@cli.command(name="check")
@IDS
@click.option("--rev", default="HEAD", show_default=True, help="Commit to check")
@WORKSPACE
@FORMAT_OPTION
@boundary
def check_cmd(ids: tuple[str, ...], rev: str, workspace_root: str | None, output_format: str) -> None:
    """Regenerate IDS (default: every artifact) in a temporary worktree of --rev; exit 1 when one differs.

    The checkout is not changed. Run it in CI to catch generated files committed out of date.
    """
    result = check(resolve_root(workspace_root), ids, rev=rev)
    stale = _stale_error(result) if result.stale else None
    if is_json(output_format):
        echo_json(result.to_dict() | ({"errors": [stale.to_dict()]} if stale else {}))
    else:
        _run_lines(result.artifacts, "GENERATED_STALE", "GENERATED_CURRENT")
        skipped = sum(item.skipped for item in result.artifacts)
        click.echo(
            f"[SUMMARY: commit={(result.commit or '')[:12]} checked={len(result.artifacts) - skipped}"
            f" stale={len(result.stale)} skipped={skipped}]"
        )
    if stale:
        raise Reported(stale)


@cli.command(name="resolve")
@click.option("--dry-run", is_flag=True, help="Report what would be resolved; change nothing and run no command")
@WORKSPACE
@FORMAT_OPTION
@boundary
def resolve_cmd(dry_run: bool, workspace_root: str | None, output_format: str) -> None:
    """Settle unmerged paths a generated artifact owns by regenerating them, then stage them.

    Run it while a merge, rebase or cherry-pick stops on conflicts. Never commits; other conflicts stay for you
    to resolve. Refused, with nothing changed, while such a conflict may feed a regeneration.
    """
    result = resolve(resolve_root(workspace_root), dry_run=dry_run)
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        kind = "GENERATED_PLANNED" if dry_run else "GENERATED_RESOLVED"
        for item in result.artifacts:
            if item.skipped:
                click.echo(f"[GENERATED_SKIPPED: {item.id} changed=0]")
            else:
                click.echo(f"[{kind}: {item.id} conflicts={len(item.conflicts)} changed={len(item.changed)}]")
        click.echo(
            f"[SUMMARY: operation={_value(result.operation)} artifacts={len(result.artifacts)}"
            f" remaining={len(result.remaining)} dry_run={_value(dry_run)}]"
        )
        if result.next_command:
            click.echo(f"[NEXT_CMD: {result.next_command}]")
    echo_notices(result.notices)
    exit_on_warnings(result.notices)
