"""Handing a completed unit to the next workflow: candidate evaluation, choosing, and rebinding."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any

from devkit.workflow.definition.checks import CheckResult
from devkit.workflow.definition.definition import HANDOFF_GATE, WorkflowDocument, schema_hash
from devkit.workflow.errors import (
    HandoffChoiceIgnoredError,
    HandoffChoiceRequiredError,
    HandoffHeldError,
    HandoffIneligibleError,
    HandoffInvalidError,
    HandoffLayoutMismatchError,
    HandoffNoneError,
    HandoffNotReadyError,
    HandoffOffError,
    HandoffUndecidedError,
)
from devkit.workflow.evaluation.requests import candidate_summary
from devkit.workflow.unit.binding import Binding, HistoryEntry, render_binding, replace_text
from devkit.workflow.unit.decisions import HANDOFF_REQUEST, Decision, load_decisions, new_decision, write_decision

if TYPE_CHECKING:
    from devkit.workflow.evaluation.results import UnitEvaluation
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
) -> tuple[Handoff | None, HandoffChoiceIgnoredError | None]:
    """Evaluate every ``next`` candidate and apply the handoff policy.

    ``recorded`` is the effective accepted ``handoff`` record of the current
    segment. A recorded choice that is not an eligible candidate is ignored
    and returned as a ``HandoffChoiceIgnoredError`` (``HANDOFF_CHOICE_IGNORED``).
    """
    if not doc.next or policy == "off":
        return None, None
    results: list[CandidateResult] = []
    for cand in doc.next:
        checks = tuple(eval_ref(ref) for ref in cand.when)
        results.append(CandidateResult(cand.workflow, cand.recommended, all(c.satisfied for c in checks), checks))
    eligible = {c.workflow for c in results if c.eligible}
    ignored: HandoffChoiceIgnoredError | None = None
    if recorded is not None:
        if isinstance(recorded.value, str) and recorded.value in eligible:
            return Handoff(policy, tuple(results), recorded.value, recorded), None
        ignored = HandoffChoiceIgnoredError(
            f"handoff choice {recorded.value!r} is not an eligible candidate of {doc.id}; ignored",
            file=recorded.file,
            fix="Record an eligible choice with `devkit workflow answer --request handoff --action accept --value <id>`",
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


def _policy_target(handoff: Handoff, policy: str, doc: WorkflowDocument, unit: UnitRef) -> str:
    """The target chosen without a caller choice: the recorded or automatic one, else why there is none."""
    if handoff.chosen is not None:
        return handoff.chosen
    if policy == "auto":
        raise HandoffUndecidedError(
            f"no candidate of {doc.id} is eligible for automatic handoff",
            *(f"{c.workflow}: {candidate_summary(c.checks) or '-'}" for c in handoff.candidates),
            fix="Satisfy a candidate's `when` checks, or choose one explicitly with --workflow <id>",
        )
    raise HandoffChoiceRequiredError(
        f"handoff from {doc.id} requires a choice (approvals.{HANDOFF_GATE}=ask)",
        *(
            f"{c.workflow}: eligible={str(c.eligible).lower()} recommended={str(c.recommended).lower()}"
            for c in handoff.candidates
        ),
        what_to_report="The eligible and recommended candidates",
        fix=(
            f"Record the user's choice with `devkit workflow answer --unit {unit.rel} --request handoff "
            f"--action accept --value <id>`, then run `devkit workflow handoff --unit {unit.rel}`"
        ),
    )


def _chosen_target(handoff: Handoff, choice: str, doc: WorkflowDocument) -> str:
    """``choice`` when it is an eligible candidate of ``doc``."""
    by_id = {c.workflow: c for c in handoff.candidates}
    candidate = by_id.get(choice)
    if candidate is None:
        raise HandoffInvalidError(
            f"{choice!r} is not a next candidate of {doc.id}", fix=f"Choose one of: {', '.join(by_id)}"
        )
    if not candidate.eligible:
        raise HandoffIneligibleError(
            f"candidate {choice!r} is not eligible: its preconditions do not hold",
            *(f"{k.name}={str(k.satisfied).lower()} {k.detail}".rstrip() for k in candidate.checks),
            fix="Satisfy the candidate's `when` checks first, or choose another candidate",
        )
    return choice


def plan_handoff(ws: Workspace, unit: UnitRef, result: UnitEvaluation, choice: str | None = None) -> HandoffPlan:
    """Decide the target of a handoff, or raise a ``WorkflowError`` saying why there is none.

    ``result`` is the evaluation of ``unit`` against its bound workflow;
    ``choice`` is a candidate named by the caller (``handoff --workflow``).
    Under ``ask`` without a recorded choice it raises
    ``HandoffChoiceRequiredError`` (``INTERACTION``): a person must choose.
    """
    doc = unit.doc
    if result.stage is not None:
        raise HandoffNotReadyError(
            f"unit {unit.rel} has not completed workflow {doc.id}: stage {result.stage.id} is current",
            *(f"unmet={u.name}" for u in result.unmet),
            fix=f"Finish the current stage (`devkit workflow next --unit {unit.rel}`) before handing off",
        )
    if result.hold:
        raise HandoffHeldError(
            f"unit {unit.rel} is held by its envelopes; it is not handed off until they are cleared",
            *result.hold.reasons(),
            fix=f"Resolve each problem (resolution envelope), answer each question (answer envelope) and fix any"
            f" malformed worker envelope, then rerun; `devkit workflow envelope check --unit {unit.rel}` lists them",
        )
    if not doc.next:
        raise HandoffNoneError(
            f"workflow {doc.id} declares no next candidates",
            fix=f"Add a `next` list to {doc.id}, or start a new unit with `devkit workflow new`",
        )
    policy = ws.config.policy(HANDOFF_GATE)
    handoff = result.handoff
    if handoff is None or policy == "off":
        raise HandoffOffError(
            f"handoff is disabled by policy (approvals.{HANDOFF_GATE}=off)",
            fix=f"Set [workflow.approvals].{HANDOFF_GATE} to ask or auto in .devkit/config.toml",
        )
    if choice is None:
        target_id, decision, explicit = _policy_target(handoff, policy, doc, unit), handoff.decision, False
    else:
        target_id, decision, explicit = _chosen_target(handoff, choice, doc), None, True
    target = ws.definition(target_id)
    target_anchor = ws.anchor_for(target)
    if target_anchor != unit.anchor:
        raise HandoffLayoutMismatchError(
            f"workflow {target.id} declares anchor {target_anchor}; unit {unit.rel} is identified by {unit.anchor}",
            fix=f"Relocate the unit into the layout of {target.id} (anchor {target_anchor}), then run `devkit workflow bind --unit <new dir> --workflow {target.id}`",
        )
    return HandoffPlan(unit, doc, target, policy, decision, explicit)


def apply_handoff(plan: HandoffPlan, *, when: date | None = None, by: str = "", note: str = "") -> HandoffOutcome:
    """Rebind the unit to the plan's target and record the finished segment in its history.

    An explicit choice is first recorded as an accepted ``handoff`` decision so
    the audit trail names it; the history entry closes the segment at the
    highest decision sequence. The record is written whole or not at all, and
    when the anchor cannot be rewritten (any exception, ``KeyboardInterrupt``
    included) it is removed again, so a failed handoff leaves the unit as it
    was. A process killed outright between the two writes leaves the record in
    the unchanged segment: an accepted choice of the target, which the next
    ``handoff`` (with or without ``--workflow``) uses.
    """
    unit = plan.unit
    decision = plan.decision
    text = unit.anchor_path.read_text("utf-8")
    written: Decision | None = None
    try:
        if plan.explicit:
            record = new_decision(
                load_decisions(unit.dir),
                HANDOFF_REQUEST,
                "accept",
                workflow=plan.source.id,
                value=plan.target.id,
                note=note,
                by=by,
            )
            decision = written = write_decision(unit.dir, record)
        last = load_decisions(unit.dir).max_seq
        day = (when or date.today()).isoformat()
        binding = unit.binding
        entry = HistoryEntry(plan.source.id, binding.hash or schema_hash(plan.source), day, last)
        history = (*binding.history, entry)
        new_binding = Binding(plan.target.id, schema_hash(plan.target), history)
        replace_text(unit.anchor_path, render_binding(text, new_binding))
    except BaseException:
        if written is not None:
            (unit.dir / written.file).unlink(missing_ok=True)
        raise
    return HandoffOutcome(
        unit=unit.rel,
        source=plan.source.id,
        target=plan.target.id,
        workflow_hash=new_binding.hash,
        policy=plan.policy,
        decision=decision.file if decision else None,
        history=history,
    )
