"""Agent-first adaptive assignment command adapters."""

from typing import Any

import click
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


def emit(result: Result, output_format: str, verb: str) -> None:
    payload = result.payload
    if is_json(output_format):
        echo_json(
            {
                **payload,
                **({"errors": [error.to_dict() for error in result.errors]} if verb == "verify" else {}),
                "notices": [notice.to_dict() for notice in result.notices],
            }
        )
    elif verb == "verify":
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
    elif verb == "list":
        for value in payload["assignments"]:
            click.echo(assignment_line(value, observed=True))
        click.echo(line("SUMMARY", **payload["summary"]))
    else:
        value = payload["assignment"]
        click.echo(assignment_line(value))
        if verb == "show":
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
                click.echo(
                    line("DECLARED_CHECK", item["name"], command=item["command"], outcome=outcomes.get(item["name"]))
                )
            for item in payload["events"]:
                click.echo(line("EVENT", item["event"], at=item["at"]))
    echo_notices(result.notices)
    if result.errors:
        raise SystemExit(1)
    exit_on_warnings(result.notices)


@click.group(name="assignment")
def assignment() -> None:
    """Record assignments and compare returns with their granted authority."""


@assignment.command(name="new")
@click.option("--owner", required=True)
@click.option("--goal", required=True)
@click.option("--id")
@click.option("--role")
@click.option("--worktree")
@click.option("--base")
@click.option("--write", multiple=True)
@click.option("--commit", is_flag=True)
@click.option("--check", multiple=True)
@click.option("--governing", multiple=True)
@click.option("--depends-on", multiple=True)
@click.option("--parent")
@click.option("--evidence")
@click.option("--handoff")
@click.option("--stop")
@workspace_option()
@FORMAT_OPTION
@boundary
def new_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """New an assignment."""
    result = NewAssignmentUseCase().execute(
        resolve_root(workspace_root),
        {key: list(value) if isinstance(value, tuple) else value for key, value in options.items()},
    )
    emit(result, output_format, "new")


@assignment.command(name="return")
@click.argument("id")
@click.option("--status", required=True)
@click.option("--final")
@click.option("--check", multiple=True)
@click.option("--unverified", multiple=True)
@click.option("--summary")
@workspace_option()
@FORMAT_OPTION
@boundary
def return_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """Return an assignment."""
    result = ReturnAssignmentUseCase().execute(
        resolve_root(workspace_root),
        {key: list(value) if isinstance(value, tuple) else value for key, value in options.items()},
    )
    emit(result, output_format, "return")


@assignment.command(name="verify")
@click.argument("id")
@workspace_option()
@FORMAT_OPTION
@boundary
def verify_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """Verify an assignment."""
    result = VerifyAssignmentUseCase().execute(
        resolve_root(workspace_root),
        {key: list(value) if isinstance(value, tuple) else value for key, value in options.items()},
    )
    emit(result, output_format, "verify")


@assignment.command(name="close")
@click.argument("id")
@click.option("--outcome", required=True)
@click.option("--reason")
@workspace_option()
@FORMAT_OPTION
@boundary
def close_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """Close an assignment."""
    result = CloseAssignmentUseCase().execute(
        resolve_root(workspace_root),
        {key: list(value) if isinstance(value, tuple) else value for key, value in options.items()},
    )
    emit(result, output_format, "close")


@assignment.command(name="list")
@click.option("--all", is_flag=True)
@workspace_option()
@FORMAT_OPTION
@boundary
def list_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """List an assignment."""
    result = ListAssignmentsUseCase().execute(
        resolve_root(workspace_root),
        {key: list(value) if isinstance(value, tuple) else value for key, value in options.items()},
    )
    emit(result, output_format, "list")


@assignment.command(name="show")
@click.argument("id")
@workspace_option()
@FORMAT_OPTION
@boundary
def show_cmd(workspace_root: str | None, output_format: str, **options: Any) -> None:
    """Show an assignment."""
    result = ShowAssignmentUseCase().execute(
        resolve_root(workspace_root),
        {key: list(value) if isinstance(value, tuple) else value for key, value in options.items()},
    )
    emit(result, output_format, "show")
