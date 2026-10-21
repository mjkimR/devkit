"""``devkit gate`` commands: install and uninstall the hook wrappers, report the setup, run a stage.

A thin command line over the library: ``status`` renders
``devkit_agt.features.gate.load_gate_project`` and ``run`` renders ``RunHookUseCase.execute``.
Every command works on the top level of the Git work tree containing
``--workspace-root`` (default: the current directory), resolved with
``devkit_dist.features.project.repositories.project.require_git_toplevel``. ``status --format json`` prints one
object (``{"hooks_dir", "hooks_path", "hooks", "gates", "config_sources",
"errors", "notices"}``) or ``{"error"}``. ``status`` is a report: it exits 1 when it lists
any problem that would fail a commit and 2 only when it cannot run; its warnings
(``GATE_HOOK_ENTRY_MISSING``, ``GATE_HOOKS_PATH_SET``) change the exit code only under ``--strict``. A blocking
``run`` exits with the highest ``exit_code`` among the problems it reports.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from devkit.advisory import AdvisoryError, Level, as_advisory_error
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    existing_directory,
    exit_on_warnings,
    is_json,
    report_exit_code,
    workspace_option,
)
from devkit_dist.features.project.usecases.workspace import require_git_toplevel

import devkit_agt.features.gate.usecases.hooks.hooks as hooks
import devkit_agt.features.gate.usecases.hooks.local_config as local_config
from devkit_agt.features.gate.models.contracts import Outcome, Stage
from devkit_agt.features.gate.models.paths import display_path
from devkit_agt.features.gate.usecases.runner import RunHookUseCase, StageReport
from devkit_agt.features.gate.usecases.status import GateStatusUseCase

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
    help=f"Also preserve symbolic links and non-regular hooks at <hook>{hooks.BACKUP_SUFFIX}",
)
@click.option(
    "--python",
    "python",
    default=None,
    help="Fallback interpreter the wrappers exec when the work tree's .venv has no devkit (default: this one)",
)
@boundary
def install_cmd(workspace_root: str | None, force: bool, python: str | None) -> None:
    """Install the pre-commit, commit-msg and post-commit wrappers, and the commented settings template.

    The template in <common-git-dir>/devkit.config gets a commented table for every installed gate it does not
    mention yet; existing lines are never changed.
    """
    root = _repo_root(workspace_root)
    installed = hooks.InstallHooksUseCase().execute(root, python or sys.executable, force=force)
    for action in installed.actions:
        click.echo(f"[HOOK: {action}]")
    template = local_config.RefreshGateTemplateUseCase().execute(root)
    click.echo(f"[CONFIG: template={template.state} path={template.path}]")
    notices = installed.notices + ([template.notice] if template.notice is not None else [])
    echo_notices(notices)
    exit_on_warnings(notices)


@cli.command(name="uninstall")
@WORKSPACE
@boundary
def uninstall_cmd(workspace_root: str | None) -> None:
    """Remove managed wrappers and restore hooks moved aside by install."""
    actions = hooks.UninstallHooksUseCase().execute(_repo_root(workspace_root))
    for action in actions or ["no managed hooks"]:
        click.echo(f"[HOOK: {action}]")


@cli.command(name="status")
@WORKSPACE
@FORMAT_OPTION
@boundary
def status_cmd(workspace_root: str | None, output_format: str) -> None:
    """Show hook wrappers, every known gate with its effective state, the configuration layers and every problem
    that would fail a commit.

    Warns (GATE_HOOK_ENTRY_MISSING) about enabled gates whose stage has no installed hook entry, so they do not run;
    when core.hooksPath sends Git to another hooks directory, warns once (GATE_HOOKS_PATH_SET) instead, naming every
    enabled gate. Exits 1 when any problem is reported and 2 when the status cannot be read (not a Git work tree)."""
    result = GateStatusUseCase().execute(_start(workspace_root))
    project, location, statuses = result.project, result.location, result.hooks
    hook_rows = [
        {
            "stage": item.stage.value,
            "state": item.state.value,
            "python": item.python,
            "python_ok": item.python_ok if item.python is not None else None,
            "backup": item.backup,
            "scripts": list(item.scripts),
        }
        for item in statuses
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
    notices = result.notices
    if is_json(output_format):
        echo_json(
            {
                "hooks_dir": str(location.directory),
                "hooks_path": location.hooks_path,
                "hooks": hook_rows,
                "gates": gate_rows,
                "config_sources": sources,
                "errors": [error.to_dict() for error in errors],
                "notices": [notice.to_dict() for notice in notices],
            }
        )
        if errors:
            sys.exit(report_exit_code(errors))
        exit_on_warnings(notices)
        return
    hooks_path = f" core.hooksPath={location.hooks_path} (wrappers do not run)" if location.hooks_path else ""
    click.echo(f"[HOOKS: dir={display_path(location.directory, project.root)}{hooks_path}]")
    for row in hook_rows:
        extra = f" python={row['python']} python_ok={str(row['python_ok']).lower()}" if row["python"] else ""
        click.echo(f"[HOOK: {row['stage']} state={row['state']}{extra} scripts={','.join(row['scripts']) or 'none'}]")
    for row in gate_rows:
        click.echo(
            f"[GATE: {row['id']} stage={row['stage']} order={row['order']} "
            f"enabled={str(row['enabled']).lower()} source={row['source']}]"
        )
    click.echo(f"[CONFIG: sources={','.join(sources) or 'none'}]")
    echo_notices(notices)  # before the problems, so errors are last
    for error in errors:
        click.echo(error.render(), err=True)
    if errors:
        sys.exit(report_exit_code(errors))
    exit_on_warnings(notices)


def _block(error: AdvisoryError, level: Level | None, *first_details: str) -> str:
    """``error`` rendered at ``level`` (as raised when ``None``), ``first_details`` leading its ``[DETAIL]`` lines.

    A failed gate's own details can be long (one per violation), so the line
    naming the gate comes before them rather than at the end of the block.
    """
    shown = error.with_level(level) if level is not None else error
    lines = shown.lines()
    at = next((i for i, line in enumerate(lines) if line.startswith("[DETAIL] ")), len(lines))
    return "\n".join([*lines[:at], *(f"[DETAIL] {detail}" for detail in first_details), *lines[at:]])


def _report(report: StageReport) -> None:
    """Render the stage's problems (setup problems, then one block per failed gate, naming it first) and its notices.

    A blocking stage refused or could not check the commit: its notices come
    first and its problems last, as errors. After ``post-commit`` the commit
    exists, so its problems are warnings (``CONTINUE``), printed before the notices.
    """
    level = None if report.stage.blocking else Level.WARNING
    blocks = [_block(error, level) for error in report.errors]
    blocks += [
        _block(run.error, level, f"gate={run.gate_id} stage={report.stage}")
        for run in report.runs
        if run.outcome is Outcome.FAILED and run.error is not None
    ]
    if level is None:
        echo_notices(report.notices)
    for block in blocks:
        click.echo(block, err=True)
    if level is not None:
        echo_notices(report.notices)


@cli.command(name="run", hidden=True, context_settings={"ignore_unknown_options": True})
@WORKSPACE
@click.argument("stage", type=click.Choice([stage.value for stage in Stage]))
@click.argument("hook_args", nargs=-1, type=click.UNPROCESSED)
@boundary
def run_cmd(workspace_root: str | None, stage: str, hook_args: tuple[str, ...]) -> None:
    """Run one stage's gates; this is what the hook wrappers call.

    Prints nothing on stdout. A blocking stage exits with the highest exit code among its problems: 1 when
    gates refused the commit, 2 when the gate setup has a configuration, registry or load problem, a gate
    failed unexpectedly, or the stage cannot run at all (not a Git work tree). post-commit always exits 0
    and reports its problems as warnings: the commit already exists.
    Options go before STAGE; hooks set DEVKIT_QUIET, DEVKIT_VERBOSE or DEVKIT_STRICT instead."""
    current = Stage(stage)
    try:
        report = RunHookUseCase().execute(_start(workspace_root), current, hook_args)
    except Exception as exc:
        if current.blocking:
            raise
        click.echo(_block(as_advisory_error(exc), Level.WARNING), err=True)  # the commit exists; report only
        return
    _report(report)
    if current.blocking and not report.ok:
        sys.exit(int(report.exit_code))
    if current.blocking:
        exit_on_warnings(report.notices)
