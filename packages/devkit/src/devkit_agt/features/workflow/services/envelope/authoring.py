"""Authoring envelopes (``envelope new`` and the kind commands): flag parsing, carrying findings forward, rendering."""

from __future__ import annotations

import json
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
    workflow_command,
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
CHECK_FIX = (
    "Pass each --check as the check name, `=`, and PASS, FAIL or SKIP, optionally followed by a space and a detail"
)


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
            target_files=["--check"],
            fix=CHECK_FIX,
        )
    value = value.strip()
    if value.split(" ", 1)[0] not in CHECK_VERDICTS:
        raise EnvelopeFlagError(
            f"--check {text!r}: the value must start with {'|'.join(CHECK_VERDICTS)}",
            target_files=["--check"],
            fix=CHECK_FIX,
        )
    return key, value


def parse_waive_flag(text: str) -> tuple[int, str]:
    """``N=reason``: the 1-based number of a copied finding and why it is waived."""
    number, sep, reason = text.partition("=")
    reason = reason.strip()
    if not sep or not number.strip().isdigit() or not reason:
        raise EnvelopeFlagError(
            f"--waive {text!r} must be <finding-number>=<reason>",
            target_files=["--waive"],
            fix="Pass each --waive as the carried finding's number, `=`, and why it is waived",
        )
    return int(number), reason


def parse_settle_flag(text: str) -> Settle:
    """``N=decision``: the 1-based position of an assumption of the answered worker envelope and the user's decision."""
    number, sep, decision = text.partition("=")
    decision = decision.strip()
    if not sep or not number.strip().isdigit() or int(number) < 1 or not decision:
        raise EnvelopeFlagError(
            f"--settle {text!r} must be <assumption-number>=<decision>",
            target_files=["--settle"],
            fix="Pass each --settle as the 1-based number of an assumption of the --answers-to envelope, `=`, and the"
            " user's decision",
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
            target_files=["--resolve"],
            fix="Pass each --resolve as a carried finding's number (from 1), or pass --resolve all",
        )
    return int(value)


def parse_findings(text: str, kind: str, unit: str = "") -> tuple[Finding, ...]:
    """A YAML list of findings; ``issue`` and ``evidence`` are required, ``resolution`` defaults to open.

    ``unit`` (workspace-relative) completes the commands the errors name.
    """
    target = ["--findings-file"]
    try:
        data = safe_load(text, source="--findings-file")
    except yaml.YAMLError as exc:
        raise EnvelopeFindingsError(
            f"--findings-file: yaml: {exc}",
            target_files=target,
            fix="Fix the YAML at the reported line; quote a value that starts with [ { & * ! % @ or ` or contains ': '",
        ) from exc
    if data is None:
        return ()
    if not isinstance(data, list):
        raise EnvelopeFindingsError(
            "--findings-file: expected a YAML list of findings",
            target_files=target,
            fix="Write one `- issue: ...` item per finding",
        )
    out: list[Finding] = []
    for i, item in enumerate(data, start=1):
        try:
            finding = parse_finding(item, f"finding {i}")
        except EnvelopeFormatError as exc:
            raise EnvelopeFindingsError(
                f"--findings-file: {exc}",
                target_files=target,
                fix=f"Write a mapping with only {', '.join(FINDING_KEYS)} (waiver only on a waived finding)",
            ) from exc
        finding = replace(finding, issue=finding.issue.strip(), evidence=finding.evidence.strip())
        if not finding.issue or not finding.evidence:
            raise EnvelopeFindingsError(
                f"--findings-file: finding {i} needs issue and evidence",
                target_files=target,
                fix=f"Add issue and evidence to finding {i}",
            )
        if kind in CLOSABLE and finding.resolution != "open":
            raise EnvelopeFlagError(
                f"--findings-file: finding {i}: a {kind} records findings as found (open); close them in a reverify",
                target_files=target,
                fix=f"Drop resolution from finding {i}; {_close_round(kind, unit)}",
            )
        out.append(finding)
    return tuple(out)


def _close_round(kind: str, unit: str) -> str:
    """How the round of a ``review`` or ``challenger`` envelope is closed, as the rest of a fix."""
    if kind == "review" and unit:
        return f"close the round afterwards with `{workflow_command(f'envelope reverify --unit {unit} --from latest')}`"
    return "close the round afterwards with `envelope reverify`, its --from naming the file this command writes"


def _items(text: str, flag: str, keys: tuple[str, ...]) -> list[Any]:
    """The YAML list a ``--questions-file`` or ``--answers-file`` holds."""
    try:
        data = safe_load(text, source=flag)
    except yaml.YAMLError as exc:
        raise EnvelopeItemsError(
            f"{flag}: yaml: {exc}",
            target_files=[flag],
            fix="Fix the YAML at the reported line; quote a value that starts with [ { & * ! % @ or ` or contains ': '",
        ) from exc
    if not isinstance(data, list) or not data:
        raise EnvelopeItemsError(
            f"{flag}: expected a non-empty YAML list",
            target_files=[flag],
            fix=f"Write one `- {keys[0]}: ...` item per entry",
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
                target_files=["--questions-file"],
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
                target_files=["--answers-file"],
                fix="Write a mapping with question, choice (an option id or null), decision (one sentence) and"
                " optionally constraints",
            ) from exc
    return tuple(out)


def _rounds(envelopes: Envelopes) -> tuple[str, ...]:
    """``--from`` naming each file it may name: the review, challenger and reverify envelopes of ``envelopes``."""
    return tuple(f"--from {e.file}" for e in envelopes.all() if e.kind in {*CLOSABLE, "reverify"})


def carried_findings(
    envelopes: Envelopes, source: str, unit_dir: Path, unit: str = ""
) -> tuple[tuple[Finding, ...], str]:
    """Findings copied forward for a reverify, and the ``review-NN.yaml`` or ``challenger-NN.yaml`` round they belong to.

    ``latest`` takes the deciding review state (the latest review round, or the
    last reverify closing it) of ``envelopes``, which the caller passes without
    the rounds a later return re-opened; a path names a review, challenger or reverify file.
    A named review or challenger round carries its closing state, the last
    reverify of ``envelopes`` naming it, so earlier resolutions and waivers persist.
    ``unit`` (workspace-relative) completes the commands the errors name; the files ``--from`` may name are
    their ``[DETAIL]`` lines.
    """
    rounds = _rounds(envelopes)
    named = "Use --from latest, or a --from in [DETAIL]" if rounds else "Use --from latest"
    if source == FROM_LATEST:
        env = envelopes.review_state()
        if env is None:
            raise EnvelopeFromError(
                "no review envelope to carry forward (a round a later `devkit workflow return` re-opened no longer"
                " counts)",
                *rounds,
                target_files=["--from"],
                fix="Write a review envelope first, or pass a --from in [DETAIL]"
                if rounds
                else "Write a review envelope first",
            )
    else:
        path = Path(source)
        path = path if path.is_absolute() else unit_dir / path
        try:
            env = read_envelope(path, path.name)
        except EnvelopeFormatError as exc:
            raise EnvelopeFromError(
                f"--from {source}: {exc.message}", *rounds, target_files=["--from"], fix=named
            ) from exc
    if env.kind == "reconcile-check":
        record = f"envelope new --kind reconcile-check --stage {env.stage}" + (f" --unit {unit}" if unit else "")
        raise EnvelopeFromError(
            "--from must name a review, challenger or reverify envelope, not reconcile-check",
            target_files=["--from"],
            fix=f"Close a reconcile finding with a new reconcile-check envelope instead of a reverify:"
            f" `{workflow_command(record)}` with --summary and --findings-file from your own check or another"
            " reconcile-reviewer call",
        )
    if env.kind not in {*CLOSABLE, "reverify"}:
        raise EnvelopeFromError(
            f"--from must name a review, challenger or reverify envelope, not {env.kind}",
            *rounds,
            target_files=["--from"],
            fix=named,
        )
    if env.kind == "reverify":
        return env.findings, env.review
    review = Path(env.file).name
    closing = envelopes.closing_state(review)
    return (closing or env).findings, review


def _finding_number(flag: str, n: int, findings: list[Finding]) -> int:
    """The 0-based index of finding ``n``; ``EnvelopeFlagError`` when it is outside the carried ``findings``."""
    count = len(findings)
    if n < 1 or n > count:
        raise EnvelopeFlagError(
            f"{flag} {n}: finding numbers are 1..{count}" if count else f"{flag} {n}: the round carries no findings",
            *(f"{i}: {f.resolution} {json.dumps(f.issue, ensure_ascii=False)}" for i, f in enumerate(findings, 1)),
            target_files=[flag],
            fix=f"Pass {flag} the number of a carried finding in [DETAIL]" if count else f"Drop {flag}",
        )
    return n - 1


def apply_resolutions(
    findings: tuple[Finding, ...], resolve: Iterable[int | None], waive: Mapping[int, str]
) -> tuple[Finding, ...]:
    """Mark copied findings resolved (by number, or every open one for ``None``) or waived with a reason.

    A number outside the copied findings is ``EnvelopeFlagError`` (``ENVELOPE_FLAG_INVALID``), whose details number
    the carried findings.
    """
    out = list(findings)
    for n in resolve:
        if n is None:
            out = [replace(f, resolution="resolved") if f.resolution == "open" else f for f in out]
            continue
        index = _finding_number("--resolve", n, out)
        out[index] = replace(out[index], resolution="resolved")
    for n in sorted(waive):
        index = _finding_number("--waive", n, out)
        out[index] = replace(out[index], resolution="waived", waiver=waive[n])
    return tuple(out)


def _check_flag_combination(kind: str, source: str | None, closing: bool, head: str, unit: str = "") -> None:
    """Refuse flag combinations that cannot produce a valid envelope of ``kind``."""
    if source is None and closing:
        raise EnvelopeFromError(
            "--resolve/--waive need --from",
            target_files=["--from"],
            fix="Add --from latest to carry the findings being closed",
        )
    if kind == "review" and source is not None:
        reverify = f"envelope reverify --unit {unit} --from latest" if unit else "envelope reverify --from latest"
        raise EnvelopeFlagError(
            "a review records findings as found; a reverify carries findings forward with --from",
            target_files=["--from"],
            fix=f"Drop --from; carry findings forward with `{workflow_command(reverify)}`",
        )
    if kind == "reverify" and source is None:
        raise EnvelopeFromError(
            "reverify needs --from latest (or a review, challenger or reverify file) to name the round it closes",
            target_files=["--from"],
            fix="Add --from latest",
        )
    if head and not is_revision(head):
        raise EnvelopeFlagError(
            f"--head {head!r} must be a hexadecimal commit id",
            target_files=["--head"],
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
    unit: str = "",
) -> Envelope:
    """Validate the authoring flags of an envelope command and build the envelope to write.

    ``envelopes`` are those of the current segment (``--from latest`` reads
    them); ``workflow`` and ``segment`` scope the new envelope to it.
    ``loaded`` are all the unit's envelopes, whatever their segment, which
    ``answers_to`` and ``resolves`` must name. The status defaults to
    ``needs_input`` with questions, ``failed`` with only a problem, else
    ``completed``. The result satisfies the envelope contract of its kind. ``unit`` (the unit's workspace-relative
    directory) completes the commands the errors name.

    Raises an ``AuthoringError`` subclass: ``EnvelopeStatusError``,
    ``EnvelopeFlagError``, ``EnvelopeFromError``, ``EnvelopeFindingsError``,
    ``EnvelopeItemsError`` or ``EnvelopeReferenceError``.
    """
    if status is None:
        status = "needs_input" if questions_yaml is not None else "failed" if problem else STATUSES[0]
    if status not in STATUSES:
        raise EnvelopeStatusError(
            f"--status {status!r} not in {'|'.join(STATUSES)}",
            target_files=["--status"],
            fix=f"Use one of {'|'.join(STATUSES)}",
        )
    resolve_list = [parse_resolve_flag(r) for r in resolve]
    settle_list = tuple(parse_settle_flag(s) for s in settle)
    waive_map = dict(parse_waive_flag(w) for w in waive)
    _check_flag_combination(kind, source, bool(resolve_list or waive_map), head, unit)
    check_map = dict(parse_check_flag(c) for c in checks)
    findings: tuple[Finding, ...] = ()
    review = ""
    if source is not None:
        findings, review = carried_findings(envelopes, source, unit_dir, unit)
        findings = apply_resolutions(findings, resolve_list, waive_map)
    if findings_yaml is not None:
        findings = findings + parse_findings(findings_yaml, kind, unit)
    attempt_list = tuple(attempts)
    if (attempt_list or recovery) and not problem:
        raise EnvelopeFlagError(
            "--tried and --recovery describe a --problem",
            target_files=["--problem"],
            fix="Add --problem with the cause that --tried and --recovery describe, or drop --tried and --recovery",
        )
    if effort and effort not in EFFORTS:
        raise EnvelopeFlagError(
            f"--effort {effort!r} not in {'|'.join(EFFORTS)}",
            target_files=["--effort"],
            fix=f"Use one of {'|'.join(EFFORTS)}",
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


# The flags an envelope contract violation of a kind comes from.
_CONTRACT_FLAGS = {
    ANSWER: ("--answers-to", "--answers-file", "--settle"),
    RESOLUTION: ("--resolves", "--summary"),
    WORKER: ("--status", "--problem", "--questions-file"),
}


def _check_contract(draft: Envelope, loaded: Envelopes) -> None:
    """Refuse a draft that its loader would report malformed: the fields and status its kind requires, a complete
    problem, and ``answers_to``/``resolves`` naming a fitting envelope of ``loaded``."""
    name = f"{draft.kind}-01.yaml"
    try:
        parse_envelope_text(name, name, render_envelope(draft, "-"))
    except EnvelopeFormatError as exc:
        stage = "names the stage" in exc.message
        raise EnvelopeFlagError(
            f"the envelope would not satisfy the contract of kind {draft.kind}: {exc.message}",
            target_files=["--stage"] if stage else _CONTRACT_FLAGS.get(draft.kind, ("--status",)),
            fix="Pass --stage with the stage the run worked in" if stage else _contract_fix(draft.kind),
        ) from exc
    problem = reference_error(draft, {e.name: e for e in loaded.all()})
    if problem is not None:
        raise _reference_error(draft, problem, loaded)


def _reference_error(draft: Envelope, problem: str, loaded: Envelopes) -> EnvelopeReferenceError:
    """The refusal of an answer or resolution whose reference does not fit; the fitting worker envelopes are its
    ``[DETAIL]`` lines."""
    workers = loaded.by_kind.get(WORKER, [])
    if draft.kind == RESOLUTION:
        fits = [f"--resolves {e.name}" for e in workers if e.problem is not None]
        flag, wanted = "--resolves", "a worker envelope with a problem"
    else:
        fits = [f"--answers-to {e.name}" for e in workers if e.questions or not draft.answers]
        flag = "--settle" if problem.startswith("settles:") else "--answers-to"
        wanted = (
            "a worker envelope whose questions, options and assumptions the answer fits"
            if flag == "--answers-to"
            else "an assumption number the --answers-to envelope records"
        )
    if flag == "--settle":
        fix = "Pass --settle " + wanted
    elif fits:
        fix = f"Pass {flag} {wanted}: one in [DETAIL]"
    else:
        fix = f"Drop this envelope: the unit has no {wanted.removeprefix('a ')}"
    return EnvelopeReferenceError(problem, *fits, target_files=[flag], fix=fix)


def _contract_fix(kind: str) -> str:
    if kind == ANSWER:
        return (
            "Pass --answers-to the worker envelope it answers and --answers-file or --settle (each assumption number"
            " once); an answer envelope has status completed"
        )
    if kind == RESOLUTION:
        return "Pass --resolves the worker envelope whose problem it resolves and --summary; a resolution has status completed"
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
