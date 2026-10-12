"""Command-line plumbing shared by every ``devkit`` command group.

One implementation of what the ``rules``, ``workflow``, ``gate`` and
distribution commands must agree on:

- ``workspace_option`` (``-w/--workspace-root``) and ``FORMAT_OPTION``
  (``--format text|json``, case-insensitive);
- ``resolve_root``: the explicit workspace root, else the project root found
  from the current directory;
- ``boundary``: renders any error as an Agent Advisory Protocol block on
  stderr and, when stdout is JSON, as ``{"error": {...}}`` on stdout, then
  exits with the error's ``exit_code``;
- ``echo_json``: stdout JSON is always exactly one object;
- ``exit_on_problems``: a command that does work and collected problems
  exits with the highest ``exit_code`` among them;
- ``report_exit_code``: a status or show command (``devkit status``,
  ``gate status``, ``workflow show``) exits ``1`` when its report lists any
  problem, whatever the problems' own codes; ``2`` is left for a command that
  cannot run at all.

click only parses syntax here: every semantic argument check raises
``ArgumentError`` (``ARGUMENT_INVALID``) through the boundary, so a JSON
caller still receives one document.
"""

from __future__ import annotations

import functools
import json
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import click

from devkit.advisory import AdvisoryError, ExitCode, as_advisory_error
from devkit.core.errors import ArgumentError
from devkit.core.project import find_project_root

WORKSPACE_HELP = "Workspace root directory [default: the devkit project containing the current directory]"

FORMAT_OPTION = click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format",
)


def workspace_option[F: Callable[..., Any]](help: str = WORKSPACE_HELP) -> Callable[[F], F]:
    """``-w/--workspace-root`` (parameter ``workspace_root``, default ``None``); ``resolve_root`` checks the value."""
    return click.option("--workspace-root", "-w", "workspace_root", default=None, type=str, help=help)


def is_json(output_format: object) -> bool:
    """Whether a ``--format`` value selects JSON."""
    return str(output_format or "text").lower() == "json"


def echo_json(data: Mapping[str, object]) -> None:
    """Print one JSON object on stdout."""
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


def existing_directory(value: str | Path, param: str = "--workspace-root") -> Path:
    """``value`` resolved; raises ``ArgumentError`` naming ``param`` unless it is an existing directory."""
    path = Path(value).resolve()
    if not path.is_dir():
        raise ArgumentError(
            f"{param} {value}: not an existing directory",
            target_files=[param],
            fix=f"Pass an existing directory to {param}",
        )
    return path


def resolve_root(value: str | Path | None) -> Path:
    """``--workspace-root`` when given (it must be an existing directory), else the project root of the cwd."""
    if value is not None:
        return existing_directory(value)
    return find_project_root(Path.cwd())


class Reported(Exception):
    """An error whose JSON result is already on stdout: the boundary renders only the advisory on stderr."""

    def __init__(self, error: AdvisoryError) -> None:
        super().__init__(str(error))
        self.error = error


def highest_exit_code(problems: Iterable[AdvisoryError]) -> int:
    """The highest ``exit_code`` among ``problems``; ``0`` when there are none."""
    return max((int(problem.exit_code) for problem in problems), default=0)


def report_exit_code(problems: Iterable[AdvisoryError]) -> int:
    """The exit code of a status or show command: ``1`` when its report lists any problem, else ``0``.

    The report itself was produced, so a problem's own ``exit_code`` (``2`` for
    a configuration or load problem) does not apply here.
    """
    return int(ExitCode.FINDINGS) if any(True for _ in problems) else 0


def exit_on_problems(problems: Sequence[AdvisoryError], *, report: bool = False) -> None:
    """Render each problem on stderr and exit; return when there are none.

    The exit code is the highest ``exit_code`` among ``problems``, or
    ``report_exit_code`` (always ``1``) when ``report`` marks a status or show command.
    """
    if not problems:
        return
    for problem in problems:
        click.echo(problem.render(), err=True)
    sys.exit(report_exit_code(problems) if report else highest_exit_code(problems))


def boundary[**P, R](fn: Callable[P, R] | None = None, *, json_only: bool = False) -> Any:
    """Decorate a click command so every error leaves through the Agent Advisory Protocol.

    Use as ``@boundary`` or ``@boundary(json_only=True)``. An error is
    rendered on stderr; when stdout is JSON (``json_only``, or the command's
    ``output_format`` parameter is ``json``) ``{"error": {...}}`` is printed
    there too, unless the error is ``Reported`` (its result is already there).
    The process exits with the error's ``exit_code``; any other exception is
    ``UNEXPECTED_ERROR``. click's own exits and usage errors pass through.
    """

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except (click.exceptions.Exit, click.ClickException, click.exceptions.Abort, SystemExit):
                raise
            except Reported as reported:
                click.echo(reported.error.render(), err=True)
                sys.exit(int(reported.error.exit_code))
            except Exception as exc:
                error = as_advisory_error(exc)
                if json_only or is_json(kwargs.get("output_format")):
                    echo_json({"error": error.to_dict()})
                click.echo(error.render(), err=True)
                sys.exit(int(error.exit_code))

        return wrapper

    return decorate if fn is None else decorate(fn)
