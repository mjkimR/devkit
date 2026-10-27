"""The ``devkit workflow`` group and its shared options; the error boundary is ``devkit_dist.adapters.cli.boundary``.

Under ``--format json`` every command prints exactly one object: ``list``
``{"units"}``, ``checks`` ``{"checks"}``, ``next --view requests``
``{"requests", "errors"}``, the
other commands their result object (collected problems under ``errors``), and
``{"error"}`` when a command fails.
"""

from __future__ import annotations

from datetime import date

import click
from devkit_core.base.errors import ArgumentError
from devkit_dist.adapters.cli import resolve_root, workspace_option

from devkit_agt.features.workflow.usecases.workspace import Workspace

WORKSPACE = workspace_option()
UNIT = click.option(
    "--unit", "-u", required=True, type=str, help="Work unit directory (workspace-relative or absolute)"
)
ANCHOR = click.option(
    "--anchor",
    "anchor",
    default=None,
    type=str,
    help="Anchor file that identifies the unit, when its directory holds several (ANCHOR_AMBIGUOUS)",
)
NO_LINT = click.option("--no-lint", is_flag=True, help="Skip lint-class checks")


# ``Context.meta`` key of the arguments the ``workflow`` group was invoked with (``_WorkflowGroup``).
INVOCATION = "devkit_agt.workflow.invocation"


class _WorkflowGroup(click.Group):
    """Records the arguments after ``workflow``, so an error can name the exact command to rerun."""

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        ctx.meta[INVOCATION] = tuple(args)
        return super().parse_args(ctx, args)


def workspace(root: str | None) -> Workspace:
    ctx = click.get_current_context(silent=True)
    invocation = ctx.meta.get(INVOCATION) if ctx is not None else None
    return Workspace(resolve_root(root), invocation=invocation)


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ArgumentError(f"--date: {exc}", target_files=["--date"], fix="Pass --date YYYY-MM-DD") from exc


@click.group(name="workflow", cls=_WorkflowGroup)
def cli() -> None:
    """Data-driven delivery workflow engine for coding agents."""
