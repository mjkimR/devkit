"""Handing a completed unit to the next workflow: candidate evaluation, choosing, and rebinding."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any

from devkit.workflow.binding import Binding, HistoryEntry, write_binding
from devkit.workflow.checks import CheckResult
from devkit.workflow.decisions import (
    HANDOFF_REQUEST,
    Decision,
    DecisionError,
    load_decisions,
    new_decision,
    write_decision,
)
from devkit.workflow.definition import HANDOFF_GATE, WorkflowDocument, schema_hash
from devkit.workflow.errors import input_error
from devkit.workflow.requests import candidate_summary

if TYPE_CHECKING:
    from devkit.workflow.results import Result
    from devkit.workflow.workspace import UnitRef, Workspace


@dataclass(frozen=True)
class CandidateResult:
    workflow: str
    recommended: bool
    eligible: bool
    checks: tuple[CheckResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "recommended": self.recommended,
            "eligible": self.eligible,
            "checks": [c.to_dict() for c in self.checks],
        }


@dataclass(frozen=True)
class Handoff:
    """The handoff decision once the bound workflow is complete.

    ``chosen`` comes from a recorded, still-eligible choice under either
    policy, else under ``auto`` from the first eligible candidate; under
    ``ask`` without a recorded choice a person picks.
    """

    policy: str
    candidates: tuple[CandidateResult, ...]
    chosen: str | None = None
    decision: Decision | None = None  # recorded choice that produced ``chosen``, if any

    @property
    def eligible(self) -> tuple[str, ...]:
        return tuple(c.workflow for c in self.candidates if c.eligible)

    @property
    def recommended(self) -> tuple[str, ...]:
        return tuple(c.workflow for c in self.candidates if c.recommended and c.eligible)

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy": self.policy,
            "candidates": [c.to_dict() for c in self.candidates],
            "eligible": list(self.eligible),
            "recommended": list(self.recommended),
            "chosen": self.chosen,
            "decision": self.decision.file if self.decision else None,
        }


def evaluate_handoff(
    doc: WorkflowDocument,
    eval_ref: Callable[[str], CheckResult],
    recorded: Decision | None,
    policy: str,
) -> tuple[Handoff | None, DecisionError | None]:
    """Evaluate every ``next`` candidate and apply the handoff policy.

    ``recorded`` is the effective accepted ``handoff`` record of the current
    segment. A recorded choice that is not an eligible candidate is ignored
    and returned as a ``DecisionError``.
    """
    if not doc.next or policy == "off":
        return None, None
    results: list[CandidateResult] = []
    for cand in doc.next:
        checks = tuple(eval_ref(ref) for ref in cand.when)
        results.append(CandidateResult(cand.workflow, cand.recommended, all(c.satisfied for c in checks), checks))
    eligible = {c.workflow for c in results if c.eligible}
    ignored: DecisionError | None = None
    if recorded is not None:
        if isinstance(recorded.value, str) and recorded.value in eligible:
            return Handoff(policy, tuple(results), recorded.value, recorded), None
        ignored = DecisionError(
            recorded.file, f"handoff choice {recorded.value!r} is not an eligible candidate of {doc.id}; ignored"
        )
    chosen = next((c.workflow for c in results if c.eligible), None) if policy == "auto" else None
    return Handoff(policy, tuple(results), chosen), ignored


@dataclass(frozen=True)
class HandoffPlan:
    """What ``apply_handoff`` will do: rebind ``unit`` from ``source`` to ``target``."""

    unit: UnitRef
    source: WorkflowDocument
    target: WorkflowDocument
    policy: str
    decision: Decision | None  # the recorded choice used, if any
    explicit: bool  # the caller named the target


@dataclass(frozen=True)
class HandoffOutcome:
    unit: str
    source: str
    target: str
    workflow_hash: str
    policy: str
    decision: str | None
    history: tuple[HistoryEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit": self.unit,
            "from": self.source,
            "to": self.target,
            "workflow_hash": self.workflow_hash,
            "policy": self.policy,
            "decision": self.decision,
            "history": [h.to_dict() for h in self.history],
        }


def plan_handoff(ws: Workspace, unit: UnitRef, result: Result, choice: str | None = None) -> HandoffPlan:
    """Decide the target of a handoff, or raise a ``WorkflowError`` saying why there is none.

    ``result`` is the evaluation of ``unit`` against its bound workflow;
    ``choice`` is a candidate named by the caller (``handoff --workflow``).
    """
    doc = unit.doc
    if result.stage is not None:
        raise input_error(
            f"unit {unit.rel} has not completed workflow {doc.id}: stage {result.stage.id} is current",
            *(f"unmet={u.name}" for u in result.unmet),
            code="HANDOFF_NOT_READY",
            fix=f"Finish the current stage (`devkit workflow next --unit {unit.rel}`) before handing off",
        )
    if not doc.next:
        raise input_error(
            f"workflow {doc.id} declares no next candidates",
            code="HANDOFF_NONE",
            fix=f"Add a `next` list to {doc.id}, or start a new unit with `devkit workflow new`",
        )
    policy = ws.config.policy(HANDOFF_GATE)
    handoff = result.handoff
    if handoff is None or policy == "off":
        raise input_error(
            f"handoff is disabled by policy (approvals.{HANDOFF_GATE}=off)",
            code="HANDOFF_OFF",
            fix=f"Set [workflow.approvals].{HANDOFF_GATE} to ask or auto in .devkit/config.toml",
        )
    if choice is None:
        if handoff.chosen is None:
            if policy == "auto":
                raise input_error(
                    f"no candidate of {doc.id} is eligible for automatic handoff",
                    *(f"{c.workflow}: {candidate_summary(c.checks) or '-'}" for c in handoff.candidates),
                    code="HANDOFF_UNDECIDED",
                    fix="Satisfy a candidate's `when` checks, or choose one explicitly with --workflow <id>",
                )
            raise input_error(
                f"handoff from {doc.id} requires a choice (approvals.{HANDOFF_GATE}=ask)",
                *(
                    f"{c.workflow}: eligible={str(c.eligible).lower()} recommended={str(c.recommended).lower()}"
                    for c in handoff.candidates
                ),
                code="HANDOFF_CHOICE_REQUIRED",
                fix=(
                    "Present the candidates to the user, record their choice with "
                    f"`devkit workflow answer --unit {unit.rel} --request handoff --action accept --value <id>` "
                    "(or rerun with --workflow <id>), then run handoff again"
                ),
            )
        target_id, decision, explicit = handoff.chosen, handoff.decision, False
    else:
        by_id = {c.workflow: c for c in handoff.candidates}
        candidate = by_id.get(choice)
        if candidate is None:
            raise input_error(
                f"{choice!r} is not a next candidate of {doc.id}",
                code="HANDOFF_INVALID",
                fix=f"Choose one of: {', '.join(by_id)}",
            )
        if not candidate.eligible:
            raise input_error(
                f"candidate {choice!r} is not eligible: its preconditions do not hold",
                *(f"{k.name}={str(k.satisfied).lower()} {k.detail}".rstrip() for k in candidate.checks),
                code="HANDOFF_INELIGIBLE",
                fix="Satisfy the candidate's `when` checks first, or choose another candidate",
            )
        target_id, decision, explicit = choice, None, True
    target = ws.definition(target_id)
    target_anchor = ws.anchor_for(target)
    if target_anchor != unit.anchor:
        raise input_error(
            f"workflow {target.id} declares anchor {target_anchor}; unit {unit.rel} is identified by {unit.anchor}",
            code="HANDOFF_LAYOUT_MISMATCH",
            fix=f"Relocate the unit into the layout of {target.id} (anchor {target_anchor}), then run `devkit workflow bind --unit <new dir> --workflow {target.id}`",
        )
    return HandoffPlan(unit, doc, target, policy, decision, explicit)


def apply_handoff(plan: HandoffPlan, *, when: date | None = None, by: str = "", note: str = "") -> HandoffOutcome:
    """Rebind the unit to the plan's target and record the finished segment in its history.

    An explicit choice is first recorded as an accepted ``handoff`` decision so
    the audit trail names it; the history entry closes the segment at the
    highest decision sequence.
    """
    unit = plan.unit
    decision = plan.decision
    if plan.explicit:
        decisions = load_decisions(unit.dir)
        record = new_decision(
            decisions, HANDOFF_REQUEST, "accept", workflow=plan.source.id, value=plan.target.id, note=note, by=by
        )
        decision = write_decision(unit.dir, record)
    last = load_decisions(unit.dir).max_seq
    day = (when or date.today()).isoformat()
    binding = unit.binding
    entry = HistoryEntry(plan.source.id, binding.hash or schema_hash(plan.source), day, last)
    history = (*binding.history, entry)
    new_binding = Binding(plan.target.id, schema_hash(plan.target), history)
    write_binding(unit.anchor_path, new_binding)
    return HandoffOutcome(
        unit=unit.rel,
        source=plan.source.id,
        target=plan.target.id,
        workflow_hash=new_binding.hash,
        policy=plan.policy,
        decision=decision.file if decision else None,
        history=history,
    )
