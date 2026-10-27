"""Prepare and execute scoped integration after Host-carried conversational approval."""

import json
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

import click
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    exit_on_warnings,
    is_json,
    resolve_root,
    workspace_option,
    yes_no,
)

from devkit_agt.features.integration.models.contracts import Task, integrate_command, prepare_command
from devkit_agt.features.integration.usecases.operations import IntegrateUseCase, PrepareIntegrationUseCase
from devkit_agt.features.integration.usecases.service import IntegrationService
from devkit_agt.features.worktree import RunFromBaseError


@contextmanager
def _rerun_on_base(root: Path, command: Callable[[str], str]) -> Iterator[None]:
    """Name the same command for the base checkout's devkit project when it ran in the worktree it would remove
    (``WORKTREE_RUN_FROM_BASE``): ``command(workspace)`` is that command with ``-w workspace``."""
    try:
        yield
    except RunFromBaseError as error:
        if error.base is not None and error.checkout is not None and root.is_relative_to(error.checkout):
            error.fix = command(str(error.base / root.relative_to(error.checkout)))
        raise


@click.group()
def cli() -> None:
    """Prepare and integrate verified work through the Host-authorized CLI boundary."""


@cli.command()
@click.argument("branch")
@click.option(
    "--task-kind",
    required=True,
    type=click.Choice(["unit", "session"]),
    help="Whether the work is a spec unit or a session",
)
@click.option("--task-id", required=True, help="The unit or session id the integration belongs to")
@click.option("--unit", default=None, help="Workspace-relative unit directory; required with --task-kind unit only")
@click.option(
    "--route",
    default="local",
    show_default=True,
    type=click.Choice(["local", "pull-request"]),
    help="Merge locally, or land through a pull request",
)
@click.option(
    "--claims", default="{}", help="Provider-specific caller declarations as JSON; exclude secrets and transcripts"
)
@workspace_option()
@FORMAT_OPTION
@boundary
def prepare(
    branch: str,
    task_kind: str,
    task_id: str,
    unit: str | None,
    route: str,
    claims: str,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Validate committed BRANCH and show its exact integration scope without performing integration effects."""
    root, task = resolve_root(workspace_root), Task(task_kind, task_id, unit, claims)
    with _rerun_on_base(root, lambda workspace: prepare_command(branch, task, route, workspace=workspace)):
        result = PrepareIntegrationUseCase(IntegrationService(root)).execute(branch, task, route)
    if is_json(output_format):
        echo_json(result.compact_dict())
        return
    request = result.request
    plan = request.context.finish
    cleanup = ",".join(scope.extension for scope in request.cleanup) or "-"
    click.echo(
        f"[INTEGRATION_PREPARED: {request.id} branch={plan.branch} target={json.dumps(plan.target_branch)} "
        f"digest={request.digest} route={route} network={request.context.network}]"
    )
    click.echo(
        f"[INTEGRATION_SCOPE: worktree_remove={yes_no(plan.worktree_identity is not None)} "
        f"delete_branch={yes_no(plan.delete_branch)} cleanup={cleanup} "
        f"disclosure={json.dumps(request.readiness.disclosure, ensure_ascii=False)}]"
    )


@cli.command()
@click.argument("branch")
@click.option(
    "--task-kind",
    required=True,
    type=click.Choice(["unit", "session"]),
    help="Whether the work is a spec unit or a session",
)
@click.option("--task-id", required=True, help="The unit or session id the integration belongs to")
@click.option("--unit", default=None, help="Workspace-relative unit directory; required with --task-kind unit only")
@click.option(
    "--route",
    default="local",
    show_default=True,
    type=click.Choice(["local", "pull-request"]),
    help="Merge locally, or land through a pull request",
)
@click.option(
    "--claims", default="{}", help="Provider-specific caller declarations as JSON; exclude secrets and transcripts"
)
@click.option(
    "--expected-digest",
    default=None,
    help="Prepared scope digest presented for approval; required under ask, optional under auto",
)
@workspace_option()
@FORMAT_OPTION
@boundary
def integrate(
    branch: str,
    task_kind: str,
    task_id: str,
    unit: str | None,
    route: str,
    claims: str,
    expected_digest: str | None,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Integrate committed BRANCH after Host-carried approval; auto policy is read from the retained base."""
    root, task = resolve_root(workspace_root), Task(task_kind, task_id, unit, claims)
    with _rerun_on_base(
        root, lambda workspace: integrate_command(branch, task, route, expected_digest, workspace=workspace)
    ):
        result = IntegrateUseCase(IntegrationService(root)).execute(
            branch, task, route, expected_digest=expected_digest
        )
    payload = result.compact_dict()
    if is_json(output_format):
        echo_json(payload)
    else:
        plan = result.request.context.finish
        effects = ",".join(f"{step}:{state}" for step, state in result.steps.items())
        click.echo(
            f"[INTEGRATION: status={result.status} branch={plan.branch} target={json.dumps(plan.target_branch)} "
            f"route={route} authority={result.authority or '-'} failed={result.failing_operation or '-'} "
            f"codes={','.join(error.code for error in result.errors) or '-'} effects={effects}]"
        )
        echo_notices(result.notices)
        for error in result.errors:  # errors last, so the decisive block ends the output
            click.echo(error.render(), err=True)
    # 2 when nothing happened, 1 when an error stopped it part way; --strict only ever raises 0 to 1. A partial run
    # whose only advisory is a warning (Git integration done, scoped cleanup remains) succeeded.
    if result.status == "blocked" and not any(state == "completed" for state in result.steps.values()):
        raise click.exceptions.Exit(2)
    if result.errors:
        raise click.exceptions.Exit(1)
    exit_on_warnings(result.notices)
