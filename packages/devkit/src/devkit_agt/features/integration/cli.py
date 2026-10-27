"""Prepare and execute scoped integration after Host-carried conversational approval."""

import json

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
)

from devkit_agt.features.integration.models.contracts import Task
from devkit_agt.features.integration.usecases.operations import IntegrateUseCase, PrepareIntegrationUseCase
from devkit_agt.features.integration.usecases.service import IntegrationService


def _yes(value: bool) -> str:
    return "yes" if value else "no"


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
    result = PrepareIntegrationUseCase(IntegrationService(resolve_root(workspace_root))).execute(
        branch, Task(task_kind, task_id, unit, claims), route
    )
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
        f"[INTEGRATION_SCOPE: worktree_remove={_yes(plan.worktree_identity is not None)} "
        f"delete_branch={_yes(plan.delete_branch)} cleanup={cleanup} "
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
    result = IntegrateUseCase(IntegrationService(resolve_root(workspace_root))).execute(
        branch, Task(task_kind, task_id, unit, claims), route, expected_digest=expected_digest
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
