from __future__ import annotations

import functools
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import click
from agent_advisory import as_advisory_error

from agent_commit_gate import git, hooks
from agent_commit_gate.config import load_gates_config
from agent_commit_gate.models import GateContext, Outcome, Stage
from agent_commit_gate.registry import project_registry
from agent_commit_gate.runner import StageReport, run_stage

VERBOSE_ENV = "DEVKIT_GATES_VERBOSE"

WORKSPACE = click.option(
    "--workspace-root",
    "-w",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Any directory inside the repository",
)
FORMAT = click.option(
    "--format", "output_format", type=click.Choice(["text", "json"]), default="text", help="Output format"
)


def _boundary(fn: Callable[..., None]) -> Callable[..., None]:
    """Render any error as an advisory on stderr."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            fn(*args, **kwargs)
        except (click.exceptions.Exit, click.ClickException, SystemExit):
            raise
        except Exception as exc:
            error = as_advisory_error(exc)
            click.echo(error.render(), err=True)
            sys.exit(int(error.exit_code))

    return wrapper


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)


@click.group(name="commit-gate")
@click.version_option(package_name="agent-commit-gate")
def cli() -> None:
    """Pluggable Git commit gates."""


@cli.command(name="install")
@WORKSPACE
@click.option("--force", is_flag=True, help=f"Move existing unmanaged hooks to <hook>{hooks.BACKUP_SUFFIX}")
@click.option("--python", "python", default=None, help="Interpreter the wrappers exec (default: this one)")
@_boundary
def install_cmd(workspace_root: str, force: bool, python: str | None) -> None:
    """Install the pre-commit, commit-msg and post-commit wrappers."""
    for action in hooks.install(Path(workspace_root), python or sys.executable, force=force):
        click.echo(f"[HOOK: {action}]")


@cli.command(name="uninstall")
@WORKSPACE
@_boundary
def uninstall_cmd(workspace_root: str) -> None:
    """Remove managed wrappers and restore hooks moved aside by install --force."""
    actions = hooks.uninstall(Path(workspace_root))
    for action in actions or ["no managed hooks"]:
        click.echo(f"[HOOK: {action}]")


@cli.command(name="status")
@WORKSPACE
@FORMAT
@_boundary
def status_cmd(workspace_root: str, output_format: str) -> None:
    """Show hook wrappers, every known gate with its effective state, and the configuration layers."""
    cwd = Path(workspace_root)
    root = git.repo_root(cwd)
    registry = project_registry(root)
    config = load_gates_config(root, git.common_git_dir(cwd))
    hook_rows = [
        {
            "stage": item.stage.value,
            "state": item.state.value,
            "python": item.python,
            "python_ok": item.python_ok if item.state is hooks.HookState.MANAGED else None,
            "backup": item.backup,
        }
        for item in hooks.status(cwd)
    ]
    gate_rows = [
        {
            "id": gate.id,
            "stage": gate.stage.value,
            "order": gate.order,
            "enabled": config.enabled(gate),
            "source": registry.sources[gate.id],
            "description": gate.description,
        }
        for gate in registry.get_all()
    ]
    sources = [_rel(path, root) for path in config.sources]
    errors = [error.message for error in registry.errors]
    if output_format == "json":
        click.echo(json.dumps({"hooks": hook_rows, "gates": gate_rows, "config_sources": sources, "errors": errors}))
        return
    for row in hook_rows:
        extra = f" python={row['python']} python_ok={str(row['python_ok']).lower()}" if row["python"] else ""
        click.echo(f"[HOOK: {row['stage']} state={row['state']}{extra}]")
    for row in gate_rows:
        click.echo(
            f"[GATE: {row['id']} stage={row['stage']} order={row['order']} "
            f"enabled={str(row['enabled']).lower()} source={row['source']}]"
        )
    click.echo(f"[CONFIG: sources={','.join(sources) or 'none'}]")
    for error in registry.errors:
        click.echo(error.render(), err=True)


def _report(report: StageReport, verbose: bool) -> None:
    for error in report.errors:
        click.echo(f"[GATE_CONFIG: stage={report.stage}]", err=True)
        click.echo(error.render(), err=True)
    for run in report.runs:
        if run.outcome is Outcome.FAILED and run.error is not None:
            click.echo(f"[GATE: {run.gate_id} stage={report.stage} outcome=failed]", err=True)
            click.echo(run.error.render(), err=True)
        elif verbose:
            note = f" note={run.note}" if run.note else ""
            click.echo(f"[GATE: {run.gate_id} stage={report.stage} outcome={run.outcome}{note}]", err=True)


@cli.command(name="run", context_settings={"ignore_unknown_options": True})
@WORKSPACE
@click.option("--verbose", "-v", is_flag=True, help=f"Also report passed and skipped gates (or set {VERBOSE_ENV}=1)")
@click.argument("stage", type=click.Choice([stage.value for stage in Stage]))
@click.argument("hook_args", nargs=-1, type=click.UNPROCESSED)
@_boundary
def run_cmd(workspace_root: str, verbose: bool, stage: str, hook_args: tuple[str, ...]) -> None:
    """Run one stage's gates; this is what the hook wrappers call."""
    cwd = Path(workspace_root)
    root = git.repo_root(cwd)
    current = Stage(stage)
    git_dir = git.common_git_dir(cwd)
    report = run_stage(
        GateContext(repo_root=root, git_dir=git_dir, stage=current, args=hook_args),
        project_registry(root),
        load_gates_config(root, git_dir),
    )
    _report(report, verbose or os.environ.get(VERBOSE_ENV) == "1")
    if report.failed and current.blocking:
        sys.exit(1)
