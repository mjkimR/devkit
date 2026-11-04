"""Agent-first maintenance history CLI; one sentinel per fact or one JSON result."""

from __future__ import annotations

from pathlib import Path

import click
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    exit_on_warnings,
    field_value,
    is_json,
    resolve_root,
    workspace_option,
)

from .models.records import PLAYBOOKS, HistoryResult
from .usecases.operations import HistoryOperation, HistoryRequest

WORKSPACE = workspace_option()
REPOSITORY = click.option("--repository", help="Credential-free owner/repo; defaults to config or origin")
BRANCH = click.option("--branch", help="Dedicated history branch; defaults to config or maintenance-history")
AUTHORITY = click.option("--authority", default="", help="Explicit user authority for this destination mutation")
RUN = click.option("--run", required=True, type=click.Path(path_type=Path, file_okay=False))
FILES = click.option("--file", "files", multiple=True, type=click.Path(path_type=Path, dir_okay=False))
COMMITS = click.option("--applied-commit", "applied_commits", multiple=True)


@click.group(name="maintenance")
def cli() -> None:
    """Maintenance records and durable history."""


@cli.group(name="history")
def history() -> None:
    """Capture runs locally; publish only with explicit authority."""


def emit(result: HistoryResult, output_format: str) -> None:
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        data = {key: value for key, value in result.data.items() if key not in ("record", "runs")}
        fields = " ".join(f"{key}={field_value(value)}" for key, value in data.items())
        click.echo(f"[{result.kind}: {fields}]")
        for run in result.data.get("runs", []):
            click.echo(
                f"[HISTORY_RUN: run_id={field_value(run['run_id'])} source_sha={field_value(run['source_sha'])} outcome={field_value(run['outcome'])}]"
            )
    echo_notices(result.notices)
    exit_on_warnings(result.notices)


@history.command(name="init")
@REPOSITORY
@BRANCH
@AUTHORITY
@WORKSPACE
@FORMAT_OPTION
@boundary
def init_cmd(
    repository: str | None, branch: str | None, authority: str, workspace_root: str | None, output_format: str
) -> None:
    """Initialize or validate an authorized history branch; write no local file."""
    emit(
        HistoryOperation().execute(
            HistoryRequest(
                "init", resolve_root(workspace_root), repository=repository, branch=branch, authority=authority
            )
        ),
        output_format,
    )


@history.command(name="start")
@click.option("--playbook", required=True, type=click.Choice(PLAYBOOKS))
@click.option("--scope", required=True)
@click.option("--into", required=True, type=click.Path(path_type=Path, file_okay=False))
@click.option("--report", required=True, type=click.Path(path_type=Path, dir_okay=False))
@click.option("--timezone", "zone")
@click.option("--supersedes", multiple=True)
@click.option("--prior-run", "prior_runs", multiple=True)
@REPOSITORY
@WORKSPACE
@FORMAT_OPTION
@boundary
def start_cmd(
    playbook: str,
    scope: str,
    into: Path,
    report: Path,
    zone: str | None,
    supersedes: tuple[str, ...],
    prior_runs: tuple[str, ...],
    repository: str | None,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Capture inspected Git content and create a unique local run directory."""
    emit(
        HistoryOperation().execute(
            HistoryRequest(
                "start",
                resolve_root(workspace_root),
                repository=repository,
                playbook=playbook,
                scope=scope,
                into=into,
                report=report,
                timezone=zone,
                supersedes=supersedes,
                prior_runs=prior_runs,
            )
        ),
        output_format,
    )


@history.command(name="finish")
@RUN
@click.option("--outcome", required=True, type=click.Choice(("completed", "failed", "interrupted")))
@click.option("--result")
@click.option("--report", type=click.Path(path_type=Path, dir_okay=False))
@FILES
@COMMITS
@click.option("--follow-up", "follow_ups", multiple=True)
@WORKSPACE
@FORMAT_OPTION
@boundary
def finish_cmd(
    run: Path,
    outcome: str,
    result: str | None,
    report: Path | None,
    files: tuple[Path, ...],
    applied_commits: tuple[str, ...],
    follow_ups: tuple[str, ...],
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Freeze report and --file digests; later publication selects only frozen files."""
    emit(
        HistoryOperation().execute(
            HistoryRequest(
                "finish",
                resolve_root(workspace_root),
                run=run,
                outcome=outcome,
                result=result,
                report=report,
                files=files,
                applied_commits=applied_commits,
                follow_ups=follow_ups,
            )
        ),
        output_format,
    )


@history.command(name="publish")
@RUN
@AUTHORITY
@REPOSITORY
@BRANCH
@FILES
@WORKSPACE
@FORMAT_OPTION
@boundary
def publish_cmd(
    run: Path,
    authority: str,
    repository: str | None,
    branch: str | None,
    files: tuple[Path, ...],
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Publish a finished run and explicitly selected frozen files atomically."""
    emit(
        HistoryOperation().execute(
            HistoryRequest(
                "publish",
                resolve_root(workspace_root),
                run=run,
                authority=authority,
                repository=repository,
                branch=branch,
                files=files,
            )
        ),
        output_format,
    )


@history.command(name="update")
@RUN
@AUTHORITY
@click.option("--integration-state", required=True)
@COMMITS
@WORKSPACE
@FORMAT_OPTION
@boundary
def update_cmd(
    run: Path,
    authority: str,
    integration_state: str,
    applied_commits: tuple[str, ...],
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Append integration state without changing the frozen report or record."""
    emit(
        HistoryOperation().execute(
            HistoryRequest(
                "update",
                resolve_root(workspace_root),
                run=run,
                authority=authority,
                integration_state=integration_state,
                applied_commits=applied_commits,
            )
        ),
        output_format,
    )


@history.command(name="list")
@click.option("--playbook", required=True, type=click.Choice(PLAYBOOKS))
@click.option("--source-sha")
@click.option("--outcome", type=click.Choice(("completed", "failed", "interrupted")))
@click.option("--include-superseded", is_flag=True)
@click.option("--limit", default=20, type=click.IntRange(min=1))
@REPOSITORY
@BRANCH
@WORKSPACE
@FORMAT_OPTION
@boundary
def list_cmd(
    playbook: str,
    source_sha: str | None,
    outcome: str | None,
    include_superseded: bool,
    limit: int,
    repository: str | None,
    branch: str | None,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """List newest runs from history indexes, including later amendments."""
    emit(
        HistoryOperation().execute(
            HistoryRequest(
                "list",
                resolve_root(workspace_root),
                playbook=playbook,
                source_sha=source_sha,
                outcome_filter=outcome,
                include_superseded=include_superseded,
                limit=limit,
                repository=repository,
                branch=branch,
            )
        ),
        output_format,
    )


@history.command(name="get")
@click.option("--run-id", required=True)
@click.option("--file", default="record.json")
@REPOSITORY
@BRANCH
@WORKSPACE
@FORMAT_OPTION
@boundary
def get_cmd(
    run_id: str, file: str, repository: str | None, branch: str | None, workspace_root: str | None, output_format: str
) -> None:
    """Read a published file, preserving its bytes as base64 in the result."""
    emit(
        HistoryOperation().execute(
            HistoryRequest(
                "get", resolve_root(workspace_root), run_id=run_id, file=file, repository=repository, branch=branch
            )
        ),
        output_format,
    )
