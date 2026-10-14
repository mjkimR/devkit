"""Authoring ``envelope new``: flag parsing, carrying review findings forward and rendering."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from devkit.workflow.errors import (
    EnvelopeFindingsError,
    EnvelopeFlagError,
    EnvelopeFormatError,
    EnvelopeFromError,
    EnvelopeStatusError,
)
from devkit.workflow.evaluation.git import is_revision
from devkit.workflow.unit.decisions import load_decisions, utc_timestamp
from devkit.workflow.unit.envelope.model import (
    FINDING_KEYS,
    STATUSES,
    Envelope,
    Envelopes,
    Finding,
    parse_finding,
    read_envelope,
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
        lines.append("review: review-NN.yaml        # the review round this reverify closes")
    if kind in {"review", "reverify", "final-report"}:
        lines.append('diff_scope: { base: "", head: "" }')
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
        data = yaml.safe_load(text)
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
                fix=f"Write a mapping with only {', '.join(FINDING_KEYS[:5])} (and waiver on a waived finding)",
            ) from exc
        finding = replace(finding, issue=finding.issue.strip(), evidence=finding.evidence.strip())
        if not finding.issue or not finding.evidence:
            raise EnvelopeFindingsError(
                f"--findings-file: finding {i} needs issue and evidence",
                fix="Add the missing key",
            )
        if kind == "review" and finding.resolution != "open":
            raise EnvelopeFlagError(
                f"--findings-file: finding {i}: a review records findings as found (open); close them in a reverify",
                fix="Drop resolution, or write a reverify envelope",
            )
        out.append(finding)
    return tuple(out)


def carried_findings(envelopes: Envelopes, source: str, unit_dir: Path) -> tuple[tuple[Finding, ...], str]:
    """Findings copied forward for a reverify, and the ``review-NN.yaml`` round they belong to.

    ``latest`` takes the deciding review state (the latest review round, or the
    last reverify closing it); a path names a review or reverify file.
    """
    if source == FROM_LATEST:
        env = envelopes.review_state()
        if env is None:
            raise EnvelopeFromError(
                "no review envelope to carry forward",
                fix="Write a review envelope first, or drop --from",
            )
    else:
        path = Path(source)
        path = path if path.is_absolute() else unit_dir / path
        try:
            env = read_envelope(path, path.name)
        except EnvelopeFormatError as exc:
            raise EnvelopeFromError(
                f"--from {source}: {exc.message}",
                fix="Use --from latest, or pass an existing, well-formed envelopes/<review|reverify>-NN.yaml",
            ) from exc
    if env.kind not in {"review", "reverify"}:
        raise EnvelopeFromError(
            f"--from must name a review or reverify envelope, not {env.kind}",
            fix="Use --from latest or a review/reverify file",
        )
    review = env.review if env.kind == "reverify" else Path(env.file).name
    return env.findings, review


def _finding_number(flag: str, n: int, count: int) -> int:
    """The 0-based index of finding ``n``; ``EnvelopeFlagError`` when it is outside ``1..count``."""
    if n < 1 or n > count:
        raise EnvelopeFlagError(
            f"{flag} {n}: finding numbers are 1..{count}",
            fix="Use a number printed by `devkit workflow envelope check`",
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
            "a review records findings as found; use kind reverify to carry findings forward with --from",
            fix="Use --kind reverify --from latest",
        )
    if kind == "reverify" and source is None:
        raise EnvelopeFromError(
            "reverify needs --from latest (or a review/reverify file) to name the round it closes",
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
) -> Envelope:
    """Validate the authoring flags of ``envelope new`` and build the envelope to write.

    ``envelopes`` are those of the current segment (``--from latest`` reads
    them); ``workflow`` and ``segment`` scope the new envelope to it.

    Raises an ``AuthoringError`` subclass: ``EnvelopeStatusError``,
    ``EnvelopeFlagError``, ``EnvelopeFromError`` or ``EnvelopeFindingsError``.
    """
    status = STATUSES[0] if status is None else status
    if status not in STATUSES:
        raise EnvelopeStatusError(
            f"--status {status!r} not in {'|'.join(STATUSES)}",
            fix=f"Use one of {'|'.join(STATUSES)}",
        )
    resolve_list = [parse_resolve_flag(r) for r in resolve]
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
    return Envelope(
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
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=10**6)
