"""Read-only integration preparation. Execution authority is supplied only by the native MCP confirmation path."""

import json

import click
from devkit_dist.adapters.cli import FORMAT_OPTION, boundary, echo_json, is_json, resolve_root, workspace_option

from devkit_agt.features.integration.models.contracts import Task
from devkit_agt.features.integration.usecases.service import IntegrationService


@click.group(hidden=True)
def cli() -> None:
    """Scoped local integration: inspect readiness and exact approval requests."""


@cli.command()
@click.argument("branch")
@click.option("--task-kind", required=True, type=click.Choice(["unit", "session"]))
@click.option("--task-id", required=True)
@click.option("--unit", default=None)
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
    claims: str,
    workspace_root: str | None,
    output_format: str,
) -> None:
    """Validate committed BRANCH and prepare its exact local request; approval and execution use MCP."""
    result = IntegrationService(resolve_root(workspace_root)).prepare(branch, Task(task_kind, task_id, unit, claims))
    if is_json(output_format):
        echo_json(result.to_dict())
    else:
        plan = result.request.context.finish
        click.echo(
            f"[INTEGRATION_PREPARED: {result.request.id} branch={plan.branch} target={json.dumps(plan.target_branch)} digest={result.request.digest} network=excluded]"
        )
