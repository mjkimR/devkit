"""Native isolated execution, persistent inspection and explicit recovery."""

from __future__ import annotations

import json
from pathlib import Path

import click
from devkit_dist.adapters.cli import FORMAT_OPTION, boundary, echo_json, is_json

from devkit_agt.features.isolated_execution.models.record import RunRecord, exit_code
from devkit_agt.features.isolated_execution.usecases.operations import (
    CancelExecution,
    CleanExecution,
    ExecutionLogs,
    InspectExecution,
    ListExecutions,
    StartExecution,
    WaitExecution,
)


def output(record: RunRecord, output_format: str) -> None:
    if is_json(output_format):
        echo_json(record)
    else:
        click.echo(f"[EXECUTION_RESULT: {json.dumps(record, ensure_ascii=False)}]")
    raise click.exceptions.Exit(exit_code(record))


@click.group()
def cli() -> None:
    """Run native commands at fixed commits in isolated background checkouts."""


@cli.command("start", context_settings={"ignore_unknown_options": True})
@click.option("--ref", "sha", required=True, help="Full locally available commit SHA.")
@click.option("--setup", default=None, help="Override the configured worktree setup shell command.")
@FORMAT_OPTION
@click.argument("argv", nargs=-1, type=click.UNPROCESSED)
@boundary
def start(sha: str, setup: str | None, argv: tuple[str, ...], output_format: str) -> None:
    """Prepare an isolated checkout and run native ARGV after -- in the background."""
    output(StartExecution().execute(Path.cwd(), sha, argv, setup), output_format)


@cli.command("list")
@FORMAT_OPTION
@boundary
def list_runs(output_format: str) -> None:
    """List retained execution evidence, including pending runs."""
    records = ListExecutions().execute(Path.cwd())
    if is_json(output_format):
        echo_json({"runs": records})
    else:
        for record in records:
            click.echo(f"[EXECUTION_RUN: id={record['run_id']} sha={record['sha']} phase={record['phase']}]")


@cli.command("status")
@click.argument("run_id")
@FORMAT_OPTION
@boundary
def status(run_id: str, output_format: str) -> None:
    """Inspect a run from any checkout of this repository."""
    output(InspectExecution().execute(Path.cwd(), run_id), output_format)


@cli.command("logs")
@click.argument("run_id")
@click.option("--tail", default=100, type=int, show_default=True)
@FORMAT_OPTION
@boundary
def logs(run_id: str, tail: int, output_format: str) -> None:
    """Read a bounded tail; full output remains at its recorded path."""
    output(ExecutionLogs().execute(Path.cwd(), run_id, tail), output_format)


@cli.command("wait")
@click.argument("run_id")
@click.option("--clean", is_flag=True, help="Request guarded cleanup after a durable terminal result.")
@click.option("--timeout", type=float, default=None)
@FORMAT_OPTION
@boundary
def wait(run_id: str, clean: bool, timeout: float | None, output_format: str) -> None:
    """Observe internally; timeout or interruption leaves execution running."""
    output(WaitExecution().execute(Path.cwd(), run_id, timeout=timeout, clean=clean), output_format)


@cli.command("cancel")
@click.argument("run_id")
@FORMAT_OPTION
@boundary
def cancel(run_id: str, output_format: str) -> None:
    """Stop managed writers and retain the checkout and evidence."""
    output(CancelExecution().execute(Path.cwd(), run_id), output_format)


@cli.command("clean")
@click.argument("run_id")
@FORMAT_OPTION
@boundary
def clean(run_id: str, output_format: str) -> None:
    """Remove only an inactive run-owned clean checkout, preserving evidence."""
    output(CleanExecution().execute(Path.cwd(), run_id), output_format)
