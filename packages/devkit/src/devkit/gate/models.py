"""Gate contracts: stages, results, the context a gate runs in, and the ``Gate`` protocol."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

from devkit.advisory import Actor, AdvisoryError, ExitCode, Retry


class Stage(StrEnum):
    """The Git hook a gate is attached to."""

    PRE_COMMIT = "pre-commit"
    COMMIT_MSG = "commit-msg"
    POST_COMMIT = "post-commit"

    @property
    def blocking(self) -> bool:
        """Git aborts the commit when this hook exits non-zero; post-commit runs after the commit exists."""
        return self is not Stage.POST_COMMIT


RESULT_INVALID = "GATE_RESULT_INVALID"


class Outcome(StrEnum):
    PASSED = "passed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class GateResult:
    """What a gate reports when it does not refuse: passed or skipped.

    Refusal is an ``AdvisoryError`` (normally ``GateError.blocked``) raised from
    ``run``, so every failure carries an advisory; a ``FAILED`` result is rejected.
    """

    outcome: Outcome = Outcome.PASSED
    note: str = ""

    def __post_init__(self) -> None:
        if self.outcome not in (Outcome.PASSED, Outcome.SKIPPED):
            raise GateConfigError(
                f"a GateResult is passed or skipped, not {self.outcome!r}; refuse by raising GateError",
                code=RESULT_INVALID,
                input_error=False,
            )

    @classmethod
    def passed(cls, note: str = "") -> GateResult:
        return cls(Outcome.PASSED, note)

    @classmethod
    def skipped(cls, reason: str) -> GateResult:
        return cls(Outcome.SKIPPED, reason)


class GateError(AdvisoryError):
    """Raised by a gate to refuse the commit; use ``GateError.blocked(...)`` for policy refusals.

    A refusal is a negative result of a check that ran, so it exits ``FINDINGS`` (``1``).
    """

    code = "GATE_FAILED"
    exit_code = ExitCode.FINDINGS


class GateConfigError(AdvisoryError):
    """The ``[gates]`` configuration, a gate's settings, or a deployed gate file is invalid.

    ``input_error=False`` marks a defect in a gate's code (``MAINTENANCE``), such
    as an invalid ``id`` or a ``GateResult`` that is neither passed nor skipped.
    """

    code = "GATE_CONFIG_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


@dataclass(frozen=True)
class GateContext:
    """Where and why a gate runs. ``settings`` is the running gate's effective settings."""

    repo_root: Path  # top level of the work tree the commit is made in
    git_dir: Path  # this worktree's git dir (``.git/worktrees/<name>`` in a linked worktree)
    common_git_dir: Path  # the git dir shared by every worktree (hooks, ``devkit.config``)
    stage: Stage
    args: tuple[str, ...] = ()  # arguments Git passed to the hook
    settings: Any = None

    @property
    def message_file(self) -> Path:
        """The commit message file of a ``commit-msg`` run."""
        if self.stage is not Stage.COMMIT_MSG or not self.args:
            raise GateConfigError(f"message_file is only available to commit-msg gates (stage={self.stage})")
        path = Path(self.args[0])
        return path if path.is_absolute() else self.repo_root / path


class Gate(Protocol):
    id: str
    description: str
    stage: Stage
    # Lower runs first within a stage. Message transforms use < 100, checks default to 100.
    order: int
    # A gate may ship disabled and be switched on per project or per clone.
    enabled_by_default: bool
    # Dataclass instance holding default settings, or ``None`` when the gate has none.
    settings: Any

    def run(self, ctx: GateContext) -> GateResult | None: ...
