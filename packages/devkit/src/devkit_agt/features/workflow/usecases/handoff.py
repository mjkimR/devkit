"""Handing a completed unit to the next workflow: candidate evaluation, choosing, and rebinding."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any

from devkit_dist.features.project.models.invocation import devkit_command

from devkit_agt.features.workflow.models.binding import Binding, HistoryEntry
from devkit_agt.features.workflow.models.checks import CheckResult
from devkit_agt.features.workflow.models.decision_records import HANDOFF_REQUEST, Decision
from devkit_agt.features.workflow.models.definition import HANDOFF_GATE, WorkflowDocument
from devkit_agt.features.workflow.models.errors import (
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
    workflow_command,
)
from devkit_agt.features.workflow.models.handoff import CandidateResult as CandidateResult
from devkit_agt.features.workflow.models.handoff import Handoff as Handoff
from devkit_agt.features.workflow.models.requests import candidate_summary
from devkit_agt.features.workflow.repositories.unit.binding import render_binding, replace_text
from devkit_agt.features.workflow.repositories.unit.decisions import load_decisions, new_decision, write_decision

if TYPE_CHECKING:
    from devkit_agt.features.workflow.models.results import UnitEvaluation
    from devkit_agt.features.workflow.usecases.workspace import UnitRef, Workspace


def evaluate_handoff(
    doc: WorkflowDocument,
    eval_ref: Callable[[str], CheckResult],
    recorded: Decision | None,
    policy: str,
    *,
    unit: str = "",
) -> tuple[Handoff | None, HandoffChoiceIgnoredError | None]:
    """Evaluate every ``next`` candidate and apply the handoff policy.

    ``recorded`` is the effective accepted ``handoff`` record of the current
    segment. A recorded choice that is not an eligible candidate is ignored
    and returned as a ``HandoffChoiceIgnoredError`` (``HANDOFF_CHOICE_IGNORED``),
    whose fix and details are the commands that record an eligible choice for ``unit`` (workspace-relative).
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
        choices = choice_commands(unit, [c.workflow for c in results if c.eligible])
        ignored = HandoffChoiceIgnoredError(
            f"handoff choice {recorded.value!r} is not an eligible candidate of {doc.id}; ignored",
            *choices.details,
            file=recorded.file,
            fix=choices.fix
            if unit
            else f"Record an eligible choice with `{devkit_command('workflow answer --request handoff')}`",
        )
    chosen = next((c.workflow for c in results if c.eligible), None) if policy == "auto" else None
    return Handoff(policy, tuple(results), chosen), ignored


@dataclass(frozen=True)
class ChoiceCommands:
    """How a handoff choice is recorded: ``fix`` (the one command, or the listing), ``details`` (one per candidate)."""

    fix: str
    details: tuple[str, ...]


def choice_commands(unit: str, eligible: list[str]) -> ChoiceCommands:
    """The ``answer`` command recording each eligible candidate of ``unit``: ``fix`` is the command itself for a single
    candidate, else ``next``, which lists them; with none eligible, ``next`` shows what each lacks."""
    commands = tuple(
        workflow_command(f"answer --unit {unit} --request handoff --action accept --value {wid}") for wid in eligible
    )
    fix = commands[0] if len(commands) == 1 else workflow_command(f"next --unit {unit}")
    return ChoiceCommands(fix, commands)


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
    policy: str
    decision: str | None
    history: tuple[HistoryEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit": self.unit,
            "from": self.source,
            "to": self.target,
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
            fix=f"Satisfy the `when` checks of a candidate in [DETAIL], then run"
            f" `{workflow_command(f'handoff --unit {unit.rel}')}`",
        )
    eligible = [c.workflow for c in handoff.candidates if c.eligible]
    recommended = [c.workflow for c in handoff.candidates if c.eligible and c.recommended]
    choices = choice_commands(unit.rel, eligible)
    raise HandoffChoiceRequiredError(
        f"handoff from {doc.id} requires a choice (approvals.{HANDOFF_GATE}=ask); after the user's answer run"
        f" `{workflow_command(f'handoff --unit {unit.rel}')}`",
        *choices.details,
        what_to_report=f"Which workflow continues {unit.rel}: eligible {', '.join(eligible) or 'none'};"
        f" recommended {', '.join(recommended) or 'none'}",
        fix=choices.fix,
    )


def _chosen_target(handoff: Handoff, choice: str, doc: WorkflowDocument) -> str:
    """``choice`` when it is an eligible candidate of ``doc``."""
    by_id = {c.workflow: c for c in handoff.candidates}
    candidate = by_id.get(choice)
    if candidate is None:
        raise HandoffInvalidError(
            f"{choice!r} is not a next candidate of {doc.id}",
            target_files=["--workflow"],
            fix=f"Pass --workflow one of: {', '.join(by_id)}",
        )
    if not candidate.eligible:
        raise HandoffIneligibleError(
            f"candidate {choice!r} is not eligible: its preconditions do not hold",
            *(f"{k.name}={'yes' if k.satisfied else 'no'} {k.detail}".rstrip() for k in candidate.checks),
            target_files=["--workflow"],
            fix="Satisfy the candidate's `when` checks in [DETAIL] first, or pass --workflow another candidate",
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
            what_to_report=f"{unit.rel} is at stage {result.stage.id} of {doc.id}, so it cannot be handed off yet;"
            " ask whether to finish that stage first",
            fix=workflow_command(f"next --unit {unit.rel}"),
        )
    if result.hold:
        raise HandoffHeldError(
            f"unit {unit.rel} is held by its envelopes; it is not handed off until they are cleared",
            *result.hold.reasons(),
            what_to_report="The unresolved problems and unanswered questions in [DETAIL]: the user answers each"
            " question (answer envelope) and decides each recovery (resolution envelope) before the handoff",
            fix=workflow_command(f"envelope check --unit {unit.rel}"),
        )
    if not doc.next:
        raise HandoffNoneError(
            f"workflow {doc.id} declares no next candidates",
            fix=f"Nothing follows {doc.id}: the unit is finished; start further work as a new unit, or add a `next`"
            f" list to {doc.id}",
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
            fix=f"Relocate the unit into the layout of {target.id} (anchor {target_anchor}), then bind the unit at its new"
            f" directory to {target.id} with the bind command's --workflow",
        )
    return HandoffPlan(unit, doc, target, policy, decision, explicit)


def apply_handoff(plan: HandoffPlan, *, when: date | None = None, by: str = "") -> HandoffOutcome:
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
                by=by,
            )
            decision = written = write_decision(unit.dir, record)
        last = load_decisions(unit.dir).max_seq
        day = (when or date.today()).isoformat()
        binding = unit.binding
        entry = HistoryEntry(plan.source.id, day, last)
        history = (*binding.history, entry)
        new_binding = Binding(plan.target.id, history)
        replace_text(unit.anchor_path, render_binding(text, new_binding))
    except BaseException:
        if written is not None:
            (unit.dir / written.file).unlink(missing_ok=True)
        raise
    return HandoffOutcome(
        unit=unit.rel,
        source=plan.source.id,
        target=plan.target.id,
        policy=plan.policy,
        decision=decision.file if decision else None,
        history=history,
    )
