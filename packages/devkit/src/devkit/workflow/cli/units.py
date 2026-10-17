"""``new``, ``bind``, ``list`` and ``show``."""

from __future__ import annotations

import sys

import click

from devkit.core.cli import FORMAT_OPTION, boundary, echo_json, is_json, report_exit_code
from devkit.core.errors import ArgumentError
from devkit.workflow.cli.app import ANCHOR, UNIT, WORKSPACE, cli, parse_date, workspace
from devkit.workflow.render import quote, render_document
from devkit.workflow.unit.units import create_unit, layouts_in_use, list_units


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
    ref = ws.bind_unit(unit, workflow_ref, anchor=anchor)
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
            fix="Run `devkit workflow show <id|path>` or `devkit workflow show --unit <dir>`",
        )
    if anchor is not None and unit is None:
        raise ArgumentError(
            "--anchor applies only with --unit",
            target_files=["--anchor"],
            fix="Drop --anchor, or run `devkit workflow show --unit <dir> --anchor <file>`",
        )
    ws = workspace(workspace_root)
    if unit is not None:
        description = ws.describe_unit(unit, anchor=anchor)
    else:
        assert ref is not None
        description = ws.describe(ws.load_definition(ref))
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
    rows = list_units(ws, statuses=statuses, excluded=excluded)
    if is_json(output_format):
        echo_json({"units": [row.to_dict() for row in rows]})
        return
    if not rows:
        dirs = ", ".join(dict.fromkeys(layout.work_dir for layout in layouts_in_use(ws)))
        click.echo(f"[UNITS: none under {dirs}]")
        return
    for row in rows:
        error = f" error={quote(row.error.message)}" if row.error is not None else ""
        click.echo(
            f"[UNIT: {row.unit} status={row.status or '-'} workflow={row.binding.workflow or '-'} anchor={row.anchor}{error}]"
        )
