"""Command-line plumbing shared by every ``devkit`` command group: the ``devkit_cli`` toolkit configured for devkit.

The agent-first output contract (``docs/architecture/ARCH-08-1-agent-output.md``) is implemented once, in
``devkit_cli``; this module binds it to devkit and adds what only devkit's commands share:

- ``BOUNDARY`` (``boundary``): ``devkit_cli.Boundary`` with the ``devkit`` logger hierarchy and the ``DEVKIT_``
  environment prefix, so ``-q/--quiet``, ``-v/--verbose`` and ``--strict`` read ``DEVKIT_QUIET``,
  ``DEVKIT_VERBOSE`` and ``DEVKIT_STRICT`` and ``-v`` prints every ``devkit`` log record as an ``[INFO]`` line;
- the output helpers of ``devkit_cli`` (``FORMAT_OPTION``, ``echo_json``, ``echo_notices``, ``exit_on_warnings``,
  ``exit_on_problems``, ``report_exit_code``, ``Reported``, ...), re-exported so command modules import one module;
- ``workspace_option`` (``-w/--workspace-root``) and ``resolve_root``: the explicit workspace root, else the devkit
  root found from the current directory (``devkit_dist.features.project.repositories.project``);
- ``field_value`` and ``yes_no``: the one rendering of a sentinel field value (``ARCH-08-1-agent-output`` §3);
  ``sentinel``, ``fields_line`` and ``echo_page`` build the sentinel lines on it;
- ``version_option``: the ``--version`` flag of a command group, printing one ``[VERSION: <label> <version>]`` line.

click only parses syntax here: every semantic argument check raises ``ArgumentError`` (``ARGUMENT_INVALID``)
through the boundary, so a JSON caller still receives one document.
"""

from __future__ import annotations

import json
import re
import shlex
from collections.abc import Callable, Sequence
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
    render_json,
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
    "echo_page",
    "existing_directory",
    "exit_on_problems",
    "exit_on_warnings",
    "field_value",
    "fields_line",
    "highest_exit_code",
    "is_json",
    "output_options",
    "output_settings",
    "render_json",
    "report_exit_code",
    "resolve_output",
    "resolve_root",
    "sentinel",
    "version_option",
    "workspace_option",
    "yes_no",
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

# A value stays bare unless it has whitespace or a character that delimits a sentinel or a field.
_BARE_VALUE = re.compile(r'[^\s"\[\]=\\]+')


def yes_no(value: bool) -> str:
    """A boolean sentinel field: ``yes`` or ``no``."""
    return "yes" if value else "no"


def field_value(value: object) -> str:
    """``value`` as one token of a ``[KIND: ...]`` sentinel line (``ARCH-08-1-agent-output`` §3).

    ``-`` for ``None`` or an empty string, ``yes``/``no`` for a boolean, bare when the text has no whitespace,
    ``"``, ``[``, ``]``, ``=`` or backslash, else a JSON string, so every fact stays on one line.
    """
    if value is None or value == "":
        return "-"
    if isinstance(value, bool):
        return yes_no(value)
    text = str(value)
    return text if _BARE_VALUE.fullmatch(text) else json.dumps(text, ensure_ascii=False)


def sentinel(name: str, positional: object, /, **fields: object) -> str:
    """``[KIND: <positional> key=value ...]``, each value rendered by ``field_value``."""
    parts = [field_value(positional), *(f"{key}={field_value(item)}" for key, item in fields.items())]
    return f"[{name}: {' '.join(parts)}]"


def fields_line(name: str, /, **fields: object) -> str:
    """``[KIND: key=value ...]``, a sentinel without a positional value."""
    return f"[{name}: {' '.join(f'{key}={field_value(item)}' for key, item in fields.items())}]"


def echo_page(command: str, total: int, offset: int, limit: int, count: int, next_command: Sequence[str]) -> None:
    """``[PAGE: total= offset= limit= count= next=]`` and, when more items follow, ``[NEXT_CMD: ...]``.

    ``command`` is the command line's fixed prefix (``uv run devkit docs``); ``next_command`` is the command's own
    argument list without ``--offset``, shell-quoted after it. ``limit`` ``0`` means no limit.
    """
    following = offset + count if limit and offset + count < total else None
    click.echo(fields_line("PAGE", total=total, offset=offset, limit=limit, count=count, next=following))
    if following is not None:
        args = [*next_command, "--offset", str(following)]
        click.echo(f"[NEXT_CMD: {command} {shlex.join(args)}]")


def version_option[F: Callable[..., Any]](distribution: str, label: str | None = None) -> Callable[[F], F]:
    """``--version``: print one ``[VERSION: <label> <version>]`` line, the installed version of ``distribution``, and
    exit; ``label`` defaults to the distribution name (``devkit`` itself passes ``label="devkit"``)."""
    shown = label or distribution

    def print_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
        if not value or ctx.resilient_parsing:
            return
        from importlib.metadata import version

        click.echo(f"[VERSION: {shown} {version(distribution)}]")
        ctx.exit()

    return click.option(
        "--version",
        is_flag=True,
        expose_value=False,
        is_eager=True,
        callback=print_version,
        help=f"Print a [VERSION: {shown} <version>] line and exit",
    )


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
