"""Native isolated execution, persistent inspection and explicit recovery."""

from __future__ import annotations

from pathlib import Path

import click
from devkit_dist.adapters.cli import FORMAT_OPTION, boundary, echo_json, field_value, is_json, yes_no

from devkit_agt.features.isolated_execution.models.record import RunRecord, exit_code, public_record
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
    view = public_record(record)
    if is_json(output_format):
        echo_json(view)
    else:
        values = {
            "id": view.get("run_id"),
            "sha": view.get("sha"),
            "phase": view.get("phase"),
            "outcome": view.get("outcome"),
            "exit": view.get("exit_code"),
            "observer": view.get("observer"),
            "cleanup": view.get("cleanup", {}).get("outcome"),
            "managed": view.get("managed_count"),
            "log": view.get("log"),
            "result": view.get("result"),
        }
        fields = " ".join(
            f"{key}={field_value(str(value) if value is not None else None)}" for key, value in values.items()
        )
        truncated = bool(
            view["truncated_fields"]
            or view.get("argv_truncated")
            or view.get("managed_omitted")
            or view.get("tail", {}).get("truncated")
        )
        click.echo(f"[EXECUTION_RESULT: {fields} truncated={yes_no(truncated)}]")
        if "cleanup" in view:
            cleanup = view["cleanup"]
            click.echo(
                f"[EXECUTION_CLEANUP: outcome={field_value(cleanup.get('outcome'))} code={field_value(cleanup.get('code'))} detail={field_value(cleanup.get('detail'))}]"
            )
        if "detail" in view:
            click.echo(f"[EXECUTION_DETAIL: message={field_value(view['detail'])}]")
        for line in view.get("lines", []):
            click.echo(f"[EXECUTION_LOG_LINE: text={field_value(line)}]")
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
@click.option("--limit", default=20, type=int, show_default=True)
@click.option("--offset", default=0, type=int, show_default=True)
@FORMAT_OPTION
@boundary
def list_runs(output_format: str, limit: int, offset: int) -> None:
    """List retained execution evidence, including pending runs."""
    page = ListExecutions().execute(Path.cwd(), limit=limit, offset=offset)
    if is_json(output_format):
        echo_json(page)
    else:
        click.echo(
            f"[EXECUTION_LIST: total={page['total']} offset={page['offset']} count={len(page['runs'])} next={field_value(str(page['next_offset']) if page['next_offset'] is not None else None)}]"
        )
        for record in page["runs"]:
            click.echo(
                f"[EXECUTION_RUN: id={field_value(record['run_id'])} sha={field_value(record.get('sha'))} phase={field_value(record['phase'])}]"
            )


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
