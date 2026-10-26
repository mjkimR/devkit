"""Workflow envelope value contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit_agt.features.workflow.models.errors import EnvelopeFormatError

WORKER, ANSWER, RESOLUTION = "worker", "answer", "resolution"

CLOSABLE = ("review", "challenger")


WORKER_REF = re.compile(r"worker-\d{2,}\.ya?ml")


@dataclass(frozen=True)
class Finding:
    issue: str = ""
    evidence: str = ""
    failure_condition: str = ""
    suggested_action: str = ""
    resolution: str = "open"
    waiver: str = ""  # why a waived finding is accepted
    severity: str = ""  # optional descriptive label; does not affect checks

    def to_dict(self) -> dict[str, str]:
        out = {"issue": self.issue, "evidence": self.evidence}
        if self.failure_condition:
            out["failure_condition"] = self.failure_condition
        if self.suggested_action:
            out["suggested_action"] = self.suggested_action
        out["resolution"] = self.resolution
        if self.waiver:
            out["waiver"] = self.waiver
        if self.severity:
            out["severity"] = self.severity
        return out


@dataclass(frozen=True)
class Option:
    """One option of a question, shaped like an option of a ``choose`` request."""

    id: str
    description: str = ""
    recommended: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "description": self.description, "recommended": self.recommended}


@dataclass(frozen=True)
class Question:
    """One question of a ``worker`` envelope, shaped like a ``choose`` request."""

    id: str
    title: str
    prompt: str
    context: str = ""
    options: tuple[Option, ...] = ()
    allow_note: bool = True

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"id": self.id, "title": self.title, "prompt": self.prompt}
        if self.context:
            out["context"] = self.context
        out["options"] = [o.to_dict() for o in self.options]
        out["allow_note"] = self.allow_note
        return out


@dataclass(frozen=True)
class Answer:
    """The rewritten answer to one question: the chosen option (``None`` outside the options) and the decision."""

    question: str
    decision: str
    choice: str | None = None
    constraints: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"question": self.question, "choice": self.choice, "decision": self.decision}
        if self.constraints:
            out["constraints"] = list(self.constraints)
        return out


@dataclass(frozen=True)
class Settle:
    """A worker assumption the user settled: its 1-based position in the answered worker's ``assumptions``."""

    assumption: int
    decision: str

    def to_dict(self) -> dict[str, Any]:
        return {"assumption": self.assumption, "decision": self.decision}


@dataclass(frozen=True)
class Problem:
    """An execution problem: its cause, what was tried and the recommended recovery."""

    cause: str
    recovery: str
    attempts: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"cause": self.cause}
        if self.attempts:
            out["attempts"] = list(self.attempts)
        out["recovery"] = self.recovery
        return out


@dataclass(frozen=True)
class Envelope:
    """One envelope. ``file`` and ``seq`` are empty for an envelope not yet written."""

    kind: str
    status: str = "completed"
    file: str = ""  # unit-relative, e.g. envelopes/review-01.yaml
    seq: int = 0
    stage: str = ""
    workflow: str = ""  # the workflow the unit was bound to when written; empty: counts in every segment
    segment: int | None = None  # finished segments (workflow_history entries) when written; None: any segment
    created_at: str = ""  # ISO 8601 UTC, as the authoring commands write it; empty when the file has none
    summary: str = ""
    review: str = ""  # reverify: the review-NN.yaml or challenger-NN.yaml it closes
    findings: tuple[Finding, ...] = ()
    checks: dict[str, str] = field(default_factory=dict)
    diff_base: str = ""
    diff_head: str = ""
    assumptions: tuple[str, ...] = ()
    unverified_areas: tuple[str, ...] = ()
    questions: tuple[Question, ...] = ()  # worker: what the run asks a person
    answers_to: str = ""  # answer: the worker-NN.yaml whose questions it answers
    answers: tuple[Answer, ...] = ()  # answer
    settles: tuple[Settle, ...] = ()  # answer: the answers_to worker's assumptions the user settled
    problem: Problem | None = None  # worker: an execution problem
    resolves: str = ""  # resolution: the worker-NN.yaml whose problem it resolves
    activity_effort: str = ""  # low | medium | high: the effort the run applied

    @property
    def name(self) -> str:
        """The file name (``worker-02.yaml``), which ``answers_to`` and ``resolves`` reference."""
        return Path(self.file).name

    def open_findings(self) -> int:
        return sum(1 for f in self.findings if f.resolution == "open")

    def check_pass(self, key: str) -> bool:
        return self.checks.get(key, "").startswith("PASS")

    def in_segment(self, workflow: str, segment: int) -> bool:
        """Whether the envelope counts in the segment ``segment`` (its index in the history) of ``workflow``.

        An envelope without ``workflow`` counts everywhere; one without ``segment`` in every segment of its workflow.
        """
        if not self.workflow:
            return True
        return self.workflow == workflow and (self.segment is None or self.segment == segment)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "seq": self.seq,
            "kind": self.kind,
            "status": self.status,
            "stage": self.stage,
            "workflow": self.workflow or None,
            "segment": self.segment,
            "summary": self.summary,
            "review": self.review or None,
            "open_findings": self.open_findings(),
            "findings": [f.to_dict() for f in self.findings],
            "checks": dict(self.checks),
            "assumptions": list(self.assumptions),
            "unverified_areas": list(self.unverified_areas),
            "diff_scope": {"base": self.diff_base, "head": self.diff_head}
            if self.diff_head or self.diff_base
            else None,
            "questions": [q.to_dict() for q in self.questions],
            "answers_to": self.answers_to or None,
            "answers": [a.to_dict() for a in self.answers],
            "settles": [s.to_dict() for s in self.settles],
            "problem": self.problem.to_dict() if self.problem else None,
            "resolves": self.resolves or None,
            "activity_effort": self.activity_effort or None,
        }


@dataclass
class Envelopes:
    by_kind: dict[str, list[Envelope]] = field(default_factory=dict)
    errors: list[EnvelopeFormatError] = field(default_factory=list)

    def latest(self, kind: str) -> Envelope | None:
        items = self.by_kind.get(kind)
        return items[-1] if items else None

    def round_state(self, kind: str) -> Envelope | None:
        """The latest ``kind`` round (``review`` or ``challenger``), or the last reverify that references it."""
        latest = self.latest(kind)
        if latest is None:
            return None
        return self.closing_state(latest.name) or latest

    def closing_state(self, name: str) -> Envelope | None:
        """The last reverify whose ``review`` names the round file ``name`` (``challenger-01.yaml``), or ``None``."""
        decider = None
        for rv in self.by_kind.get("reverify", []):
            if rv.review == name:
                decider = rv
        return decider

    def review_state(self) -> Envelope | None:
        """The latest review round, or the last reverify that references it; reverifies of challenger rounds never
        count."""
        return self.round_state("review")

    def deciding(self, kind: str) -> Envelope | None:
        """The envelope a check of ``kind`` reads: the round state of ``review`` and ``challenger``, else the latest."""
        return self.round_state(kind) if kind in CLOSABLE else self.latest(kind)

    def scoped(self, workflow: str, segment: int) -> Envelopes:
        """The envelopes that count in segment ``segment`` of ``workflow`` (``Envelope.in_segment``)."""
        kept = {kind: [e for e in items if e.in_segment(workflow, segment)] for kind, items in self.by_kind.items()}
        return Envelopes({kind: items for kind, items in kept.items() if items}, list(self.errors))

    def all(self) -> list[Envelope]:
        """Every loaded envelope, ordered by file name."""
        return sorted((e for items in self.by_kind.values() for e in items), key=lambda e: e.file)

    def inspection_dict(self, *, details: bool = False) -> dict[str, Any]:
        """Project evidence without repeating historical bodies; validation always reads every file."""
        deciding = {e.file for kind in self.by_kind if kind != "reverify" and (e := self.deciding(kind)) is not None}
        entries = []
        for envelope in self.all():
            data = envelope.to_dict()
            if not details:
                data = {
                    key: data[key]
                    for key in (
                        "file",
                        "seq",
                        "kind",
                        "status",
                        "stage",
                        "workflow",
                        "segment",
                        "review",
                        "open_findings",
                    )
                }
                if envelope.file in deciding:
                    findings = [f.to_dict() for f in envelope.findings if f.resolution == "open"]
                    if findings:
                        data["findings"] = findings
            entries.append(data)
        return {
            "envelopes": entries,
            **self.hold().to_dict(),
            "errors": [error.to_dict() for error in sorted(self.errors, key=lambda error: error.file)],
        }

    def unresolved_problems(self) -> list[Envelope]:
        """The envelopes whose ``problem`` no ``resolution`` names in ``resolves``; any of them blocks the unit.

        Later commits or successful runs do not clear a problem: only a resolution that references it does.
        """
        resolved = {e.resolves for e in self.by_kind.get(RESOLUTION, []) if e.status == "completed"}
        return [e for e in self.all() if e.problem is not None and e.name not in resolved]

    def pending_questions(self) -> list[tuple[Envelope, Question]]:
        """``(worker envelope, question)`` for every question no ``answer`` envelope answers yet.

        The answers to one worker envelope's questions may be spread over several answer envelopes.
        """
        answered: dict[str, set[str]] = {}
        for answer in self.by_kind.get(ANSWER, []):
            if answer.status == "completed":
                answered.setdefault(answer.answers_to, set()).update(a.question for a in answer.answers)
        return [
            (env, q)
            for env in self.by_kind.get(WORKER, [])
            for q in env.questions
            if q.id not in answered.get(env.name, set())
        ]

    def malformed_workers(self) -> list[EnvelopeFormatError]:
        """The malformed ``worker-NN`` files: whether they report a problem or questions cannot be known."""
        return [e for e in self.errors if WORKER_REF.fullmatch(Path(e.file).name)]

    def hold(self) -> Hold:
        """What holds the unit's gates: unresolved problems, unanswered questions and malformed worker envelopes."""
        return Hold(tuple(self.unresolved_problems()), tuple(self.pending_questions()), tuple(self.malformed_workers()))


@dataclass(frozen=True)
class Hold:
    """Why a unit cannot pass a gate or be integrated: it is blocked, or it waits for answers."""

    problems: tuple[Envelope, ...] = ()
    questions: tuple[tuple[Envelope, Question], ...] = ()
    malformed: tuple[EnvelopeFormatError, ...] = ()  # worker files that cannot be read: held, fail closed

    def __bool__(self) -> bool:
        return bool(self.problems or self.questions or self.malformed)

    @property
    def blocked(self) -> bool:
        return bool(self.problems or self.malformed)

    def reasons(self, prefix: str = "") -> list[str]:
        """One line per problem, unanswered question and malformed worker envelope, files prefixed with ``prefix``."""
        lines = [f"{prefix}{e.file}: unresolved problem: {e.problem.cause}" for e in self.problems if e.problem]
        lines += [f"{prefix}{e.file}: unanswered question {q.id}: {q.title}" for e, q in self.questions]
        lines += [f"{prefix}{e.file}: malformed worker envelope: {e.message}" for e in self.malformed]
        return lines

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocked": self.blocked,
            "problems": [{"file": e.file, **(e.problem.to_dict() if e.problem else {})} for e in self.problems],
            "pending_questions": [{"file": e.file, "id": q.id, "title": q.title} for e, q in self.questions],
            "malformed_workers": [{"file": e.file, "reason": e.message} for e in self.malformed],
        }
