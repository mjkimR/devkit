"""Agent-first adaptive assignment command adapters."""

from collections.abc import Callable
from typing import Any

import click
from devkit_core.base.usecase import BaseUseCase
from devkit_dist.adapters.cli import (
    FORMAT_OPTION,
    boundary,
    echo_json,
    echo_notices,
    exit_on_warnings,
    field_value,
    is_json,
    resolve_root,
    workspace_option,
)

from devkit_adaptive.features.assignment.models.values import Result
from devkit_adaptive.features.assignment.usecases.closing import CloseAssignmentUseCase
from devkit_adaptive.features.assignment.usecases.creating import NewAssignmentUseCase
from devkit_adaptive.features.assignment.usecases.listing import ListAssignmentsUseCase
from devkit_adaptive.features.assignment.usecases.returning import ReturnAssignmentUseCase
from devkit_adaptive.features.assignment.usecases.showing import ShowAssignmentUseCase
from devkit_adaptive.features.assignment.usecases.verifying import VerifyAssignmentUseCase


def line(kind: str, positional: str | None = None, **fields: Any) -> str:
    prefix = (field_value(positional) + " ") if positional is not None else ""
    return f"[{kind}: {prefix}" + " ".join(f"{key}={field_value(value)}" for key, value in fields.items()) + "]"


def assignment_line(value: dict[str, Any], *, observed: bool = False) -> str:
    if observed:
        observation = value.get("observed") or {}
        return line(
            "ASSIGNMENT",
            value["id"],
            status=value["status"],
            owner=value["owner"],
            role=value["role"],
            parent=value["parent"],
            worktree=value["worktree"],
            worktree_state=observation.get("worktree_state"),
            head=observation.get("head"),
            commits=observation.get("commits"),
            dirty=observation.get("dirty"),
            waiting_on=",".join(observation.get("waiting_on", [])),
            attention=",".join(observation.get("attention", [])),
            assigned_at=value["assigned_at"],
        )
    returned = value["return"] or {}
    close = value["close"] or {}
    return line(
        "ASSIGNMENT",
        value["id"],
        status=value["status"],
        owner=value["owner"],
        role=value["role"],
        parent=value["parent"],
        worktree=value["worktree"],
        base=value["base"],
        final=returned.get("final"),
        outcome=close.get("outcome"),
    )


def _print_verification(result: Result) -> None:
    payload = result.payload
    for name, check in payload["checks"].items():
        click.echo(line("CHECK", name, status=check["status"]))
    for entry in payload["checks"]["scope"]["outside"]:
        click.echo(line("OUT_OF_SCOPE", entry["path"], change=entry["change"]))
    changed = set(payload["changed_paths"]["committed"]) | set(payload["changed_paths"]["uncommitted"])
    click.echo(
        line(
            "VERIFICATION",
            payload["id"],
            result=payload["result"],
            final=payload["final"],
            changed=len(changed),
            out_of_scope=len(payload["checks"]["scope"]["outside"]),
        )
    )
    echo_notices(result.errors)


def _print_list(result: Result) -> None:
    for value in result.payload["assignments"]:
        click.echo(assignment_line(value, observed=True))
    click.echo(line("SUMMARY", **result.payload["summary"]))


def _print_assignment(result: Result) -> None:
    click.echo(assignment_line(result.payload["assignment"]))


def _print_details(result: Result) -> None:
    value = result.payload["assignment"]
    click.echo(assignment_line(value))
    click.echo(line("GRANT", commit=value["commit"]))
    for name in ("goal", "evidence", "handoff", "stop", "return_summary", "close_reason"):
        field = (
            (value["return"] or {}).get("summary")
            if name == "return_summary"
            else (value["close"] or {}).get("reason")
            if name == "close_reason"
            else value.get(name)
        )
        if field is not None:
            click.echo(line("FIELD", name, value=field))
    for name, key in (("WRITE", "write"), ("GOVERNING", "governing"), ("DEPENDS_ON", "depends_on")):
        for item in value[key]:
            click.echo(f"[{name}: {field_value(item)}]")
    for item in (value["return"] or {}).get("unverified", []):
        click.echo(f"[UNVERIFIED: {field_value(item)}]")
    outcomes = {item["name"]: item["outcome"] for item in (value["return"] or {}).get("checks", [])}
    for item in value["checks"]:
        click.echo(line("DECLARED_CHECK", item["name"], command=item["command"], outcome=outcomes.get(item["name"])))
    for item in result.payload["events"]:
        click.echo(line("EVENT", item["event"], at=item["at"]))


def _run(
    use_case: BaseUseCase,
    workspace_root: str | None,
    output_format: str,
    options: dict[str, Any],
    printer: Callable[[Result], None],
    *,
    errors: bool = False,
) -> None:
    """Execute ``use_case`` with the command's options and write its result; ``errors`` reports the result's errors
    in the JSON document (the verification's findings)."""
    result: Result = use_case.execute(
        resolve_root(workspace_root),
        {key: list(value) if isinstance(value, tuple) else value for key, value in options.items()},
    )
    if is_json(output_format):
        echo_json(
            {
                **result.payload,
                **({"errors": [error.to_dict() for error in result.errors]} if errors else {}),
                "notices": [notice.to_dict() for notice in result.notices],
            }
        )
    else:
        printer(result)
    echo_notices(result.notices)
    if result.errors:
        raise SystemExit(1)
    exit_on_warnings(result.notices)


@click.group(name="assignment")
def assignment() -> None:
    """Record assignments and compare returns with their granted authority."""


@assignment.command(name="new")
@click.option("--owner", required=True, help="Who carries out the assignment")
@click.option("--goal", required=True, help="What the assignment must achieve")
@click.option("--id", help="Assignment ID matching ^[a-z0-9][a-z0-9-]{0,39}$; defaults to the first unused a<N>")
@click.option("--role", help="Role the owner takes")
@click.option(
    "--worktree", help="Present worktree of this repository; defaults to the one containing the workspace root"
)
@click.option("--base", help="Commit the assignee starts from; defaults to the worktree HEAD")
@click.option(
    "--write", multiple=True, help="Granted write path relative to the worktree root, repeatable; none is read-only"
)
@click.option("--commit", is_flag=True, help="Grant commits; without it HEAD must stay at the base")
@click.option("--check", multiple=True, help="Declared check <name>[=<command>], repeatable; the command is never run")
@click.option(
    "--governing",
    multiple=True,
    help="Constraining document ID or path, repeatable; the single value none records no document",
)
@click.option("--depends-on", multiple=True, help="ID of an assignment this one is sequenced after, repeatable")
@click.option("--parent", help="ID of an unclosed top-level assignment whose authority this one narrows")
@click.option("--evidence", help="Recorded evidence note for resume; not verified")
@click.option("--handoff", help="Recorded handoff note for resume; not verified")
@click.option("--stop", help="Recorded stop condition for resume; not verified")
@workspace_option()
@FORMAT_OPTION
@boundary
def new_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """Record a new assignment with status open, its grant and its worktree base."""
    _run(NewAssignmentUseCase(), workspace_root, output_format, options, _print_assignment)


@assignment.command(name="return")
@click.argument("id")
@click.option("--status", required=True, help="Return status: completed, needs_input or failed")
@click.option("--final", help="Final commit of the work; defaults to the assignment worktree's HEAD")
@click.option(
    "--check", multiple=True, help="Check outcome <name>=pass|fail|skipped|unavailable, repeatable; reported, never run"
)
@click.option("--unverified", multiple=True, help="Claim the assignee did not verify, repeatable")
@click.option("--summary", help="Summary of what was returned")
@workspace_option()
@FORMAT_OPTION
@boundary
def return_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """Record the assignee's return and set status returned; a later return replaces the current one."""
    _run(ReturnAssignmentUseCase(), workspace_root, output_format, options, _print_assignment)


@assignment.command(name="verify")
@click.argument("id")
@workspace_option()
@FORMAT_OPTION
@boundary
def verify_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """Compare the current return with the repository and set status verified or rejected; exit 1 on fail."""
    _run(VerifyAssignmentUseCase(), workspace_root, output_format, options, _print_verification, errors=True)


@assignment.command(name="close")
@click.argument("id")
@click.option("--outcome", required=True, help="Close outcome: integrated or abandoned")
@click.option("--reason", help="Why; required for abandoned, and for integrated when the status is not verified")
@workspace_option()
@FORMAT_OPTION
@boundary
def close_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """End an assignment with status closed; a parent with an unclosed child is refused."""
    _run(CloseAssignmentUseCase(), workspace_root, output_format, options, _print_assignment)


@assignment.command(name="list")
@click.option("--all", is_flag=True, help="Include closed assignments")
@workspace_option()
@FORMAT_OPTION
@boundary
def list_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """List the unclosed assignments with their observed worktree state; --all adds the closed ones."""
    _run(ListAssignmentsUseCase(), workspace_root, output_format, options, _print_list)


@assignment.command(name="show")
@click.argument("id")
@workspace_option()
@FORMAT_OPTION
@boundary
def show_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """Print one assignment with every recorded field, its current return and its event history."""
    _run(ShowAssignmentUseCase(), workspace_root, output_format, options, _print_details)
