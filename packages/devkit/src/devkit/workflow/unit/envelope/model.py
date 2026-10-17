"""``<unit>/envelopes/<kind>-NN.yaml``: the envelope model, loading, validation, review state and hold state.

Besides reviews, the contract defines the envelopes of delegated work. A ``worker`` envelope is the one record of
a run: the questions it puts to a person in ``questions``, an execution problem in ``problem``. What another actor
does later references it: an ``answer`` records the rewritten answers (``answers_to``), a ``resolution`` closes the
problem (``resolves``). A unit with an unresolved
problem is *blocked*; one with a question not fully answered *waits for answers*. Both hold its gates
(``Envelopes.hold``).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from devkit.workflow.definition.ids import IDENT_HINT, IDENT_PATTERN, is_ident
from devkit.workflow.errors import EnvelopeFormatError, EnvelopeKindError
from devkit.workflow.unit.records import as_text, is_temporary, write_numbered

ENVELOPES_DIR = "envelopes"
FILE = re.compile(rf"({IDENT_PATTERN})-(\d{{2,}})\.ya?ml")
REVIEW_REF = re.compile(r"review-\d{2,}\.ya?ml")
WORKER_REF = re.compile(r"worker-\d{2,}\.ya?ml")
RESOLUTIONS = ("open", "resolved", "waived")
STATUSES = ("completed", "needs_input", "failed")
EFFORTS = ("low", "medium", "high")
FINDING_KEYS = ("issue", "evidence", "failure_condition", "suggested_action", "resolution", "waiver", "severity")
QUESTION_KEYS = ("id", "title", "prompt", "context", "options", "allow_note")
OPTION_KEYS = ("id", "description", "recommended")
ANSWER_KEYS = ("question", "choice", "decision", "constraints")
PROBLEM_KEYS = ("cause", "attempts", "recovery")
TITLE_LIMIT = 40  # a question's title, like a request's
# Kinds whose fields and status the contract fixes, besides review and reverify.
ANSWER, WORKER, RESOLUTION = "answer", "worker", "resolution"


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
    review: str = ""  # reverify: the review-NN.yaml it closes
    findings: tuple[Finding, ...] = ()
    checks: dict[str, str] = field(default_factory=dict)
    diff_base: str = ""
    diff_head: str = ""
    assumptions: tuple[str, ...] = ()
    unverified_areas: tuple[str, ...] = ()
    questions: tuple[Question, ...] = ()  # worker: what the run asks a person
    answers_to: str = ""  # answer: the worker-NN.yaml whose questions it answers
    answers: tuple[Answer, ...] = ()  # answer
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

    def review_state(self) -> Envelope | None:
        """The latest review round, or the last reverify that references it."""
        review = self.latest("review")
        if review is None:
            return None
        decider = review
        name = Path(review.file).name
        for rv in self.by_kind.get("reverify", []):
            if rv.review == name:
                decider = rv
        return decider

    def deciding(self, kind: str) -> Envelope | None:
        return self.review_state() if kind == "review" else self.latest(kind)

    def scoped(self, workflow: str, segment: int) -> Envelopes:
        """The envelopes that count in segment ``segment`` of ``workflow`` (``Envelope.in_segment``)."""
        kept = {kind: [e for e in items if e.in_segment(workflow, segment)] for kind, items in self.by_kind.items()}
        return Envelopes({kind: items for kind, items in kept.items() if items}, list(self.errors))

    def all(self) -> list[Envelope]:
        """Every loaded envelope, ordered by file name."""
        return sorted((e for items in self.by_kind.values() for e in items), key=lambda e: e.file)

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


def _text_list(value: Any, what: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise EnvelopeFormatError(f"{what}: expected a list of strings")
    return tuple(as_text(v) for v in value)


def parse_finding(item: Any, where: str) -> Finding:
    """One finding mapping; raises ``EnvelopeFormatError`` naming ``where``."""
    if not isinstance(item, dict):
        raise EnvelopeFormatError(f"{where}: expected a mapping")
    unknown = set(item) - set(FINDING_KEYS)
    if unknown:
        raise EnvelopeFormatError(f"{where}: unknown keys {sorted(unknown)}")
    resolution = as_text(item.get("resolution")) or "open"
    if resolution not in RESOLUTIONS:
        raise EnvelopeFormatError(f"{where}.resolution {resolution!r} not in {'|'.join(RESOLUTIONS)}")
    severity = item.get("severity", "")
    if "severity" in item and (not isinstance(severity, str) or not severity.strip()):
        raise EnvelopeFormatError(f"{where}.severity: expected a non-empty string")
    return Finding(
        severity=severity,
        issue=as_text(item.get("issue")),
        evidence=as_text(item.get("evidence")),
        failure_condition=as_text(item.get("failure_condition")),
        suggested_action=as_text(item.get("suggested_action")),
        resolution=resolution,
        waiver=as_text(item.get("waiver")),
    )


def parse_envelope(rel: str, seq: int, name_kind: str, data: Any) -> Envelope:
    """Validate one envelope document read from ``rel``; raises ``EnvelopeFormatError`` naming the file."""
    try:
        return _parse_envelope(rel, seq, name_kind, data)
    except EnvelopeFormatError as exc:
        exc.file = rel
        raise


def _parse_envelope(rel: str, seq: int, name_kind: str, data: Any) -> Envelope:
    if not isinstance(data, dict):
        raise EnvelopeFormatError("yaml: expected a mapping")
    kind = as_text(data.get("kind"))
    if not kind:
        raise EnvelopeFormatError("missing required key kind")
    if kind != name_kind:
        raise EnvelopeFormatError(f"kind {kind!r} does not match file name kind {name_kind!r}")
    status = as_text(data.get("status"))
    if not status:
        raise EnvelopeFormatError("missing required key status")
    if status not in STATUSES:
        raise EnvelopeFormatError(f"status {status!r} not in {'|'.join(STATUSES)}")
    review = as_text(data.get("review"))
    if kind == "reverify" and REVIEW_REF.fullmatch(review) is None:
        raise EnvelopeFormatError("reverify needs `review: review-NN.yaml` naming the review round it closes")
    raw_findings = data.get("findings") or []
    if not isinstance(raw_findings, list):
        raise EnvelopeFormatError("findings: expected a list")
    findings = tuple(parse_finding(item, f"findings[{i}]") for i, item in enumerate(raw_findings))
    raw_checks = data.get("checks") or {}
    if not isinstance(raw_checks, dict):
        raise EnvelopeFormatError("checks: expected a mapping")
    workflow = as_text(data.get("workflow"))
    if workflow and not is_ident(workflow):
        raise EnvelopeFormatError(f"workflow {workflow!r} must be a workflow id ({IDENT_HINT})")
    segment = data.get("segment")
    if segment is not None and (not isinstance(segment, int) or isinstance(segment, bool) or segment < 0):
        raise EnvelopeFormatError("segment: expected a non-negative integer")
    scope = data.get("diff_scope") or {}
    if not isinstance(scope, dict):
        raise EnvelopeFormatError("diff_scope: expected a mapping with base and head")
    effort = as_text(data.get("activity_effort"))
    if effort and effort not in EFFORTS:
        raise EnvelopeFormatError(f"activity_effort {effort!r} not in {'|'.join(EFFORTS)}")
    questions = _questions(data.get("questions"))
    answers = _answers(data.get("answers"))
    answers_to = as_text(data.get("answers_to"))
    problem = _problem(data.get("problem"))
    resolves = as_text(data.get("resolves"))
    _check_kind_fields(kind, status, questions, answers, answers_to, problem, resolves, as_text(data.get("summary")))
    if kind == WORKER and as_text(data.get("stage")) in ("", "-"):
        raise EnvelopeFormatError("a worker envelope names the stage its run worked in (stage)")
    return Envelope(
        kind=kind,
        status=status,
        file=rel,
        seq=seq,
        stage=as_text(data.get("stage")),
        workflow=workflow,
        segment=segment,
        created_at=as_text(data.get("created_at")),
        summary=as_text(data.get("summary")),
        review=review,
        findings=findings,
        checks={str(k): as_text(v) for k, v in raw_checks.items()},
        diff_base=as_text(scope.get("base")),
        diff_head=as_text(scope.get("head")),
        assumptions=_text_list(data.get("assumptions"), "assumptions"),
        unverified_areas=_text_list(data.get("unverified_areas"), "unverified_areas"),
        questions=questions,
        answers_to=answers_to,
        answers=answers,
        problem=problem,
        resolves=resolves,
        activity_effort=effort,
    )


def _mapping(item: Any, where: str, keys: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise EnvelopeFormatError(f"{where}: expected a mapping")
    unknown = set(item) - set(keys)
    if unknown:
        raise EnvelopeFormatError(f"{where}: unknown keys {sorted(unknown)}")
    return item


def _required_text(item: dict[str, Any], key: str, where: str) -> str:
    value = as_text(item.get(key)).strip()
    if not value:
        raise EnvelopeFormatError(f"{where}: missing required key {key}")
    return value


def _flag(item: dict[str, Any], key: str, where: str, default: bool) -> bool:
    value = item.get(key, default)
    if not isinstance(value, bool):
        raise EnvelopeFormatError(f"{where}.{key}: expected true or false")
    return value


def _option(item: Any, where: str) -> Option:
    item = _mapping(item, where, OPTION_KEYS)
    option_id = as_text(item.get("id"))
    if not is_ident(option_id):
        raise EnvelopeFormatError(f"{where}.id {option_id!r} must match {IDENT_HINT}")
    return Option(option_id, as_text(item.get("description")), _flag(item, "recommended", where, False))


def parse_question(item: Any, where: str) -> Question:
    """One question mapping; raises ``EnvelopeFormatError`` naming ``where``."""
    item = _mapping(item, where, QUESTION_KEYS)
    question_id = as_text(item.get("id"))
    if not is_ident(question_id):
        raise EnvelopeFormatError(f"{where}.id {question_id!r} must match {IDENT_HINT}")
    title = _required_text(item, "title", where)
    if len(title) > TITLE_LIMIT:
        raise EnvelopeFormatError(f"{where}.title: at most {TITLE_LIMIT} characters")
    raw = item.get("options") or []
    if not isinstance(raw, list):
        raise EnvelopeFormatError(f"{where}.options: expected a list")
    options = tuple(_option(o, f"{where}.options[{i}]") for i, o in enumerate(raw))
    if len({o.id for o in options}) != len(options):
        raise EnvelopeFormatError(f"{where}.options: option ids must be unique")
    if sum(o.recommended for o in options) > 1:
        raise EnvelopeFormatError(f"{where}.options: at most one option is recommended")
    allow_note = _flag(item, "allow_note", where, True)
    if not options and not allow_note:
        raise EnvelopeFormatError(f"{where}: a question without options must allow a note")
    return Question(
        question_id, title, _required_text(item, "prompt", where), as_text(item.get("context")), options, allow_note
    )


def parse_answer(item: Any, where: str) -> Answer:
    """One answer mapping; raises ``EnvelopeFormatError`` naming ``where``."""
    item = _mapping(item, where, ANSWER_KEYS)
    question = as_text(item.get("question"))
    if not is_ident(question):
        raise EnvelopeFormatError(f"{where}.question {question!r} must match {IDENT_HINT}")
    choice = item.get("choice")
    if choice is not None and not is_ident(choice):
        raise EnvelopeFormatError(f"{where}.choice {choice!r} must be an option id or null")
    return Answer(
        question,
        _required_text(item, "decision", where),
        choice,
        _text_list(item.get("constraints"), f"{where}.constraints"),
    )


def parse_problem(value: Any, where: str = "problem") -> Problem:
    """A problem mapping; raises ``EnvelopeFormatError`` naming ``where``."""
    item = _mapping(value, where, PROBLEM_KEYS)
    return Problem(
        _required_text(item, "cause", where),
        _required_text(item, "recovery", where),
        _text_list(item.get("attempts"), f"{where}.attempts"),
    )


def _questions(value: Any) -> tuple[Question, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise EnvelopeFormatError("questions: expected a list")
    questions = tuple(parse_question(item, f"questions[{i}]") for i, item in enumerate(value))
    if len({q.id for q in questions}) != len(questions):
        raise EnvelopeFormatError("questions: question ids must be unique")
    return questions


def _answers(value: Any) -> tuple[Answer, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise EnvelopeFormatError("answers: expected a list")
    answers = tuple(parse_answer(item, f"answers[{i}]") for i, item in enumerate(value))
    if len({a.question for a in answers}) != len(answers):
        raise EnvelopeFormatError("answers: one answer per question")
    return answers


def _problem(value: Any) -> Problem | None:
    return None if value is None else parse_problem(value)


def _check_kind_fields(
    kind: str,
    status: str,
    questions: tuple[Question, ...],
    answers: tuple[Answer, ...],
    answers_to: str,
    problem: Problem | None,
    resolves: str,
    summary: str,
) -> None:
    """The fields each kind carries, and the statuses they allow (``docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md``)."""
    if questions and kind != WORKER:
        raise EnvelopeFormatError("questions: only a worker envelope carries questions")
    if (answers or answers_to) and kind != ANSWER:
        raise EnvelopeFormatError("answers and answers_to: only an answer envelope carries them")
    if resolves and kind != RESOLUTION:
        raise EnvelopeFormatError("resolves: only a resolution envelope carries it")
    if problem is not None and kind != WORKER:
        raise EnvelopeFormatError("problem: only a worker envelope carries a problem")
    if problem is not None and status == "completed":
        raise EnvelopeFormatError("problem: a completed envelope reports no problem; use needs_input or failed")
    if questions and status != "needs_input":
        raise EnvelopeFormatError("questions: a worker envelope that asks has status needs_input")
    if kind == ANSWER:
        if WORKER_REF.fullmatch(answers_to) is None:
            raise EnvelopeFormatError(
                "an answer needs `answers_to: worker-NN.yaml` naming the run whose questions it answers"
            )
        if not answers:
            raise EnvelopeFormatError("an answer envelope needs answers")
        if status != "completed":
            raise EnvelopeFormatError("an answer envelope has status completed")
    elif kind == RESOLUTION:
        if WORKER_REF.fullmatch(resolves) is None:
            raise EnvelopeFormatError("a resolution needs `resolves: worker-NN.yaml` naming the problem it resolves")
        if status != "completed":
            raise EnvelopeFormatError("a resolution envelope has status completed")
        if not summary.strip():
            raise EnvelopeFormatError("a resolution needs a summary of what was done and why it resolves the problem")
    elif kind == WORKER and status == "failed" and problem is None:
        raise EnvelopeFormatError("a failed worker envelope needs a problem (cause, attempts, recovery)")
    elif kind == WORKER and status == "needs_input" and problem is None and not questions:
        raise EnvelopeFormatError("a needs_input worker envelope asks questions or reports a problem")


def reference_error(envelope: Envelope, loaded: Mapping[str, Envelope]) -> str | None:
    """Why ``envelope``'s ``answers_to`` or ``resolves`` does not name a fitting envelope of ``loaded`` (by file
    name), or ``None`` when it does or the envelope references nothing."""
    if envelope.kind == ANSWER:
        target = loaded.get(envelope.answers_to)
        if target is None or not target.questions:
            return f"answers_to {envelope.answers_to!r} names no well-formed worker envelope with questions in the unit"
        questions = {q.id: q for q in target.questions}
        for answer in envelope.answers:
            question = questions.get(answer.question)
            if question is None:
                return f"answers: {answer.question!r} is not a question of {target.name}"
            if answer.choice is not None and answer.choice not in {o.id for o in question.options}:
                return f"answers: {answer.choice!r} is not an option of {target.name} {question.id}"
    if envelope.kind == RESOLUTION:
        target = loaded.get(envelope.resolves)
        if target is None or target.problem is None:
            return f"resolves {envelope.resolves!r} names no well-formed worker envelope with a problem in the unit"
    return None


def _check_references(out: Envelopes) -> None:
    """Move every answer or resolution whose reference does not fit to ``out.errors``: it answers or resolves
    nothing, so the question stays pending and the problem unresolved."""
    loaded = {e.name: e for e in out.all()}
    for kind in (ANSWER, RESOLUTION):
        kept: list[Envelope] = []
        for envelope in out.by_kind.get(kind, []):
            problem = reference_error(envelope, loaded)
            if problem is None:
                kept.append(envelope)
            else:
                out.errors.append(EnvelopeFormatError(problem, file=envelope.file))
        if kind in out.by_kind:
            out.by_kind[kind] = kept
            if not kept:
                del out.by_kind[kind]


def read_envelope(path: Path, rel: str) -> Envelope:
    """Read and validate the envelope file at ``path`` (reported as ``rel``); raises ``EnvelopeFormatError``."""
    if FILE.fullmatch(path.name) is None:
        raise EnvelopeFormatError(f"file name must be <kind>-<NN>.yaml with kind matching {IDENT_HINT}", file=rel)
    try:
        text = path.read_text("utf-8")
    except (OSError, UnicodeError) as exc:
        raise EnvelopeFormatError(str(exc), file=rel) from exc
    return parse_envelope_text(path.name, rel, text)


def parse_envelope_text(name: str, rel: str, text: str) -> Envelope:
    """Validate the envelope file ``name`` (reported as ``rel``) with content ``text``; raises
    ``EnvelopeFormatError``. References to other envelopes are checked by ``collect_envelopes``."""
    match = FILE.fullmatch(name)
    if match is None:
        raise EnvelopeFormatError(f"file name must be <kind>-<NN>.yaml with kind matching {IDENT_HINT}", file=rel)
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise EnvelopeFormatError(f"yaml: {exc}", file=rel) from exc
    return parse_envelope(rel, int(match.group(2)), match.group(1), data)


def is_envelope_name(name: str) -> bool:
    """Whether a file named ``name`` in ``envelopes/`` is loaded as an envelope (temporary files are not)."""
    return not is_temporary(name) and Path(name).suffix in {".yaml", ".yml"}


def collect_envelopes(files: Iterable[tuple[str, Callable[[], str]]]) -> Envelopes:
    """Envelopes from ``(file name, reader)`` pairs of one unit's ``envelopes/`` directory.

    A malformed file is an entry in ``errors``, and so is an answer or resolution whose ``answers_to`` or
    ``resolves`` names no fitting envelope of the same set.
    """
    out = Envelopes()
    for name, read in sorted(files, key=lambda item: item[0]):
        rel = f"{ENVELOPES_DIR}/{name}"
        try:
            text = read()
        except (OSError, UnicodeError) as exc:
            out.errors.append(EnvelopeFormatError(str(exc), file=rel))
            continue
        try:
            parsed = parse_envelope_text(name, rel, text)
        except EnvelopeFormatError as exc:
            exc.stage, exc.workflow = _readable_scope(text)
            out.errors.append(exc)
            continue
        out.by_kind.setdefault(parsed.kind, []).append(parsed)
    for items in out.by_kind.values():
        items.sort(key=lambda e: e.seq)
    _check_references(out)
    return out


def _readable_scope(text: str) -> tuple[str, str]:
    """The ``stage`` and ``workflow`` a malformed envelope still states, when its YAML is a mapping."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return "", ""
    if not isinstance(data, dict):
        return "", ""
    stage, workflow = as_text(data.get("stage")), as_text(data.get("workflow"))
    return ("" if stage == "-" else stage), (workflow if is_ident(workflow) else "")


def load_envelopes(unit_dir: Path) -> Envelopes:
    """Read ``unit_dir/envelopes``; a missing directory yields an empty set, a malformed file an entry in ``errors``."""
    directory = unit_dir / ENVELOPES_DIR
    if not directory.is_dir():
        return Envelopes()
    files = [
        (entry.name, lambda entry=entry: entry.read_text("utf-8"))
        for entry in directory.iterdir()
        if is_envelope_name(entry.name) and not entry.is_dir()
    ]
    return collect_envelopes(files)


def write_envelope(unit_dir: Path, kind: str, body: str) -> tuple[Path, int]:
    """Write ``body`` as the next ``envelopes/<kind>-NN.yaml``; existing files are never overwritten.

    The sequence follows the highest number of any ``<kind>-NN`` file present,
    malformed ones included. Returns the path and the sequence number. Raises
    ``EnvelopeKindError`` (``ENVELOPE_KIND_INVALID``) for a malformed kind.
    """
    if not is_ident(kind):
        raise EnvelopeKindError(f"kind {kind!r} must match {IDENT_HINT}")

    def sequence_of(name: str) -> int | None:
        match = FILE.fullmatch(name)
        return int(match.group(2)) if match and match.group(1) == kind else None

    return write_numbered(unit_dir / ENVELOPES_DIR, 1, lambda n: f"{kind}-{n:02d}.yaml", sequence_of, body)
