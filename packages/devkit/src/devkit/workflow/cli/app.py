"""The ``devkit workflow`` group and its shared options; the error boundary is ``devkit.core.cli.boundary``.

Under ``--format json`` every command prints exactly one object: ``list``
``{"units"}``, ``checks`` ``{"checks"}``, ``requests`` ``{"requests"}``, the
other commands their result object (collected problems under ``errors``), and
``{"error"}`` when a command fails.
"""

from __future__ import annotations

from datetime import date

import click

from devkit.core.cli import resolve_root, workspace_option
from devkit.core.errors import ArgumentError
from devkit.workflow.workspace import Workspace

WORKSPACE = workspace_option()
UNIT = click.option(
    "--unit", "-u", required=True, type=str, help="Work unit directory (workspace-relative or absolute)"
)
NO_LINT = click.option("--no-lint", is_flag=True, help="Skip lint-class checks")


def workspace(root: str | None) -> Workspace:
    return Workspace(resolve_root(root))


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ArgumentError(f"--date: {exc}", target_files=["--date"], fix="Pass --date YYYY-MM-DD") from exc


@click.group(name="workflow")
def cli() -> None:
    """Data-driven delivery workflow engine for coding agents."""
