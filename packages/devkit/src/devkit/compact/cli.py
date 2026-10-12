"""``devkit run``: run a command and print a bounded view of its output; the full log stays on disk.

Text stdout is ``[RUN: ...]``, then ``[RUN_SUMMARY: ...]`` and
``[RUN_WARNING: ...]`` lines, ``[RUN_OMITTED: ...]`` when a budget was
exceeded and, only when the command failed, ``[RUN_OUTPUT: ...]`` (with the
number of lines filtered out) followed by the excerpt. stderr carries the advisory blocks of nested ``devkit`` commands
(warnings and notices, then the runner's own notices, then errors). The
command inherits the resolved ``-q``/``-v``/``--strict`` as ``DEVKIT_QUIET``,
``DEVKIT_VERBOSE`` and ``DEVKIT_STRICT``.

Exit codes: ``0`` the command succeeded, ``1`` it failed (its own code is
``exit=`` on the ``[RUN]`` line), ``2`` it could not be started or the
arguments are invalid.
"""

from __future__ import annotations

import dataclasses
import json
import math
import os
import re
import sys

import click

from devkit.advisory import ExitCode, Level
from devkit.compact.execute import CommandRun, run_command
from devkit.compact.scan import Omitted, RelayedAdvisory
from devkit.core.cli import (
    FORMAT_OPTION,
    QUIET_ENV,
    STRICT_ENV,
    VERBOSE_ENV,
    boundary,
    echo_json,
    echo_notices,
    exit_on_warnings,
    is_json,
    output_settings,
)
from devkit.core.errors import ArgumentError

_BARE = re.compile(r'[^\s"\]]+')


def _quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _value(value: str) -> str:
    """``-`` when empty, bare without spaces, quotes or brackets, else a JSON string."""
    if not value:
        return "-"
    return value if _BARE.fullmatch(value) else _quote(value)


def _outcome(run: CommandRun) -> str:
    return "passed" if run.passed else "failed"


def _omitted(run: CommandRun) -> Omitted:
    """What the view left out; the excerpt counts only when it is shown (the command failed)."""
    return run.scan.omitted if not run.passed else dataclasses.replace(run.scan.omitted, output=0)


def _echo_text(run: CommandRun) -> None:
    found = run.scan
    click.echo(f"[RUN: {_quote(run.command)} outcome={_outcome(run)} exit={run.exit_code} log={_value(str(run.log))}]")
    for summary in found.summaries:
        click.echo(f"[RUN_SUMMARY: {_quote(summary)}]")
    for warning in found.warnings:
        click.echo(f"[RUN_WARNING: {_quote(warning.message)} location={_value(warning.location)}]")
    omitted = _omitted(run)
    if omitted:
        click.echo(
            f"[RUN_OMITTED: summaries={omitted.summaries} warnings={omitted.warnings} "
            f"advisories={omitted.advisories} output={omitted.output}]"
        )
    if not run.passed:
        click.echo(f"[RUN_OUTPUT: shown={len(found.output)} omitted={omitted.output} filtered={found.filtered}]")
        if found.output:
            click.echo(found.output, nl=not found.output.endswith("\n"))


def _echo_json(run: CommandRun) -> None:
    found = run.scan
    omitted = _omitted(run)
    echo_json(
        {
            "command": list(run.argv),
            "outcome": _outcome(run),
            "exit_code": run.exit_code,
            "log": str(run.log),
            "summaries": list(found.summaries),
            "warnings": [{"message": w.message, "location": w.location} for w in found.warnings],
            "advisories": [{"level": a.level.value, "text": a.text} for a in found.advisories],
            "omitted": {
                "summaries": omitted.summaries,
                "warnings": omitted.warnings,
                "advisories": omitted.advisories,
                "output": omitted.output,
            },
            "output": None if run.passed else found.output,
            "filtered": 0 if run.passed else found.filtered,
            "notices": [notice.to_dict() for notice in run.notices],
        }
    )


def _echo_advisories(advisories: tuple[RelayedAdvisory, ...]) -> None:
    for advisory in advisories:
        click.echo(advisory.text, err=True)


@click.command(
    name="run",
    context_settings={"ignore_unknown_options": True, "allow_interspersed_args": False},
)
@click.option(
    "--slow-after",
    type=float,
    default=60.0,
    show_default=True,
    metavar="SECONDS",
    help="Add a RUN_SLOW_COMMAND notice when the command runs this long; 0 turns it off",
)
@FORMAT_OPTION
@click.argument("command", nargs=-1, required=True, type=click.UNPROCESSED)
@boundary
def run_cmd(slow_after: float, output_format: str, command: tuple[str, ...]) -> None:
    """Run COMMAND with its full output in a log file; print its outcome, summaries, warnings and,
    when it failed, an excerpt.

    Options go before COMMAND; everything from COMMAND on is passed to it unchanged
    (`devkit run -- just test`). The command runs in the current directory.
    """
    if not math.isfinite(slow_after) or slow_after < 0:
        raise ArgumentError(
            f"--slow-after {slow_after:g}: not a finite number of seconds >= 0",
            target_files=["--slow-after"],
            fix="Pass --slow-after a number of seconds, or 0 to turn the notice off",
        )
    settings = output_settings()
    env = {
        **os.environ,
        QUIET_ENV: "1" if settings.quiet else "0",
        VERBOSE_ENV: "1" if settings.verbose else "0",
        STRICT_ENV: "1" if settings.strict else "0",
    }
    run = run_command(command, env=env, slow_after=slow_after, notices=not settings.quiet)
    if is_json(output_format):
        _echo_json(run)
    else:
        _echo_text(run)
    advisories = run.scan.advisories
    _echo_advisories(tuple(a for a in advisories if a.level is not Level.ERROR))
    echo_notices(run.notices)
    _echo_advisories(tuple(a for a in advisories if a.level is Level.ERROR))
    if not run.passed:
        sys.exit(int(ExitCode.FINDINGS))
    exit_on_warnings(run.notices)
    # A relayed warning was reported by this run too, even when a wrapper hid the nested command's exit code.
    if settings.strict and any(a.level is Level.WARNING for a in advisories):
        sys.exit(int(ExitCode.FINDINGS))
