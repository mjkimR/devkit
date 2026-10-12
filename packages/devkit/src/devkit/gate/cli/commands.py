from __future__ import annotations

import functools
import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click

from devkit.advisory import AdvisoryError, ExitCode, as_advisory_error
from devkit.gate import git, hooks
from devkit.gate.config import GatesConfig, load_gates_config
from devkit.gate.models import GateConfigError, GateContext, Outcome, Stage
from devkit.gate.registry import GateRegistry, project_registry
from devkit.gate.runner import StageReport, Validation, run_stage, validate

VERBOSE_ENV = "DEVKIT_GATES_VERBOSE"

WORKSPACE = click.option(
    "--workspace-root",
    "-w",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Any directory inside the repository (gates always run for the work tree's top level)",
)
FORMAT = click.option(
    "--format", "output_format", type=click.Choice(["text", "json"]), default="text", help="Output format"
)


def _boundary(fn: Callable[..., None]) -> Callable[..., None]:
    """Render any error as an advisory on stderr (and as ``{"error": ...}`` on stdout under --format json).

    The process exits with the error's ``exit_code``: ``2`` (``ERROR``) unless the error says otherwise.
    """

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            fn(*args, **kwargs)
        except (click.exceptions.Exit, click.ClickException, SystemExit):
            raise
        except Exception as exc:
            error = as_advisory_error(exc)
            if kwargs.get("output_format") == "json":
                click.echo(json.dumps({"error": error.to_dict()}))
            click.echo(error.render(), err=True)
            sys.exit(int(error.exit_code))

    return wrapper


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)


@dataclass(frozen=True)
class _Project:
    """Everything ``status`` and ``run`` read: the repository, its gates and their validated configuration."""

    root: Path
    git_dir: Path
    common_git_dir: Path
    registry: GateRegistry
    config: GatesConfig
    validation: Validation  # includes a configuration file that cannot be loaded


def _load(workspace_root: str) -> _Project:
    cwd = Path(workspace_root)
    root = git.repo_root(cwd)
    common = git.common_git_dir(root)
    registry = project_registry(root)
    load_errors: list[AdvisoryError] = []
    try:
        config = load_gates_config(root, common)
    except GateConfigError as exc:
        config = GatesConfig()
        load_errors.append(exc)
    checked = validate(registry, config)
    validation = Validation(checked.settings, (*load_errors, *checked.errors))
    return _Project(root, git.git_dir(root), common, registry, config, validation)


@click.group(name="gate")
@click.version_option(package_name="devkit")
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
@_boundary
def install_cmd(workspace_root: str, force: bool, python: str | None) -> None:
    """Install the pre-commit, commit-msg and post-commit wrappers."""
    for action in hooks.install(Path(workspace_root), python or sys.executable, force=force):
        click.echo(f"[HOOK: {action}]")


@cli.command(name="uninstall")
@WORKSPACE
@_boundary
def uninstall_cmd(workspace_root: str) -> None:
    """Remove managed wrappers and restore hooks moved aside by install."""
    actions = hooks.uninstall(Path(workspace_root))
    for action in actions or ["no managed hooks"]:
        click.echo(f"[HOOK: {action}]")


@cli.command(name="status")
@WORKSPACE
@FORMAT
@_boundary
def status_cmd(workspace_root: str, output_format: str) -> None:
    """Show hook wrappers, every known gate with its effective state, the configuration layers and every problem
    that would fail a commit.

    Exits 1 when any such problem is reported, 2 when the status cannot be read (not a Git work tree)."""
    project = _load(workspace_root)
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
    sources = [_rel(path, project.root) for path in project.config.sources]
    errors = project.validation.errors
    if output_format == "json":
        click.echo(
            json.dumps(
                {
                    "hooks_dir": str(location.directory),
                    "hooks_path": location.hooks_path,
                    "hooks": hook_rows,
                    "gates": gate_rows,
                    "config_sources": sources,
                    "errors": [error.to_dict() for error in errors],
                }
            )
        )
        if errors:
            sys.exit(int(ExitCode.FINDINGS))
        return
    hooks_path = f" core.hooksPath={location.hooks_path} (wrappers do not run)" if location.hooks_path else ""
    click.echo(f"[HOOKS: dir={_rel(location.directory, project.root)}{hooks_path}]")
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
        sys.exit(int(ExitCode.FINDINGS))


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
    """Run one stage's gates; this is what the hook wrappers call.

    A blocking stage exits 1 when a gate refused the commit or the gate setup has problems, and 2 when the
    stage cannot run at all (not a Git work tree, an unexpected error). post-commit always exits 0."""
    current = Stage(stage)
    try:
        project = _load(workspace_root)
        report = run_stage(
            GateContext(
                repo_root=project.root,
                git_dir=project.git_dir,
                common_git_dir=project.common_git_dir,
                stage=current,
                args=hook_args,
            ),
            project.registry,
            project.config,
            project.validation,
        )
    except Exception as exc:
        if current.blocking:
            raise
        click.echo(as_advisory_error(exc).render(), err=True)  # the commit exists; report only
        return
    _report(report, verbose or os.environ.get(VERBOSE_ENV) == "1")
    if report.failed and current.blocking:
        sys.exit(int(ExitCode.FINDINGS))
