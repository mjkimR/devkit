"""Built-in ``pre-commit`` gate: run the project's own verification commands.

``commands`` (empty by default, which skips the gate) are shell command lines
run in order with ``sh -c`` from the top level of the work tree, each through
``devkit.compact.run_command``: the full output goes to a log file and the
refusal carries only the compact view (summaries, failed tests or the last
lines, and the log path). Every command runs, so one commit attempt reports
every failure.

The commands see the working tree, not the index: unstaged edits to tracked
files and untracked files can make the result differ from what is committed.
The gate says so with a ``GATE_VERIFY_UNSTAGED`` notice rather than refusing,
since agents usually commit everything they changed. The hook's ``GIT_DIR``,
``GIT_INDEX_FILE``, ``GIT_WORK_TREE`` and ``GIT_PREFIX`` are removed from the
commands' environment, so a test suite that runs Git in its own repositories
is not pointed at this commit's index. The index is passed as
``DEVKIT_GIT_INDEX_FILE`` instead, which devkit's own staged checks
(``devkit rules check --staged``) use for this repository, so they evaluate
exactly what is committed, ``git commit -a`` and ``git commit <paths>``
included (``devkit.core.git.commit_index``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from devkit.advisory import AdvisoryError
from devkit.compact import CommandInterrupted, CommandRun, run_command
from devkit.core.git import COMMIT_INDEX_VARIABLE, run_git
from devkit.gate.engine.base import BaseGate
from devkit.gate.engine.models import GateContext, GateResult, Stage
from devkit.gate.errors import GateRefusedError, VerifyUnstagedNotice

HOOK_GIT_VARIABLES = ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE", "GIT_PREFIX")
# Last output lines shown for a failed command, beside its summaries and failed tests.
TAIL_LINES = 10


@dataclass(frozen=True)
class VerifyCommandsSettings:
    commands: list[str] = field(
        default_factory=list,
        metadata={"help": "Shell commands run in order from the repository root; empty skips the gate"},
    )


def _unstaged(ctx: GateContext) -> list[str]:
    """Tracked files with unstaged changes and untracked files, as Git reports them for this commit's index."""
    entries = run_git(ctx.repo_root, "status", "--porcelain=v1", "-z", "--untracked-files=normal").split(b"\0")
    paths = []
    for entry in entries:
        if len(entry) > 3 and (entry[:2] == b"??" or entry[1:2] not in (b" ", b"")):
            paths.append(os.fsdecode(entry[3:]))
    return paths


def _failure_details(command: str, run: CommandRun) -> list[str]:
    found = run.scan
    lines = [f"command: {command}  exit={run.exit_code}  log={run.log}"]
    lines += [f"  summary: {summary}" for summary in found.summaries]
    lines += [f"  failed: {failure.test}: {failure.message}" for failure in found.failures]
    shown = set(found.summaries)
    tail = [line for line in found.output.splitlines() if line.strip() and line not in shown][-TAIL_LINES:]
    lines += [f"  | {line}" for line in tail]
    return lines


class VerifyCommandsGate(BaseGate):
    def __init__(self) -> None:
        super().__init__(
            id="verify-commands",
            description="Run the project's verification commands (format, lint, type check, tests) before a commit.",
            stage=Stage.PRE_COMMIT,
            order=200,
            settings=VerifyCommandsSettings(),
        )

    def run(self, ctx: GateContext) -> GateResult:
        settings: VerifyCommandsSettings = ctx.settings
        if not settings.commands:
            return GateResult.skipped("no commands configured")
        unstaged = _unstaged(ctx)
        env = {key: value for key, value in os.environ.items() if key not in HOOK_GIT_VARIABLES}
        if index := os.environ.get("GIT_INDEX_FILE"):
            env[COMMIT_INDEX_VARIABLE] = str(ctx.repo_root / index)  # Git may pass it relative to the top level
        failed: list[tuple[str, CommandRun]] = []
        notices: list[AdvisoryError] = []
        for command in settings.commands:
            try:
                run = run_command(["sh", "-c", command], cwd=ctx.repo_root, env=env)
            except CommandInterrupted:
                raise KeyboardInterrupt from None
            notices.extend(run.notices)
            if not run.passed:
                failed.append((command, run))
        if unstaged:
            notices.append(
                VerifyUnstagedNotice(
                    f"the commands checked the working tree, which differs from the commit in {len(unstaged)} file(s)",
                    *unstaged[:10],
                    *([f"... and {len(unstaged) - 10} more"] if len(unstaged) > 10 else []),
                )
            )
        if failed:
            details = [line for command, run in failed for line in _failure_details(command, run)]
            raise GateRefusedError(
                f"verification failed: {', '.join(command for command, _ in failed)}",
                *details,
                *(f"note: {notice.message}" for notice in notices if isinstance(notice, VerifyUnstagedNotice)),
                code="GATE_VERIFY_FAILED",
                fix="Fix what the failed commands report (each log has the full output), then commit again",
            )
        return GateResult.passed(f"{len(settings.commands)} command(s) passed", notices=notices)
