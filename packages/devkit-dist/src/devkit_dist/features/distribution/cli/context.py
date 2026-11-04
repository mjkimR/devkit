"""Distribution context CLI adapters."""

from __future__ import annotations

from pathlib import Path

import click

from devkit_dist.adapters.cli import boundary, echo_json, echo_notices, exit_on_warnings, resolve_root
from devkit_dist.features.distribution.usecases.context import GetContext

from .output import WORKSPACE

FOR_HELP = (
    "An existing directory inside the project the context is for; the installed providers select its context "
    "documents [default: the current directory, or the workspace root when the current directory is outside it]"
)


def _default_working(root: Path) -> Path:
    """The current directory when it lies inside the resolved ``root``, else ``root``."""
    cwd = Path.cwd()
    try:
        current, base = cwd.resolve(), root.resolve()
    except (RuntimeError, OSError):
        return root
    return cwd if current == base or base in current.parents else root


@click.command(name="get-context")
@click.argument("bundle_name")
@click.option("--for", "working", type=click.Path(path_type=Path), default=None, help=FOR_HELP)
@WORKSPACE
@boundary(json_only=True)
def context(bundle_name: str, working: Path | None, workspace_root: str | None) -> None:
    """Return the full constitution, instruction headers and context documents for a synced bundle.

    stdout is one JSON object; a provider warning is listed under its ``notices`` and exits 1 under ``--strict``.
    """
    root = resolve_root(workspace_root)
    result = GetContext().execute(root, bundle_name, working if working is not None else _default_working(root))
    echo_json(result.to_dict())
    echo_notices(result.notices)
    exit_on_warnings(result.notices)
