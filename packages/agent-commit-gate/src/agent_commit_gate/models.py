"""Gate contracts: stages, results, the context a gate runs in, and the ``Gate`` protocol."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from agent_advisory import Actor, AdvisoryError, Retry


class Stage(StrEnum):
    """The Git hook a gate is attached to."""

    PRE_COMMIT = "pre-commit"
    COMMIT_MSG = "commit-msg"
    POST_COMMIT = "post-commit"

    @property
    def blocking(self) -> bool:
        """Git aborts the commit when this hook exits non-zero; post-commit runs after the commit exists."""
        return self is not Stage.POST_COMMIT


class Outcome(StrEnum):
    PASSED = "passed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class GateResult:
    """What a gate reports when it does not refuse. Refusal is an ``AdvisoryError`` raised from ``run``."""

    outcome: Outcome = Outcome.PASSED
    note: str = ""

    @classmethod
    def passed(cls, note: str = "") -> GateResult:
        return cls(Outcome.PASSED, note)

    @classmethod
    def skipped(cls, reason: str) -> GateResult:
        return cls(Outcome.SKIPPED, reason)


class GateError(AdvisoryError):
    """Raised by a gate to refuse the commit; use ``GateError.blocked(...)`` for policy refusals."""

    code = "GATE_FAILED"


class GateConfigError(AdvisoryError):
    """The ``[gates]`` configuration, a gate's settings, or a deployed gate file is invalid."""

    code = "GATE_CONFIG_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


@dataclass(frozen=True)
class GateContext:
    """Where and why a gate runs. ``settings`` is the running gate's effective settings."""

    repo_root: Path
    git_dir: Path  # the common git dir, shared by every worktree
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


@runtime_checkable
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
