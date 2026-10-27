"""Built-in ``pre-commit`` gate: run the project's own verification commands.

``commands`` (empty by default, which skips the gate) are shell command lines
run in order with ``sh -c`` from the top level of the work tree, each through
``devkit_agt.features.compact.run_command``: the full output goes to a log file and the
refusal carries only the compact view (summaries, failed tests or the last
lines, and the log path). Every command runs, so one commit attempt reports
every failure; an interrupted one (``CommandInterrupted``) aborts the stage. The error blocks of nested ``devkit`` commands are relayed in the
details. When a failed command is a ``devkit`` command that could not run (exit
``2`` with an error block of its own: rules that cannot load, a project that needs
``devkit sync``) the gate raises ``GATE_VERIFY_NOT_RUN`` instead of the
``GATE_VERIFY_FAILED`` refusal (``INPUT_ERROR``: fix what failed, commit again), since nothing judged the commit's content: ``AUTO``
with their fix when every relayed error is ``AUTO`` with the same one (a missing
``devkit sync``), else ``MAINTENANCE``.

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
included (``devkit_agt.features.rules.commit_index``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level
from devkit_core.core.git import run_git

from devkit_agt.features.compact import CommandRun, run_command, status_records
from devkit_agt.features.gate.models.base import BaseGate
from devkit_agt.features.gate.models.contracts import GateContext, GateResult, Stage
from devkit_agt.features.gate.models.errors import GateFindingsError, VerifyNotRunError, VerifyUnstagedNotice
from devkit_agt.features.rules import COMMIT_INDEX_VARIABLE

HOOK_GIT_VARIABLES = ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE", "GIT_PREFIX")


@dataclass(frozen=True)
class VerifyCommandsSettings:
    commands: list[str] = field(
        default_factory=list,
        metadata={"help": "Shell commands run in order from the repository root; empty skips the gate"},
    )


def _unstaged(ctx: GateContext) -> list[str]:
    """Tracked files with unstaged changes and untracked files, as Git reports them for this commit's index."""
    raw = run_git(ctx.repo_root, "status", "--porcelain=v1", "-z", "--untracked-files=normal")
    # Y is the work tree's column; "??" is untracked.
    return [os.fsdecode(path) for status, path in status_records(raw) if status[1:2] != b" "]


def _not_run(run: CommandRun) -> bool:
    """A nested ``devkit`` command that could not do its job: exit ``2`` with an error block of its own."""
    return run.exit_code == ExitCode.ERROR and any(item.level is Level.ERROR for item in run.scan.advisories)


def _auto_fix(runs: list[CommandRun]) -> str | None:
    """The one ``[FIX]`` that every relayed error of ``runs`` directs the agent to run (``AUTO``), if there is one."""
    modes: set[str] = set()
    fixes: set[str] = set()
    for run in runs:
        for item in run.scan.advisories:
            if item.level is not Level.ERROR:
                continue
            lines = item.text.splitlines()
            action = next((line for line in lines if line.startswith("[ACTION] ")), "")
            modes.add(action.removeprefix("[ACTION] ").split(" ", 1)[0])
            fixes.update(line.removeprefix("[FIX]").strip() for line in lines if line.startswith("[FIX]"))
    return next(iter(fixes)) if modes == {"AUTO"} and len(fixes) == 1 else None


class VerifyCommandsGate(BaseGate):
    def __init__(self) -> None:
        super().__init__(
            id="verify-commands",
            description="Run the project's verification commands (format, lint, type check, tests) before a commit.",
            stage=Stage.PRE_COMMIT,
            order=200,
            settings=VerifyCommandsSettings(),
        )

    def setup(self, settings: VerifyCommandsSettings) -> str:
        count = len(settings.commands)
        return f"commands={count}" if count else "commands=0 (skipped: no commands configured)"

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
            # An interrupted command raises CommandInterrupted, which the runner lets abort the stage.
            run = run_command(["sh", "-c", command], cwd=ctx.repo_root, env=env)
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
            details = [
                line
                for command, run in failed
                for line in run.failure_details(f"command: {command}  ", failed_tests=True)
            ]
            notes = [f"note: {notice.message}" for notice in notices if isinstance(notice, VerifyUnstagedNotice)]
            commands = ", ".join(command for command, _ in failed)
            not_run = [run for _, run in failed if _not_run(run)]
            if not_run:
                # When every nested error is AUTO with one fix (a missing sync), so is this one: run it, commit again.
                fix = _auto_fix(not_run)
                auto = {"actor": Actor.TOOL, "fix": fix} if fix else {}
                raise VerifyNotRunError(f"verification could not run: {commands}", *details, *notes, **auto)
            raise GateFindingsError(
                f"verification failed: {commands}",
                *details,
                *notes,
                code="GATE_VERIFY_FAILED",
                fix="Fix what the failed commands report (each log has the full output), then commit again",
            )
        return GateResult.passed(f"{len(settings.commands)} command(s) passed", notices=notices)
