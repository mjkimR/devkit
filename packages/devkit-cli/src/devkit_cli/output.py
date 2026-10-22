"""What a command writes: its result on stdout, the advisories it returned on stderr, and its exit code.

Every function here reads the running command's ``OutputSettings`` (set by a ``Boundary``) from a context
variable, so a command module needs no reference to the boundary that wraps it:

- ``FORMAT_OPTION`` (``--format text|json``, case-insensitive) and ``is_json``;
- ``echo_json``: stdout JSON is always exactly one object, in UTF-8;
- ``echo_notices``: the warnings and notices a command returned, on stderr after its result (in JSON mode the
  result carries them instead); ``exit_on_warnings`` applies ``--strict``;
- ``exit_on_problems``: a command that does work and collected problems exits with the highest ``exit_code``
  among them; ``report_exit_code``: a status or show command exits ``1`` when its report lists any problem.

The contract is ``ARCH-08-1-agent-output`` of the devkit repository.
"""

from __future__ import annotations

import contextvars
import json
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

import click
from devkit.advisory import AdvisoryError, ExitCode, Level

FORMAT_OPTION = click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format",
)


@dataclass(frozen=True)
class OutputSettings:
    """The output options of the running command: ``quiet`` hides notices, ``verbose`` shows logs, ``strict``
    makes a warning exit ``1``; ``json`` is set by the boundary when stdout is JSON, so advisories stay off stderr."""

    quiet: bool = False
    verbose: bool = False
    strict: bool = False
    json: bool = False


_settings: contextvars.ContextVar[OutputSettings | None] = contextvars.ContextVar("devkit_cli_output", default=None)
# Warnings and notices a JSON-mode command passed to ``echo_notices``: an error document printed afterwards carries them.
_unprinted: contextvars.ContextVar[list[AdvisoryError] | None] = contextvars.ContextVar(
    "devkit_cli_notices", default=None
)


def output_settings() -> OutputSettings:
    """The ``OutputSettings`` of the running command; all off outside one."""
    return _settings.get() or OutputSettings()


def is_json(output_format: object) -> bool:
    """Whether a ``--format`` value selects JSON."""
    return str(output_format or "text").lower() == "json"


def echo_json(data: Mapping[str, object]) -> None:
    """Print one JSON object on stdout.

    Text is written as UTF-8, not ``\\uXXXX`` escapes, so a non-English path or message reaches the agent as it is
    and costs no extra context. The boundary makes stdout UTF-8 with ``backslashreplace``, so the bytes never depend
    on the locale and a ``surrogateescape``-decoded path (a lone surrogate) is written as its ``\\uXXXX`` escape,
    which is still valid JSON.
    """
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))


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

    The report itself was produced, so a problem's own ``exit_code`` (``2`` for a configuration or load problem)
    does not apply here.
    """
    return int(ExitCode.FINDINGS) if any(True for _ in problems) else 0


def exit_on_problems(problems: Sequence[AdvisoryError], *, report: bool = False) -> None:
    """Render each problem on stderr and exit; return when there are none.

    The exit code is the highest ``exit_code`` among ``problems``, or ``report_exit_code`` (always ``1``) when
    ``report`` marks a status or show command. In JSON mode nothing is rendered: the command's JSON result lists the
    problems.
    """
    if not problems:
        return
    if not output_settings().json:
        for problem in problems:
            click.echo(problem.render(), err=True)
    sys.exit(report_exit_code(problems) if report else highest_exit_code(problems))


_LEVEL_ORDER = {Level.ERROR: 0, Level.WARNING: 1, Level.NOTICE: 2}


def echo_notices(notices: Iterable[AdvisoryError]) -> None:
    """Render the warnings and notices a command returned on stderr, after its result.

    Warnings come first, then notices, each in the order the command collected them, so what the user must hear
    about is never buried; ``--quiet`` skips the notices. In JSON mode nothing is rendered: the JSON result lists them
    in the collected order, and an error document printed instead of a result carries them under ``notices``.
    """
    settings = output_settings()
    if settings.json:
        pending = _unprinted.get()
        if pending is not None:
            pending.extend(notices)
        return
    quiet = settings.quiet
    for notice in sorted(notices, key=lambda notice: _LEVEL_ORDER[notice.level]):
        if quiet and notice.level is Level.NOTICE:
            continue
        click.echo(notice.render(), err=True)


def exit_on_warnings(notices: Iterable[AdvisoryError]) -> None:
    """Under ``--strict``, exit ``1`` when any of ``notices`` is a warning; otherwise return."""
    if output_settings().strict and any(notice.level is Level.WARNING for notice in notices):
        sys.exit(int(ExitCode.FINDINGS))
