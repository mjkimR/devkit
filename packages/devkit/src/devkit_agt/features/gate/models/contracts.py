"""Gate contracts: stages, results, the context a gate runs in, and the ``Gate`` protocol."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError

from devkit_agt.features.gate.models.errors import DEVKIT, GateDefinitionError, GateResultError


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


def checked_notices(notices: object) -> tuple[AdvisoryError, ...]:
    """``notices`` as a tuple; raises ``GateResultError`` unless it is an iterable of ``AdvisoryError``."""
    try:
        items = tuple(notices)  # type: ignore[call-overload]  # checked here, whatever a gate passed
    except TypeError:
        raise GateResultError(
            f"GateResult notices is a {type(notices).__name__}, not a sequence of AdvisoryError"
        ) from None
    wrong = next((item for item in items if not isinstance(item, AdvisoryError)), None)
    if wrong is not None:
        raise GateResultError(
            f"a GateResult notice is a {type(wrong).__name__}, not an AdvisoryError; "
            "report a warning or notice as an AdvisoryError at level WARNING or NOTICE"
        )
    return items


@dataclass(frozen=True)
class GateResult:
    """What a gate reports when it does not refuse: passed or skipped.

    Refusal is an ``AdvisoryError`` (normally ``GateRefusedError``) raised from
    ``run``, so every failure carries an advisory; a ``FAILED`` result is
    rejected with ``GateResultError``. ``notices`` are warnings and notices the
    commit should not be blocked for (``AdvisoryError`` at level ``WARNING`` or
    ``NOTICE``; the runner lowers an ``ERROR`` to ``WARNING``); anything else
    among them is rejected with ``GateResultError`` too.
    """

    outcome: Outcome = Outcome.PASSED
    note: str = ""
    notices: tuple[AdvisoryError, ...] = ()

    def __post_init__(self) -> None:
        if self.outcome not in (Outcome.PASSED, Outcome.SKIPPED):
            raise GateResultError(
                f"a GateResult is passed or skipped, not {self.outcome!r}; refuse by raising GateRefusedError"
            )
        object.__setattr__(self, "notices", checked_notices(self.notices))

    @classmethod
    def passed(cls, note: str = "", notices: Sequence[AdvisoryError] = ()) -> GateResult:
        return cls(Outcome.PASSED, note, tuple(notices))

    @classmethod
    def skipped(cls, reason: str) -> GateResult:
        return cls(Outcome.SKIPPED, reason)


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
        if self.stage is not Stage.COMMIT_MSG:
            raise GateDefinitionError(f"message_file is only available to commit-msg gates (stage={self.stage})")
        if not self.args:
            raise ArgumentError(
                "commit-msg: no commit message file given",
                fix=f"Pass the message file: `{DEVKIT} gate run commit-msg <file>`",
            )
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
