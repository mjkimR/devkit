"""Authoring envelopes (``envelope new`` and the kind commands): flag parsing, carrying findings forward, rendering."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from devkit_core.core.yaml import safe_load

from devkit_agt.features.workflow.models.envelope import Answer, Envelope, Envelopes, Finding, Problem, Question, Settle
from devkit_agt.features.workflow.models.errors import (
    EnvelopeFindingsError,
    EnvelopeFlagError,
    EnvelopeFormatError,
    EnvelopeFromError,
    EnvelopeItemsError,
    EnvelopeReferenceError,
    EnvelopeStatusError,
)
from devkit_agt.features.workflow.repositories.git import is_revision
from devkit_agt.features.workflow.repositories.unit.decisions import load_decisions, utc_timestamp
from devkit_agt.features.workflow.services.envelope.model import (
    ANSWER,
    ANSWER_KEYS,
    CLOSABLE,
    EFFORTS,
    FINDING_KEYS,
    QUESTION_KEYS,
    RESOLUTION,
    STATUSES,
    WORKER,
    parse_answer,
    parse_envelope_text,
    parse_finding,
    parse_question,
    read_envelope,
    reference_error,
)

CHECK_VERDICTS = ("PASS", "FAIL", "SKIP")
FROM_LATEST = "latest"


def envelope_timestamp(unit_dir: Path, workflow: str, segment_start: int, now: datetime | None = None) -> str:
    """The ``created_at`` of an envelope written now in the segment of ``workflow`` after decision ``segment_start``.

    It is the current time (``utc_timestamp``), or the end of the segment's
    latest accepted return (``Decisions.returns_end``) when the clock has not
    passed it yet, so a return written just before never voids the envelope.
    """
    returns_end = load_decisions(unit_dir).segment(workflow, segment_start).returns_end()
    return utc_timestamp(now, after=returns_end)


def skeleton(kind: str, stage: str, created_at: str, workflow: str = "", segment: int | None = None) -> str:
    """A new envelope body that no check accepts until it is filled in; ``workflow``/``segment`` scope it."""
    lines = [f"kind: {kind}", f"stage: {stage or repr('-')}"]  # a bare `-` would start a YAML sequence
    if workflow:
        lines.append(f"workflow: {workflow}")
    if segment is not None:
        lines.append(f"segment: {segment}")
    lines += [
        f"created_at: {created_at}",
        "status: needs_input            # completed | needs_input | failed",
        'summary: ""',
        "findings: []",
        "checks: {}",
    ]
    if kind == "reverify":
        lines.append("review: review-NN.yaml        # the review (or challenger-NN.yaml) round this reverify closes")
    if kind in {"review", "reverify", "final-report"}:
        lines.append('diff_scope: { base: "", head: "" }')
    if kind == ANSWER:
        lines.append("answers_to: worker-NN.yaml    # the worker envelope whose questions this answers")
        lines.append("answers: []                   # question, choice, decision, constraints")
        lines.append("# settles: []                 # assumption (1-based position in answers_to), decision")
    if kind == RESOLUTION:
        lines.append("resolves: worker-NN.yaml      # the envelope whose problem this resolves")
    if kind == WORKER:
        lines.append("# questions: []   # needs_input: id, title, prompt, context, options, allow_note")
        lines.append(
            '# problem: { cause: "", attempts: [], recovery: "" }   # needs_input/failed: an execution problem'
        )
    return "\n".join(lines) + "\n"


def parse_check_flag(text: str) -> tuple[str, str]:
    """``name=VERDICT[ detail]`` where VERDICT is PASS, FAIL or SKIP."""
    key, sep, value = text.partition("=")
    key = key.strip()
    if not sep or not key or " " in key:
        raise EnvelopeFlagError(
            f"--check {text!r} must be name=PASS|FAIL|SKIP[ detail]",
            fix='--check tests="PASS 14/14"',
        )
    value = value.strip()
    if value.split(" ", 1)[0] not in CHECK_VERDICTS:
        raise EnvelopeFlagError(
            f"--check {text!r}: the value must start with {'|'.join(CHECK_VERDICTS)}",
            fix='--check tests="PASS 14/14"',
        )
    return key, value


def parse_waive_flag(text: str) -> tuple[int, str]:
    """``N=reason``: the 1-based number of a copied finding and why it is waived."""
    number, sep, reason = text.partition("=")
    reason = reason.strip()
    if not sep or not number.strip().isdigit() or not reason:
        raise EnvelopeFlagError(
            f"--waive {text!r} must be <finding-number>=<reason>",
            fix='--waive "2=protocol-wide format kept"',
        )
    return int(number), reason


def parse_settle_flag(text: str) -> Settle:
    """``N=decision``: the 1-based position of an assumption of the answered worker envelope and the user's decision."""
    number, sep, decision = text.partition("=")
    decision = decision.strip()
    if not sep or not number.strip().isdigit() or int(number) < 1 or not decision:
        raise EnvelopeFlagError(
            f"--settle {text!r} must be <assumption-number>=<decision>",
            fix='--settle "2=Keep the TOML layout"',
        )
    return Settle(int(number), decision)


def parse_resolve_flag(text: str) -> int | None:
    """``N`` (1-based) or ``all`` (returns ``None``)."""
    value = text.strip()
    if value == "all":
        return None
    if not value.isdigit() or int(value) < 1:
        raise EnvelopeFlagError(
            f"--resolve {text!r} must be a finding number or all",
            fix="--resolve 1 --resolve 3, or --resolve all",
        )
    return int(value)


def parse_findings(text: str, kind: str) -> tuple[Finding, ...]:
    """A YAML list of findings; ``issue`` and ``evidence`` are required, ``resolution`` defaults to open."""
    try:
        data = safe_load(text, source="--findings-file")
    except yaml.YAMLError as exc:
        raise EnvelopeFindingsError(
            f"--findings-file: yaml: {exc}",
            fix="Fix the YAML at the reported line; quote a value that starts with [ { & * ! % @ or ` or contains ': '",
        ) from exc
    if data is None:
        return ()
    if not isinstance(data, list):
        raise EnvelopeFindingsError(
            "--findings-file: expected a YAML list of findings",
            fix="Write one `- issue: ...` item per finding",
        )
    out: list[Finding] = []
    for i, item in enumerate(data, start=1):
        try:
            finding = parse_finding(item, f"finding {i}")
        except EnvelopeFormatError as exc:
            raise EnvelopeFindingsError(
                f"--findings-file: {exc}",
                fix=f"Write a mapping with only {', '.join(FINDING_KEYS)} (waiver only on a waived finding)",
            ) from exc
        finding = replace(finding, issue=finding.issue.strip(), evidence=finding.evidence.strip())
        if not finding.issue or not finding.evidence:
            raise EnvelopeFindingsError(
                f"--findings-file: finding {i} needs issue and evidence",
                fix="Add the missing key",
            )
        if kind in CLOSABLE and finding.resolution != "open":
            raise EnvelopeFlagError(
                f"--findings-file: finding {i}: a {kind} records findings as found (open); close them in a reverify",
                fix=f"Drop resolution; close the round with `uv run devkit workflow envelope reverify --from envelopes/{kind}-NN.yaml`",
            )
        out.append(finding)
    return tuple(out)


def _items(text: str, flag: str, keys: tuple[str, ...]) -> list[Any]:
    """The YAML list a ``--questions-file`` or ``--answers-file`` holds."""
    try:
        data = safe_load(text, source=flag)
    except yaml.YAMLError as exc:
        raise EnvelopeItemsError(
            f"{flag}: yaml: {exc}",
            fix="Fix the YAML at the reported line; quote a value that starts with [ { & * ! % @ or ` or contains ': '",
        ) from exc
    if not isinstance(data, list) or not data:
        raise EnvelopeItemsError(
            f"{flag}: expected a non-empty YAML list", fix=f"Write one `- {keys[0]}: ...` item per entry"
        )
    return data


def parse_questions(text: str) -> tuple[Question, ...]:
    """A YAML list of questions (``id``, ``title``, ``prompt``, ``context``, ``options``, ``allow_note``)."""
    out: list[Question] = []
    for i, item in enumerate(_items(text, "--questions-file", QUESTION_KEYS), start=1):
        try:
            out.append(parse_question(item, f"question {i}"))
        except EnvelopeFormatError as exc:
            raise EnvelopeItemsError(
                f"--questions-file: {exc}",
                fix="Write a mapping with id, title (40 characters at most), prompt, and optionally context, options"
                " ({id, description, recommended}) and allow_note",
            ) from exc
    return tuple(out)


def parse_answers(text: str) -> tuple[Answer, ...]:
    """A YAML list of answers (``question``, ``choice``, ``decision``, ``constraints``)."""
    out: list[Answer] = []
    for i, item in enumerate(_items(text, "--answers-file", ANSWER_KEYS), start=1):
        try:
            out.append(parse_answer(item, f"answer {i}"))
        except EnvelopeFormatError as exc:
            raise EnvelopeItemsError(
                f"--answers-file: {exc}",
                fix="Write a mapping with question, choice (an option id or null), decision (one sentence) and"
                " optionally constraints",
            ) from exc
    return tuple(out)


def carried_findings(envelopes: Envelopes, source: str, unit_dir: Path) -> tuple[tuple[Finding, ...], str]:
    """Findings copied forward for a reverify, and the ``review-NN.yaml`` or ``challenger-NN.yaml`` round they belong to.

    ``latest`` takes the deciding review state (the latest review round, or the
    last reverify closing it) of ``envelopes``, which the caller passes without
    the rounds a later return re-opened; a path names a review, challenger or reverify file.
    A named review or challenger round carries its closing state, the last
    reverify of ``envelopes`` naming it, so earlier resolutions and waivers persist.
    """
    if source == FROM_LATEST:
        env = envelopes.review_state()
        if env is None:
            raise EnvelopeFromError(
                "no review envelope to carry forward (a round a later `devkit workflow return` re-opened no longer"
                " counts)",
                fix="Write a review envelope first; close a challenger round with --from envelopes/challenger-NN.yaml",
            )
    else:
        path = Path(source)
        path = path if path.is_absolute() else unit_dir / path
        try:
            env = read_envelope(path, path.name)
        except EnvelopeFormatError as exc:
            raise EnvelopeFromError(
                f"--from {source}: {exc.message}",
                fix="Use --from latest, or pass an existing, well-formed envelopes/<review|challenger|reverify>-NN.yaml",
            ) from exc
    if env.kind == "reconcile-check":
        raise EnvelopeFromError(
            "--from must name a review, challenger or reverify envelope, not reconcile-check",
            fix="Close a reconcile finding with a new reconcile-check envelope instead of a reverify: `uv run devkit workflow"
            " envelope new --unit <dir> --kind reconcile-check --stage living-spec-draft --summary ...` after your"
            " own check, or call the reconcile-reviewer again and record its return the same way",
        )
    if env.kind not in {*CLOSABLE, "reverify"}:
        raise EnvelopeFromError(
            f"--from must name a review, challenger or reverify envelope, not {env.kind}",
            fix="Use --from latest for the review round, or --from envelopes/challenger-NN.yaml for a challenger round",
        )
    if env.kind == "reverify":
        return env.findings, env.review
    review = Path(env.file).name
    closing = envelopes.closing_state(review)
    return (closing or env).findings, review


def _finding_number(flag: str, n: int, count: int) -> int:
    """The 0-based index of finding ``n``; ``EnvelopeFlagError`` when it is outside ``1..count``."""
    if n < 1 or n > count:
        raise EnvelopeFlagError(
            f"{flag} {n}: finding numbers are 1..{count}",
            fix="Use a number printed by `uv run devkit workflow envelope check`",
        )
    return n - 1


def apply_resolutions(
    findings: tuple[Finding, ...], resolve: Iterable[int | None], waive: Mapping[int, str]
) -> tuple[Finding, ...]:
    """Mark copied findings resolved (by number, or every open one for ``None``) or waived with a reason.

    A number outside the copied findings is ``EnvelopeFlagError`` (``ENVELOPE_FLAG_INVALID``).
    """
    out = list(findings)
    for n in resolve:
        if n is None:
            out = [replace(f, resolution="resolved") if f.resolution == "open" else f for f in out]
            continue
        index = _finding_number("--resolve", n, len(out))
        out[index] = replace(out[index], resolution="resolved")
    for n in sorted(waive):
        index = _finding_number("--waive", n, len(out))
        out[index] = replace(out[index], resolution="waived", waiver=waive[n])
    return tuple(out)


def _check_flag_combination(kind: str, source: str | None, closing: bool, head: str) -> None:
    """Refuse flag combinations that cannot produce a valid envelope of ``kind``."""
    if source is None and closing:
        raise EnvelopeFromError(
            "--resolve/--waive need --from", fix="Add --from latest to carry the findings being closed"
        )
    if kind == "review" and source is not None:
        raise EnvelopeFlagError(
            "a review records findings as found; a reverify carries findings forward with --from",
            fix="Use `uv run devkit workflow envelope reverify --from latest`",
        )
    if kind == "reverify" and source is None:
        raise EnvelopeFromError(
            "reverify needs --from latest (or a review, challenger or reverify file) to name the round it closes",
            fix="Add --from latest",
        )
    if head and not is_revision(head):
        raise EnvelopeFlagError(
            f"--head {head!r} must be a hexadecimal commit id",
            fix="Pass --head $(git rev-parse HEAD)",
        )


def compose_envelope(
    *,
    unit_dir: Path,
    envelopes: Envelopes,
    kind: str,
    stage: str = "",
    workflow: str = "",
    segment: int | None = None,
    status: str | None = None,
    summary: str = "",
    assumptions: Iterable[str] = (),
    unverified: Iterable[str] = (),
    checks: Iterable[str] = (),
    base: str = "",
    head: str = "",
    findings_yaml: str | None = None,
    source: str | None = None,
    resolve: Iterable[str] = (),
    waive: Iterable[str] = (),
    questions_yaml: str | None = None,
    answers_to: str = "",
    answers_yaml: str | None = None,
    settle: Iterable[str] = (),
    problem: str = "",
    attempts: Iterable[str] = (),
    recovery: str = "",
    resolves: str = "",
    effort: str = "",
    loaded: Envelopes | None = None,
) -> Envelope:
    """Validate the authoring flags of an envelope command and build the envelope to write.

    ``envelopes`` are those of the current segment (``--from latest`` reads
    them); ``workflow`` and ``segment`` scope the new envelope to it.
    ``loaded`` are all the unit's envelopes, whatever their segment, which
    ``answers_to`` and ``resolves`` must name. The status defaults to
    ``needs_input`` with questions, ``failed`` with only a problem, else
    ``completed``. The result satisfies the envelope contract of its kind.

    Raises an ``AuthoringError`` subclass: ``EnvelopeStatusError``,
    ``EnvelopeFlagError``, ``EnvelopeFromError``, ``EnvelopeFindingsError``,
    ``EnvelopeItemsError`` or ``EnvelopeReferenceError``.
    """
    if status is None:
        status = "needs_input" if questions_yaml is not None else "failed" if problem else STATUSES[0]
    if status not in STATUSES:
        raise EnvelopeStatusError(
            f"--status {status!r} not in {'|'.join(STATUSES)}",
            fix=f"Use one of {'|'.join(STATUSES)}",
        )
    resolve_list = [parse_resolve_flag(r) for r in resolve]
    settle_list = tuple(parse_settle_flag(s) for s in settle)
    waive_map = dict(parse_waive_flag(w) for w in waive)
    _check_flag_combination(kind, source, bool(resolve_list or waive_map), head)
    check_map = dict(parse_check_flag(c) for c in checks)
    findings: tuple[Finding, ...] = ()
    review = ""
    if source is not None:
        findings, review = carried_findings(envelopes, source, unit_dir)
        findings = apply_resolutions(findings, resolve_list, waive_map)
    if findings_yaml is not None:
        findings = findings + parse_findings(findings_yaml, kind)
    attempt_list = tuple(attempts)
    if (attempt_list or recovery) and not problem:
        raise EnvelopeFlagError("--tried and --recovery describe a --problem", fix="Add --problem <cause>")
    if effort and effort not in EFFORTS:
        raise EnvelopeFlagError(
            f"--effort {effort!r} not in {'|'.join(EFFORTS)}", fix=f"Use one of {'|'.join(EFFORTS)}"
        )
    draft = Envelope(
        kind=kind,
        status=status,
        stage=stage,
        workflow=workflow,
        segment=segment,
        summary=summary,
        review=review,
        findings=findings,
        checks=check_map,
        diff_base=base,
        diff_head=head,
        assumptions=tuple(assumptions),
        unverified_areas=tuple(unverified),
        questions=parse_questions(questions_yaml) if questions_yaml is not None else (),
        answers_to=Path(answers_to).name if answers_to else "",
        answers=parse_answers(answers_yaml) if answers_yaml is not None else (),
        settles=settle_list,
        problem=Problem(problem, recovery, attempt_list) if problem else None,
        resolves=Path(resolves).name if resolves else "",
        activity_effort=effort,
    )
    _check_contract(draft, loaded if loaded is not None else envelopes)
    return draft


def _check_contract(draft: Envelope, loaded: Envelopes) -> None:
    """Refuse a draft that its loader would report malformed: the fields and status its kind requires, a complete
    problem, and ``answers_to``/``resolves`` naming a fitting envelope of ``loaded``."""
    name = f"{draft.kind}-01.yaml"
    try:
        parse_envelope_text(name, name, render_envelope(draft, "-"))
    except EnvelopeFormatError as exc:
        raise EnvelopeFlagError(
            f"the envelope would not satisfy the contract of kind {draft.kind}: {exc.message}",
            fix="Pass --stage <the stage the run worked in>"
            if "names the stage" in exc.message
            else _contract_fix(draft.kind),
        ) from exc
    problem = reference_error(draft, {e.name: e for e in loaded.all()})
    if problem is not None:
        raise EnvelopeReferenceError(
            problem,
            fix="Name an envelope `uv run devkit workflow envelope check` lists: --answers-to a worker-NN.yaml with those"
            " questions, options and assumptions, --resolves a worker-NN.yaml with a problem",
        )


def _contract_fix(kind: str) -> str:
    if kind == ANSWER:
        return (
            "Pass --answers-to worker-NN.yaml and --answers-file or --settle (each assumption number once);"
            " an answer envelope has status completed"
        )
    if kind == RESOLUTION:
        return "Pass --resolves worker-NN.yaml and --summary; a resolution has status completed"
    return (
        "Drop the fields this kind does not carry; only a worker envelope carries questions (status needs_input) and"
        " a problem (needs_input or failed), and a failed worker envelope needs --problem and --recovery"
    )


def render_envelope(draft: Envelope, created_at: str) -> str:
    """The YAML body of an envelope to write, in a fixed key order; empty optional keys are omitted."""
    data: dict[str, Any] = {"kind": draft.kind, "stage": draft.stage or "-"}
    if draft.workflow:
        data["workflow"] = draft.workflow
    if draft.segment is not None:
        data["segment"] = draft.segment
    data["created_at"] = created_at
    data["status"] = draft.status
    if draft.review:
        data["review"] = draft.review
    data["summary"] = draft.summary
    data["findings"] = [f.to_dict() for f in draft.findings]
    if draft.assumptions:
        data["assumptions"] = list(draft.assumptions)
    if draft.unverified_areas:
        data["unverified_areas"] = list(draft.unverified_areas)
    data["checks"] = dict(draft.checks)
    if draft.diff_base or draft.diff_head:
        data["diff_scope"] = {"base": draft.diff_base, "head": draft.diff_head}
    if draft.questions:
        data["questions"] = [q.to_dict() for q in draft.questions]
    if draft.answers_to:
        data["answers_to"] = draft.answers_to
    if draft.answers:
        data["answers"] = [a.to_dict() for a in draft.answers]
    if draft.settles:
        data["settles"] = [s.to_dict() for s in draft.settles]
    if draft.problem is not None:
        data["problem"] = draft.problem.to_dict()
    if draft.resolves:
        data["resolves"] = draft.resolves
    if draft.activity_effort:
        data["activity_effort"] = draft.activity_effort
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=10**6)
