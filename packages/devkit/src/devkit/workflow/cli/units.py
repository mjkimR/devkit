"""``new``, ``bind``, ``list`` and ``show``."""

from __future__ import annotations

import sys

import click

from devkit.advisory import ExitCode
from devkit.workflow.binding import Binding, write_binding
from devkit.workflow.cli.app import (
    FORMAT,
    UNIT,
    WORKSPACE,
    boundary,
    cli,
    echo_json,
    is_json,
    parse_date,
    workspace,
)
from devkit.workflow.definition import schema_hash
from devkit.workflow.errors import input_error
from devkit.workflow.render import quote, render_document
from devkit.workflow.units import create_unit, layouts_in_use, list_units


@cli.command(name="new")
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
    unit = create_unit(ws, slug, workflow=workflow_ref, when=parse_date(when), status=status)
    click.echo(f"[UNIT: {unit.rel} workflow={unit.doc.id} anchor={unit.anchor}]")


@cli.command(name="bind")
@WORKSPACE
@UNIT
@click.option(
    "--workflow",
    "workflow_ref",
    default=None,
    help="Workflow id or definition path (default: current binding or [workflow].default)",
)
@boundary
def bind_cmd(workspace_root: str | None, unit: str, workflow_ref: str | None) -> None:
    """Record which workflow a unit follows and the hash of its stage schema."""
    ws = workspace(workspace_root)
    ref = ws.resolve_unit(unit, workflow_ref)
    binding = Binding(ref.doc.id, schema_hash(ref.doc))
    write_binding(ref.anchor_path, binding)
    click.echo(f"[BOUND: {ref.doc.id} hash={binding.hash}]")


@cli.command(name="show")
@WORKSPACE
@click.argument("ref", type=str, required=False)
@click.option("--unit", "-u", "unit", default=None, help="Show the workflow this unit is bound to instead of REF")
@FORMAT
@boundary
def show_cmd(workspace_root: str | None, ref: str | None, unit: str | None, output_format: str) -> None:
    """Print a workflow definition's stages, gates and schema hash (by id/path, or a unit's binding)."""
    ws = workspace(workspace_root)
    if (ref is None) == (unit is None):
        raise input_error(
            "pass exactly one of REF or --unit",
            code="WORKFLOW_NOT_SELECTED",
            fix="Run `devkit workflow show <id|path>` or `devkit workflow show --unit <dir>`",
        )
    binding: Binding | None = None
    if unit is not None:
        unit_ref = ws.resolve_unit(unit)
        doc, binding = unit_ref.doc, unit_ref.binding
    else:
        assert ref is not None
        doc = ws.load_definition(ref)
    data = ws.describe(doc, binding)
    problems: list[dict[str, str]] = data["problems"]
    if is_json(output_format):
        echo_json(data)
    else:
        click.echo(render_document(doc, ws.config.approvals, ws.config.stages), nl=False)
        if binding is not None:
            drift = str(data["binding"]["drift"]).lower()
            click.echo(f"[BINDING: workflow={binding.workflow or '-'} hash={binding.hash or '-'} drift={drift}]")
        for p in problems:
            click.secho(f"[PROBLEM: {p['where']}: {p['message']}]", fg="red")
    if problems:
        sys.exit(int(ExitCode.FINDINGS))


@cli.command(name="list")
@WORKSPACE
@click.option("--status", "statuses", multiple=True, help="Keep units whose anchor status equals this (repeatable)")
@click.option(
    "--exclude-status", "excluded", multiple=True, help="Drop units whose anchor status equals this (repeatable)"
)
@FORMAT
@boundary
def list_cmd(
    workspace_root: str | None, statuses: tuple[str, ...], excluded: tuple[str, ...], output_format: str
) -> None:
    """List discovered work units with their status and binding, across every layout in use."""
    ws = workspace(workspace_root)
    rows = list_units(ws, statuses=statuses, excluded=excluded)
    if is_json(output_format):
        echo_json([row.to_dict() for row in rows])
        return
    if not rows:
        dirs = ", ".join(dict.fromkeys(layout.work_dir for layout in layouts_in_use(ws)))
        click.echo(f"[UNITS: none under {dirs}]")
        return
    for row in rows:
        error = f" error={quote(row.error)}" if row.error else ""
        click.echo(
            f"[UNIT: {row.unit} status={row.status or '-'} workflow={row.binding.workflow or '-'} anchor={row.anchor}{error}]"
        )
