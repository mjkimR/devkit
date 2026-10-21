"""``devkit run``: run a command and print a bounded view of its output; the full log stays on disk.

Text stdout is ``[RUN: ...]``, then ``[RUN_SUMMARY: ...]`` lines (for a
command that passed without one, ``[RUN_LAST_LINE: ...]`` lines: the last lines
of its output; for a command that failed, ``[RUN_FAILURE: ...]`` lines for the
failed tests the excerpt cuts out) and ``[RUN_WARNING: ...]`` lines, ``[RUN_OMITTED: ...]`` when a budget was
exceeded and, only when the command failed, ``[RUN_OUTPUT: ...]`` (with the
number of lines filtered out) followed by the excerpt. stderr carries the advisory blocks of nested ``devkit`` commands
(warnings and notices, then the runner's own notices, then errors). The
command inherits the resolved ``-q``/``-v``/``--strict`` as ``DEVKIT_QUIET``,
``DEVKIT_VERBOSE`` and ``DEVKIT_STRICT``. A run interrupted (Ctrl-C) or
terminated (``SIGTERM``, ``SIGHUP``) prints only its ``[RUN: ...
outcome=interrupted ...]`` line, with the log that holds the output so far.

Exit codes: ``0`` the command succeeded, ``1`` it failed (its own code is
``exit=`` on the ``[RUN]`` line), ``2`` it could not be started or the
arguments are invalid, ``128 + N`` the run was interrupted by signal ``N``.
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
from devkit_core.base.errors import ArgumentError
from devkit_core.core.logs import get_logger
from devkit_dist.adapters.cli import (
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

from devkit_agt.features.compact.models.scan import Failure, Omitted, RelayedAdvisory
from devkit_agt.features.compact.usecases.execute import CommandInterrupted, CommandRun, RunCommand

_BARE = re.compile(r'[^\s"\]]+')

_log = get_logger(__name__)


def _quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _value(value: str) -> str:
    """``-`` when empty, bare without spaces, quotes or brackets, else a JSON string."""
    if not value:
        return "-"
    return value if _BARE.fullmatch(value) else _quote(value)


def _outcome(run: CommandRun) -> str:
    if run.interrupted:
        return "interrupted"
    return "passed" if run.passed else "failed"


def _failed(run: CommandRun) -> bool:
    """Whether the command ran to the end and failed: only then is the excerpt shown."""
    return not run.passed and not run.interrupted


def _omitted(run: CommandRun) -> Omitted:
    """What the view left out; the excerpt and the failures beside it count only when they are shown (the
    command failed)."""
    return run.scan.omitted if not run.passed else dataclasses.replace(run.scan.omitted, failures=0, output=0)


def _failures(run: CommandRun) -> tuple[Failure, ...]:
    """The failed tests the excerpt cuts out, shown beside it: only for a command that failed."""
    return () if run.passed else run.scan.failures


def _last_lines(run: CommandRun) -> tuple[str, ...]:
    """The output's last lines, in place of a summary: only for a command that passed without one."""
    return run.scan.last_lines if run.passed and not run.scan.summaries else ()


def _text(run: CommandRun) -> str:
    found = run.scan
    lines = [f"[RUN: {_quote(run.command)} outcome={_outcome(run)} exit={run.exit_code} log={_value(str(run.log))}]"]
    lines += [f"[RUN_SUMMARY: {_quote(summary)}]" for summary in found.summaries]
    lines += [f"[RUN_LAST_LINE: {_quote(line)}]" for line in _last_lines(run)]
    lines += [
        f"[RUN_FAILURE: {_quote(failure.test)} kind={failure.kind} message={_value(failure.message)}]"
        for failure in _failures(run)
    ]
    lines += [f"[RUN_WARNING: {_quote(w.message)} location={_value(w.location)}]" for w in found.warnings]
    omitted = _omitted(run)
    if omitted:
        lines.append(
            f"[RUN_OMITTED: summaries={omitted.summaries} failures={omitted.failures} warnings={omitted.warnings} "
            f"advisories={omitted.advisories} output={omitted.output}]"
        )
    text = "\n".join(lines) + "\n"
    if _failed(run):
        text += f"[RUN_OUTPUT: shown={len(found.output)} omitted={omitted.output} filtered={found.filtered}]\n"
        if found.output:
            text += found.output if found.output.endswith("\n") else found.output + "\n"
    return text


def _json(run: CommandRun) -> dict[str, object]:
    found = run.scan
    omitted = _omitted(run)
    return {
        "command": list(run.argv),
        "outcome": _outcome(run),
        "exit_code": run.exit_code,
        "log": str(run.log),
        "summaries": list(found.summaries),
        "last_lines": list(_last_lines(run)),
        "failures": [{"test": f.test, "kind": f.kind, "message": f.message} for f in _failures(run)],
        "warnings": [{"message": w.message, "location": w.location} for w in found.warnings],
        "advisories": [{"level": a.level.value, "text": a.text} for a in found.advisories],
        "omitted": {
            "summaries": omitted.summaries,
            "failures": omitted.failures,
            "warnings": omitted.warnings,
            "advisories": omitted.advisories,
            "output": omitted.output,
        },
        "output": found.output if _failed(run) else None,
        "filtered": found.filtered if _failed(run) else 0,
        "notices": [notice.to_dict() for notice in run.notices],
    }


def _echo(run: CommandRun, output_format: str) -> int:
    """Print the result on stdout; return how many characters it took."""
    if is_json(output_format):
        data = _json(run)
        echo_json(data)
        return len(json.dumps(data, indent=2, ensure_ascii=False)) + 1  # as echo_json prints it
    text = _text(run)
    click.echo(text, nl=False)
    return len(text)


def _echo_advisories(advisories: tuple[RelayedAdvisory, ...]) -> None:
    """Relay nested blocks on stderr; in JSON mode the result's ``advisories`` already carries them."""
    if output_settings().json:
        return
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
    try:
        run = RunCommand().execute(command, env=env, slow_after=slow_after, notices=not settings.quiet)
    except CommandInterrupted as interrupted:
        # The command's group is stopped; the log shows where it stopped.
        _echo(interrupted.run, output_format)
        sys.exit(128 + interrupted.run.interrupted)
    shown = _echo(run, output_format)
    advisories = run.scan.advisories
    shown += sum(len(a.text) + 1 for a in advisories)
    read = run.scan.read
    _log.info("showed %d characters for %d of output (%.0f%%)", shown, read, 100 * shown / read if read else 0)
    _echo_advisories(tuple(a for a in advisories if a.level is not Level.ERROR))
    echo_notices(run.notices)
    _echo_advisories(tuple(a for a in advisories if a.level is Level.ERROR))
    if not run.passed:
        sys.exit(int(ExitCode.FINDINGS))
    exit_on_warnings(run.notices)
    # A relayed warning was reported by this run too, even when a wrapper hid the nested command's exit code.
    if settings.strict and any(a.level is Level.WARNING for a in advisories):
        sys.exit(int(ExitCode.FINDINGS))
