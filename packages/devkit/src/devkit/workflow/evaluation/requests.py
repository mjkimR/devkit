"""Human requests: the open questions a unit puts to a person (see docs/workflow/human-interaction.md)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from devkit.workflow.definition.checks import GATE_PREFIX, CheckClass, CheckResult
from devkit.workflow.definition.definition import StageDefinition, WorkflowDocument
from devkit.workflow.unit.decisions import CHECK_PREFIX, HANDOFF_REQUEST, Decision

if TYPE_CHECKING:
    from devkit.workflow.handoff import Handoff

TITLE_LIMIT = 40


@dataclass(frozen=True)
class Option:
    id: str
    description: str = ""
    recommended: bool = False
    eligible: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "recommended": self.recommended,
            "eligible": self.eligible,
        }


@dataclass(frozen=True)
class Target:
    type: str  # gate | check | handoff
    name: str
    stage: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "name": self.name, "stage": self.stage}


@dataclass(frozen=True)
class Request:
    """An open question for a person."""

    id: str
    kind: str  # approve | choose
    title: str
    prompt: str
    target: Target
    options: tuple[Option, ...] = ()
    allow_note: bool = True
    declined: Decision | None = None
    answer: str = "record"  # gate requests: record (devkit workflow answer) or given (next --given <gate>)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "prompt": self.prompt,
            "target": self.target.to_dict(),
            "options": [o.to_dict() for o in self.options],
            "allow_note": self.allow_note,
            "answer": self.answer,
            "declined": (
                {"file": self.declined.file, "note": self.declined.note, "at": self.declined.at}
                if self.declined
                else None
            ),
        }


DeclinedLookup = Callable[[str], Decision | None]


def stage_requests(
    doc: WorkflowDocument, stage: StageDefinition, unmet: list[CheckResult], declined: DeclinedLookup
) -> list[Request]:
    """Approve requests for the unmet gate and human checks of the current stage."""
    requests: list[Request] = []
    for u in unmet:
        if stage.gate and u.name == GATE_PREFIX + stage.gate:
            rid = GATE_PREFIX + stage.gate
            requests.append(
                Request(
                    id=rid,
                    kind="approve",
                    title=f"Approve {stage.gate}"[:TITLE_LIMIT],
                    prompt=f"Approve gate {stage.gate!r} to finish stage {stage.id!r} of {doc.id}.",
                    target=Target("gate", stage.gate, stage.id),
                    declined=declined(rid),
                    answer=doc.gate_answer(stage.gate),
                )
            )
        elif u.class_ == CheckClass.HUMAN and not u.satisfied:
            rid = CHECK_PREFIX + u.name
            requests.append(
                Request(
                    id=rid,
                    kind="approve",
                    title=f"Confirm {u.name}"[:TITLE_LIMIT],
                    prompt=f"Confirm human check {u.name!r} for stage {stage.id!r} of {doc.id}.",
                    target=Target("check", u.name, stage.id),
                    declined=declined(rid),
                )
            )
    return requests


def candidate_summary(checks: tuple[CheckResult, ...]) -> str:
    """``name=true|false`` for each ``when`` check of a candidate."""
    return " ".join(f"{k.name}={str(k.satisfied).lower()}" for k in checks)


def handoff_request(doc: WorkflowDocument, handoff: Handoff, declined: DeclinedLookup) -> Request:
    """The single-select ``choose`` request for the next workflow of a completed unit."""
    options = tuple(
        Option(c.workflow, candidate_summary(c.checks), c.recommended, c.eligible) for c in handoff.candidates
    )
    return Request(
        id=HANDOFF_REQUEST,
        kind="choose",
        title="Choose next workflow",
        prompt=f"Workflow {doc.id} is complete; choose the workflow that continues this unit.",
        target=Target("handoff", doc.id, None),
        options=options,
        declined=declined(HANDOFF_REQUEST),
    )
