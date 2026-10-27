"""``new``, ``bind``, ``list`` and ``show``."""

from __future__ import annotations

import sys

import click
from devkit_core.base.errors import ArgumentError
from devkit_dist.adapters.cli import FORMAT_OPTION, boundary, echo_json, field_value, is_json, report_exit_code

from devkit_agt.features.workflow.cli.app import ANCHOR, UNIT, WORKSPACE, cli, parse_date, workspace
from devkit_agt.features.workflow.cli.render import quote, render_document
from devkit_agt.features.workflow.usecases.operations import BindUnitUseCase, DescribeWorkflowUseCase
from devkit_agt.features.workflow.usecases.units import CreateUnitUseCase, ListUnitsUseCase


@cli.command(name="new", hidden=True)
@WORKSPACE
@click.argument("slug", type=str)
@click.option(
    "--workflow", "workflow_ref", default=None, help="Workflow id or definition path (default: [workflow].default)"
)
@click.option("--date", "when", default=None, help="Date used by the layout template, YYYY-MM-DD (default: today)")
@click.option("--status", default="planned", show_default=True, help="Initial anchor status")
@boundary
def new_cmd(workspace_root: str | None, slug: str, workflow_ref: str | None, when: str | None, status: str) -> None:
    """Create a work unit from the layout template and bind it to a workflow."""
    ws = workspace(workspace_root)
    unit = CreateUnitUseCase().execute(ws, slug, workflow=workflow_ref, when=parse_date(when), status=status)
    click.echo(f"[UNIT: {unit.rel} workflow={unit.doc.id} anchor={unit.anchor}]")


@cli.command(name="bind", hidden=True)
@WORKSPACE
@UNIT
@ANCHOR
@click.option(
    "--workflow",
    "workflow_ref",
    default=None,
    help="Workflow id or definition path (default: current binding or [workflow].default)",
)
@boundary
def bind_cmd(workspace_root: str | None, unit: str, anchor: str | None, workflow_ref: str | None) -> None:
    """Record which workflow a unit follows."""
    ws = workspace(workspace_root)
    ref = BindUnitUseCase(ws).execute(unit, workflow_ref, anchor=anchor)
    click.echo(f"[BOUND: {ref.doc.id}]")


@cli.command(name="show")
@WORKSPACE
@click.argument("ref", type=str, required=False)
@click.option("--unit", "-u", "unit", default=None, help="Show the workflow this unit is bound to instead of REF")
@ANCHOR
@FORMAT_OPTION
@boundary
def show_cmd(
    workspace_root: str | None, ref: str | None, unit: str | None, anchor: str | None, output_format: str
) -> None:
    """Print a workflow definition's stages and gates (by id/path, or a unit's binding).

    Exits 1 when the report lists problems (under "errors" in JSON), whatever their own codes.
    """
    if (ref is None) == (unit is None):
        raise ArgumentError(
            "pass exactly one of REF or --unit",
            target_files=["REF", "--unit"],
            fix="Pass either a workflow id or definition path, or --unit with a unit directory, not both",
        )
    if anchor is not None and unit is None:
        raise ArgumentError(
            "--anchor applies only with --unit",
            target_files=["--anchor"],
            fix="Drop --anchor, or pass --unit with the unit directory instead of REF",
        )
    ws = workspace(workspace_root)
    description = DescribeWorkflowUseCase(ws).execute(ref, unit=unit, anchor=anchor)
    doc, binding = description.doc, description.binding
    if is_json(output_format):
        echo_json(description.to_dict())
    else:
        click.echo(render_document(doc, ws.config.approvals, ws.config.stages), nl=False)
        if binding is not None:
            click.echo(f"[BINDING: workflow={binding.workflow or '-'}]")
        for problem in description.errors:
            click.echo(f"[PROBLEM: {problem}]")
    if not description.ok:
        sys.exit(report_exit_code(description.errors))


@cli.command(name="list")
@WORKSPACE
@click.option("--status", "statuses", multiple=True, help="Keep units whose anchor status equals this (repeatable)")
@click.option(
    "--exclude-status", "excluded", multiple=True, help="Drop units whose anchor status equals this (repeatable)"
)
@FORMAT_OPTION
@boundary
def list_cmd(
    workspace_root: str | None, statuses: tuple[str, ...], excluded: tuple[str, ...], output_format: str
) -> None:
    """List discovered work units with their status and binding, across every layout in use."""
    ws = workspace(workspace_root)
    listing = ListUnitsUseCase().execute(ws, statuses=statuses, excluded=excluded)
    rows = listing.units
    if is_json(output_format):
        errors = [row.error.to_dict() for row in rows if row.error is not None]
        echo_json({"units": [row.to_dict() for row in rows], "errors": errors})
        return
    if not rows:
        click.echo(f"[OK: no units dirs={field_value(','.join(listing.directories))}]")
        return
    for row in rows:
        # The first line names the problem; the parser's full report is in JSON, and `next --unit` raises it.
        error = f" error={quote(row.error.message.splitlines()[0])}" if row.error is not None else ""
        click.echo(
            f"[UNIT: {row.unit} status={row.status or '-'} workflow={row.binding.workflow or '-'} anchor={row.anchor}{error}]"
        )
