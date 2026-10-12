"""``devkit gate`` commands: install and uninstall the hook wrappers, report the setup, run a stage.

A thin command line over the library: ``status`` renders
``devkit.gate.load_gate_project`` and ``run`` renders ``devkit.gate.run_hook``.
Every command works on the top level of the Git work tree containing
``--workspace-root`` (default: the current directory), resolved with
``devkit.core.require_git_toplevel``. ``status --format json`` prints one
object (``{"hooks_dir", "hooks_path", "hooks", "gates", "config_sources",
"errors"}``) or ``{"error"}``. ``status`` is a report: it exits 1 when it lists
any problem that would fail a commit and 2 only when it cannot run. A blocking
``run`` exits with the highest ``exit_code`` among the problems it reports.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from devkit.advisory import as_advisory_error
from devkit.core import require_git_toplevel
from devkit.core.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    existing_directory,
    is_json,
    report_exit_code,
    workspace_option,
)
from devkit.gate.engine.models import Outcome, Stage
from devkit.gate.engine.registry import display_path
from devkit.gate.engine.runner import StageReport, load_gate_project, run_hook
from devkit.gate.hooks import hooks

VERBOSE_ENV = "DEVKIT_GATES_VERBOSE"

WORKSPACE = workspace_option(
    "Any directory inside the repository [default: the current directory]; "
    "gates always run for the work tree's top level"
)


def _start(workspace_root: str | None) -> Path:
    """``--workspace-root`` (an existing directory) or the current directory."""
    return existing_directory(workspace_root) if workspace_root is not None else Path.cwd()


def _repo_root(workspace_root: str | None) -> Path:
    """The Git top level containing ``--workspace-root`` (default: the current directory)."""
    return require_git_toplevel(_start(workspace_root))


@click.group(name="gate")
def cli() -> None:
    """Pluggable Git commit gates."""


@cli.command(name="install")
@WORKSPACE
@click.option(
    "--force",
    is_flag=True,
    help=f"Move existing unmanaged hooks to <hook>{hooks.BACKUP_SUFFIX}; the wrappers keep running them first",
)
@click.option(
    "--python",
    "python",
    default=None,
    help="Fallback interpreter the wrappers exec when the work tree's .venv has no devkit (default: this one)",
)
@boundary
def install_cmd(workspace_root: str | None, force: bool, python: str | None) -> None:
    """Install the pre-commit, commit-msg and post-commit wrappers."""
    for action in hooks.install(_repo_root(workspace_root), python or sys.executable, force=force):
        click.echo(f"[HOOK: {action}]")


@cli.command(name="uninstall")
@WORKSPACE
@boundary
def uninstall_cmd(workspace_root: str | None) -> None:
    """Remove managed wrappers and restore hooks moved aside by install."""
    actions = hooks.uninstall(_repo_root(workspace_root))
    for action in actions or ["no managed hooks"]:
        click.echo(f"[HOOK: {action}]")


@cli.command(name="status")
@WORKSPACE
@FORMAT_OPTION
@boundary
def status_cmd(workspace_root: str | None, output_format: str) -> None:
    """Show hook wrappers, every known gate with its effective state, the configuration layers and every problem
    that would fail a commit.

    Exits 1 when any problem is reported and 2 when the status cannot be read (not a Git work tree)."""
    project = load_gate_project(_start(workspace_root))
    location = hooks.locate(project.root)
    hook_rows = [
        {
            "stage": item.stage.value,
            "state": item.state.value,
            "python": item.python,
            "python_ok": item.python_ok if item.state is hooks.HookState.MANAGED else None,
            "backup": item.backup,
        }
        for item in hooks.status(project.root, location)
    ]
    gate_rows = [
        {
            "id": gate.id,
            "stage": gate.stage.value,
            "order": gate.order,
            "enabled": project.config.enabled(gate),
            "source": project.registry.sources[gate.id],
            "description": gate.description,
        }
        for gate in project.registry.get_all()
    ]
    sources = [display_path(path, project.root) for path in project.config.sources]
    errors = project.validation.errors
    if is_json(output_format):
        echo_json(
            {
                "hooks_dir": str(location.directory),
                "hooks_path": location.hooks_path,
                "hooks": hook_rows,
                "gates": gate_rows,
                "config_sources": sources,
                "errors": [error.to_dict() for error in errors],
            }
        )
        if errors:
            sys.exit(report_exit_code(errors))
        return
    hooks_path = f" core.hooksPath={location.hooks_path} (wrappers do not run)" if location.hooks_path else ""
    click.echo(f"[HOOKS: dir={display_path(location.directory, project.root)}{hooks_path}]")
    for row in hook_rows:
        extra = f" python={row['python']} python_ok={str(row['python_ok']).lower()}" if row["python"] else ""
        click.echo(f"[HOOK: {row['stage']} state={row['state']}{extra}]")
    for row in gate_rows:
        click.echo(
            f"[GATE: {row['id']} stage={row['stage']} order={row['order']} "
            f"enabled={str(row['enabled']).lower()} source={row['source']}]"
        )
    click.echo(f"[CONFIG: sources={','.join(sources) or 'none'}]")
    for error in errors:
        click.echo(error.render(), err=True)
    if errors:
        sys.exit(report_exit_code(errors))


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
@boundary
def run_cmd(workspace_root: str | None, verbose: bool, stage: str, hook_args: tuple[str, ...]) -> None:
    """Run one stage's gates; this is what the hook wrappers call.

    A blocking stage exits with the highest exit code among its problems: 1 when gates refused the commit,
    2 when the gate setup has a configuration, registry or load problem, a gate failed unexpectedly, or the
    stage cannot run at all (not a Git work tree). post-commit always exits 0."""
    current = Stage(stage)
    try:
        report = run_hook(_start(workspace_root), current, hook_args)
    except Exception as exc:
        if current.blocking:
            raise
        click.echo(as_advisory_error(exc).render(), err=True)  # the commit exists; report only
        return
    _report(report, verbose or os.environ.get(VERBOSE_ENV) == "1")
    if current.blocking and not report.ok:
        sys.exit(int(report.exit_code))
