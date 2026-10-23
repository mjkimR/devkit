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


@click.group()
def cli() -> None:
    """Prepare and integrate verified work through the Host-authorized CLI boundary."""


@cli.command()
@click.argument("branch")
@click.option("--task-kind", required=True, type=click.Choice(["unit", "session"]))
@click.option("--task-id", required=True)
@click.option("--unit", default=None)
@click.option("--route", default="local", type=click.Choice(["local", "pull-request"]))
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
        echo_json(result.to_dict())
    else:
        plan = result.request.context.finish
        click.echo(
            f"[INTEGRATION_PREPARED: {result.request.id} branch={plan.branch} target={json.dumps(plan.target_branch)} digest={result.request.digest} route={route} network={result.request.context.network}]"
        )


@cli.command()
@click.argument("branch")
@click.option("--task-kind", required=True, type=click.Choice(["unit", "session"]))
@click.option("--task-id", required=True)
@click.option("--unit", default=None)
@click.option("--route", default="local", type=click.Choice(["local", "pull-request"]))
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
        click.echo(
            f"[INTEGRATION: status={result.status} branch={plan.branch} target={json.dumps(plan.target_branch)} "
            f"route={route} authority={result.authority or '-'} failed={result.failing_operation or '-'} "
            f"codes={','.join(error.code for error in result.errors) or '-'} effects={json.dumps(result.steps, sort_keys=True)}]"
        )
        echo_notices([*result.errors, *result.notices])
    exit_on_warnings(result.notices)
    if result.status == "blocked" and not any(state == "completed" for state in result.steps.values()):
        raise click.exceptions.Exit(2)
    if result.errors or result.status == "partial":
        raise click.exceptions.Exit(1)
