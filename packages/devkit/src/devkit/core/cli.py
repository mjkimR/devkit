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
  cannot run at all;
- ``output_options`` (applied by ``boundary``, so every command has them):
  ``-q/--quiet``, ``-v/--verbose`` and ``--strict``, or ``DEVKIT_QUIET``,
  ``DEVKIT_VERBOSE`` and ``DEVKIT_STRICT``; ``echo_notices`` prints the
  warnings and notices a command returned after its result, and
  ``exit_on_warnings`` applies ``--strict``. Under ``--verbose`` every
  ``devkit`` log record is printed on stderr as an ``[INFO]`` line.

The output contract is ``docs/architecture/agent-output.md``.

click only parses syntax here: every semantic argument check raises
``ArgumentError`` (``ARGUMENT_INVALID``) through the boundary, so a JSON
caller still receives one document.
"""

from __future__ import annotations

import contextlib
import contextvars
import functools
import json
import logging
import os
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click

from devkit.advisory import AdvisoryError, ExitCode, Level, as_advisory_error
from devkit.core.errors import ArgumentError
from devkit.core.project import find_project_root

WORKSPACE_HELP = "Workspace root directory [default: the devkit project containing the current directory]"

QUIET_ENV = "DEVKIT_QUIET"
VERBOSE_ENV = "DEVKIT_VERBOSE"
STRICT_ENV = "DEVKIT_STRICT"

LOGGER = "devkit"
_CONTINUATION = " " * len("[INFO]   ")
_log = logging.getLogger(__name__)

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


@dataclass(frozen=True)
class OutputSettings:
    """The output options of the running command: ``quiet`` hides notices, ``verbose`` shows logs, ``strict``
    makes a warning exit ``1``."""

    quiet: bool = False
    verbose: bool = False
    strict: bool = False


_settings: contextvars.ContextVar[OutputSettings | None] = contextvars.ContextVar("devkit_output", default=None)


def output_settings() -> OutputSettings:
    """The ``OutputSettings`` of the running command; all off outside one."""
    return _settings.get() or OutputSettings()


def _env(name: str) -> bool:
    return os.environ.get(name) == "1"


def resolve_output(quiet: bool, verbose: bool, strict: bool) -> OutputSettings:
    """Combine the flags with the environment: a flag wins; quiet together with verbose is ``ArgumentError``."""
    if quiet or verbose:
        sources = ["--quiet", "--verbose"]
    else:
        quiet, verbose = _env(QUIET_ENV), _env(VERBOSE_ENV)
        sources = [f"{QUIET_ENV}=1", f"{VERBOSE_ENV}=1"]
    if quiet and verbose:
        raise ArgumentError(
            f"{' and '.join(sources)} cannot be combined",
            target_files=sources,
            fix="Pass at most one of -q/--quiet and -v/--verbose",
        )
    return OutputSettings(quiet=quiet, verbose=verbose, strict=strict or _env(STRICT_ENV))


def output_options[F: Callable[..., Any]](fn: F) -> F:
    """Add ``-q/--quiet``, ``-v/--verbose`` and ``--strict`` (parameters ``quiet``, ``verbose``, ``strict``).

    ``boundary`` applies it and consumes the three parameters, so a command never sees them.
    """
    fn = click.option(
        "--strict", "strict", is_flag=True, help=f"Exit 1 when a warning was reported (or {STRICT_ENV}=1)"
    )(fn)
    fn = click.option(
        "--verbose", "-v", "verbose", is_flag=True, help=f"Also print [INFO] log lines on stderr (or {VERBOSE_ENV}=1)"
    )(fn)
    return click.option(
        "--quiet", "-q", "quiet", is_flag=True, help=f"Hide [NOTICE] blocks on stderr (or {QUIET_ENV}=1)"
    )(fn)


_LEVEL_ORDER = {Level.ERROR: 0, Level.WARNING: 1, Level.NOTICE: 2}


def echo_notices(notices: Iterable[AdvisoryError]) -> None:
    """Render the warnings and notices a command returned on stderr, after its result.

    Warnings come first, then notices, each in the order the command collected
    them, so what the user must hear about is never buried; ``--quiet`` skips
    the notices. JSON keeps the collected order.
    """
    quiet = output_settings().quiet
    for notice in sorted(notices, key=lambda notice: _LEVEL_ORDER[notice.level]):
        if quiet and notice.level is Level.NOTICE:
            continue
        click.echo(notice.render(), err=True)


def exit_on_warnings(notices: Iterable[AdvisoryError]) -> None:
    """Under ``--strict``, exit ``1`` when any of ``notices`` is a warning; otherwise return."""
    if output_settings().strict and any(notice.level is Level.WARNING for notice in notices):
        sys.exit(int(ExitCode.FINDINGS))


class _InfoFormatter(logging.Formatter):
    """A log record as ``[INFO]   <module>: <message>``, its further lines (a traceback) as continuation lines.

    ``<module>`` is the logger name without the ``devkit.`` prefix (``gate.engine.runner``), so an agent
    reading ``-v`` output knows which part of devkit spoke.
    """

    def format(self, record: logging.LogRecord) -> str:
        head, *rest = super().format(record).splitlines() or [""]
        source = record.name.removeprefix(f"{LOGGER}.")
        return "\n".join([f"[INFO]   {source}: {head}".rstrip(), *(f"{_CONTINUATION}{line}".rstrip() for line in rest)])


@contextlib.contextmanager
def _logs_on_stderr(enabled: bool) -> Iterator[None]:
    """Print every ``devkit`` log record on stderr while the command runs, when ``enabled``."""
    if not enabled:
        yield
        return
    logger = logging.getLogger(LOGGER)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_InfoFormatter())
    previous = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        yield
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)


def boundary(fn: Callable[..., Any] | None = None, *, json_only: bool = False) -> Any:
    """Decorate a click command so every error leaves through the Agent Advisory Protocol.

    Use as ``@boundary`` or ``@boundary(json_only=True)``. It adds the output
    options (``output_options``) and applies them while the command runs. An
    error is rendered on stderr; when stdout is JSON (``json_only``, or the
    command's ``output_format`` parameter is ``json``) ``{"error": {...}}`` is
    printed there too, unless the error is ``Reported`` (its result is already
    there). The process exits with the error's ``exit_code``; any other
    exception is ``UNEXPECTED_ERROR``, its traceback logged for ``--verbose``.
    click's own exits and usage errors pass through.
    """

    def decorate(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, quiet: bool = False, verbose: bool = False, strict: bool = False, **kwargs: Any) -> Any:
            token: contextvars.Token[OutputSettings | None] | None = None
            try:
                settings = resolve_output(quiet, verbose, strict)
                token = _settings.set(settings)
                with _logs_on_stderr(settings.verbose):
                    try:
                        return func(*args, **kwargs)
                    except Exception as exc:
                        expected = isinstance(exc, AdvisoryError) and exc.level is Level.ERROR
                        if not (expected or isinstance(exc, (click.ClickException, Reported))):
                            _log.debug("unexpected error", exc_info=exc)  # a raised notice included
                        raise
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
            finally:
                if token is not None:
                    _settings.reset(token)

        return output_options(wrapper)

    return decorate if fn is None else decorate(fn)
