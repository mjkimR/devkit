"""Command-line plumbing shared by every ``devkit`` command group: the ``devkit_cli`` toolkit configured for devkit.

The agent-first output contract (``docs/architecture/ARCH-08-1-agent-output.md``) is implemented once, in
``devkit_cli``; this module binds it to devkit and adds what only devkit's commands share:

- ``BOUNDARY`` (``boundary``): ``devkit_cli.Boundary`` with the ``devkit`` logger hierarchy and the ``DEVKIT_``
  environment prefix, so ``-q/--quiet``, ``-v/--verbose`` and ``--strict`` read ``DEVKIT_QUIET``,
  ``DEVKIT_VERBOSE`` and ``DEVKIT_STRICT`` and ``-v`` prints every ``devkit`` log record as an ``[INFO]`` line;
- the output helpers of ``devkit_cli`` (``FORMAT_OPTION``, ``echo_json``, ``echo_notices``, ``exit_on_warnings``,
  ``exit_on_problems``, ``report_exit_code``, ``Reported``, ...), re-exported so command modules import one module;
- ``workspace_option`` (``-w/--workspace-root``) and ``resolve_root``: the explicit workspace root, else the devkit
  root found from the current directory (``devkit_dist.features.project.repositories.project``).

click only parses syntax here: every semantic argument check raises ``ArgumentError`` (``ARGUMENT_INVALID``)
through the boundary, so a JSON caller still receives one document.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import click
from devkit_cli import (
    FORMAT_OPTION,
    Boundary,
    OutputSettings,
    Reported,
    echo_json,
    echo_notices,
    exit_on_problems,
    exit_on_warnings,
    highest_exit_code,
    is_json,
    output_settings,
    report_exit_code,
)
from devkit_core.base.errors import ArgumentError
from devkit_core.core.logs import ROOT, get_logger

from devkit_dist.features.project.usecases.workspace import find_project_root, require_devkit_root

__all__ = [
    "BOUNDARY",
    "FORMAT_OPTION",
    "LOGGER",
    "QUIET_ENV",
    "STRICT_ENV",
    "VERBOSE_ENV",
    "WORKSPACE_HELP",
    "OutputSettings",
    "Reported",
    "boundary",
    "echo_json",
    "echo_notices",
    "existing_directory",
    "exit_on_problems",
    "exit_on_warnings",
    "highest_exit_code",
    "is_json",
    "output_options",
    "output_settings",
    "report_exit_code",
    "resolve_output",
    "resolve_root",
    "workspace_option",
]

LOGGER = ROOT
# The traceback of an unexpected error is logged here, so -v shows it as "[INFO]   devkit_dist.adapters.cli: ...".
BOUNDARY = Boundary(LOGGER, log=get_logger(__name__))
boundary = BOUNDARY
output_options = BOUNDARY.output_options
resolve_output = BOUNDARY.resolve_output

QUIET_ENV = BOUNDARY.quiet_env
VERBOSE_ENV = BOUNDARY.verbose_env
STRICT_ENV = BOUNDARY.strict_env

WORKSPACE_HELP = "Workspace root directory [default: the devkit project containing the current directory]"


def workspace_option[F: Callable[..., Any]](help: str = WORKSPACE_HELP) -> Callable[[F], F]:
    """``-w/--workspace-root`` (parameter ``workspace_root``, default ``None``); ``resolve_root`` checks the value."""
    return click.option("--workspace-root", "-w", "workspace_root", default=None, type=str, help=help)


def existing_directory(value: str | Path, param: str = "--workspace-root") -> Path:
    """``value`` resolved; raises ``ArgumentError`` naming ``param`` unless it is an existing directory.

    An empty or whitespace-only value is refused rather than read as the current directory.
    """
    fix = f"Pass an existing directory to {param}"
    if isinstance(value, str) and not value.strip():
        raise ArgumentError(f"{param} is empty", target_files=[param], fix=fix)
    try:
        path = Path(value).resolve()
        is_dir = path.is_dir()
    except (RuntimeError, OSError) as exc:  # Python 3.12 raises RuntimeError for a symlink loop
        raise ArgumentError(f"{param} {value}: cannot be resolved: {exc}", target_files=[param], fix=fix) from exc
    if not is_dir:
        raise ArgumentError(f"{param} {value}: not an existing directory", target_files=[param], fix=fix)
    return path


def resolve_root(value: str | Path | None) -> Path:
    """``--workspace-root`` when given (an existing directory that can be a devkit root: outside Git, or the top
    level of its Git work tree), else the devkit root of the cwd."""
    if value is not None:
        return require_devkit_root(existing_directory(value))
    return find_project_root(Path.cwd())
