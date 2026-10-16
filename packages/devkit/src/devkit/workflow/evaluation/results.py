"""The result of evaluating a unit against a workflow, and its parts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from devkit.advisory import AdvisoryError
from devkit.workflow.definition.checks import CheckClass, CheckResult
from devkit.workflow.definition.definition import StageDefinition
from devkit.workflow.errors import DecisionRecordError, EnvelopeFormatError
from devkit.workflow.evaluation.requests import Request
from devkit.workflow.unit.binding import Binding
from devkit.workflow.unit.decisions import Decision
from devkit.workflow.unit.envelope import Hold

if TYPE_CHECKING:
    from devkit.workflow.handoff import Handoff


@dataclass(frozen=True)
class Skipped:
    id: str
    reason: str  # the policy entry that skipped the stage, e.g. approvals.<gate>=off or stages.<id>=off

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "reason": self.reason}


@dataclass(frozen=True)
class GateStatus:
    """The gate of the current stage.

    ``source`` says what satisfied it: ``policy`` (``auto``), ``given``
    (``--given``) or ``decision`` (an accepted record, named by ``decision``);
    empty while it is not satisfied.
    """

    name: str
    policy: str
    satisfied: bool
    source: str = ""
    decision: str | None = None
    held: bool = False  # an unresolved problem or unanswered question keeps it from passing, whatever its source

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "policy": self.policy,
            "satisfied": self.satisfied,
            "source": self.source or None,
            "decision": self.decision,
            "held": self.held,
        }


@dataclass(frozen=True)
class Delegate:
    role: str
    isolation: str
    contract: str | None = None  # workspace-relative path of the role's contract, when known

    def to_dict(self) -> dict[str, str | None]:
        return {"role": self.role, "isolation": self.isolation, "contract": self.contract}


@dataclass(frozen=True)
class Waiting:
    class_: CheckClass
    checks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"class": self.class_.value, "checks": list(self.checks)}


@dataclass(frozen=True)
class Drift:
    recorded: str
    current: str

    def to_dict(self) -> dict[str, str]:
        return {"recorded": self.recorded, "current": self.current}


@dataclass
class UnitEvaluation:
    """The evaluation of a unit against a workflow: where it stands, what is unmet and what comes next.

    Collected problems are ``AdvisoryError`` instances: ``envelope_errors``,
    ``decision_errors`` and ``lint_error`` (the ``devkit.rules`` error that
    stopped ``lint-clean``, passed through unchanged). ``to_dict`` lists them
    together under ``errors``.
    """

    workflow: str
    unit: str
    status: str
    binding: Binding
    done: list[str] = field(default_factory=list)
    skipped: list[Skipped] = field(default_factory=list)
    stage: StageDefinition | None = None
    unmet: list[CheckResult] = field(default_factory=list)
    next_skill: str = ""
    delegate: Delegate | None = None
    gate: GateStatus | None = None
    waiting: Waiting | None = None
    envelope_errors: list[EnvelopeFormatError] = field(default_factory=list)
    drift: Drift | None = None
    bound_elsewhere: str | None = None  # the workflow the unit is bound to, when evaluated against another
    lint_error: AdvisoryError | None = None
    handoff: Handoff | None = None
    requests: list[Request] = field(default_factory=list)
    decision_errors: list[DecisionRecordError] = field(default_factory=list)
    stale_approvals: list[Decision] = field(default_factory=list)  # approvals for stages after the current one
    hold: Hold = field(default_factory=Hold)  # unresolved problems and unanswered questions, whatever the segment
    passed_gates: list[tuple[str, GateStatus]] = field(default_factory=list)  # (stage, gate) of done gated stages

    @property
    def complete(self) -> bool:
        return self.stage is None

    @property
    def blocked_by_drift(self) -> bool:
        """Drift under in-flight work: the definition changed and a stage is still current."""
        return self.drift is not None and self.stage is not None

    @property
    def errors(self) -> list[AdvisoryError]:
        """Every collected problem: envelope errors, decision errors and the lint error."""
        lint = [self.lint_error] if self.lint_error is not None else []
        return [*self.envelope_errors, *self.decision_errors, *lint]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "unit": self.unit,
            "status": self.status,
            "bound": self.binding.bound,
            "bound_elsewhere": self.bound_elsewhere,
            "done": list(self.done),
            "skipped": [s.to_dict() for s in self.skipped],
            "stage": self.stage.to_dict() if self.stage else None,
            "unmet": [u.to_dict() for u in self.unmet],
            "next_skill": self.next_skill or None,
            "delegate": self.delegate.to_dict() if self.delegate else None,
            "gate": self.gate.to_dict() if self.gate else None,
            "waiting": self.waiting.to_dict() if self.waiting else None,
            "complete": self.complete,
            "drift": self.drift.to_dict() if self.drift else None,
            "handoff": self.handoff.to_dict() if self.handoff else None,
            "requests": [r.to_dict() for r in self.requests],
            "stale_approvals": [d.file for d in self.stale_approvals],
            **self.hold.to_dict(),
            "passed_gates": [{"stage": stage, **gate.to_dict()} for stage, gate in self.passed_gates],
            "errors": [e.to_dict() for e in self.errors],
        }
