"""Authoring ``envelope new``: flag parsing, carrying review findings forward and rendering."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

from devkit.advisory import Actor, Retry
from devkit.workflow.envelope.model import (
    FILE,
    FINDING_KEYS,
    STATUSES,
    Envelope,
    EnvelopeError,
    EnvelopeFormatError,
    Envelopes,
    Finding,
    parse_envelope,
    parse_finding,
)
from devkit.workflow.errors import WorkflowError
from devkit.workflow.git import REVISION

CHECK_VERDICTS = ("PASS", "FAIL", "SKIP")
FROM_LATEST = "latest"


def skeleton(kind: str, stage: str, created_at: str) -> str:
    """A new envelope body that no check accepts until it is filled in."""
    lines = [
        f"kind: {kind}",
        f"stage: {stage or '-'}",
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


class AuthoringError(WorkflowError):
    """A flag combination or value that cannot produce a valid envelope; ``code`` names the condition."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True

    def __init__(self, code: str, message: str, fix: str) -> None:
        super().__init__(message, code=code, fix=fix)


def parse_check_flag(text: str) -> tuple[str, str]:
    """``name=VERDICT[ detail]`` where VERDICT is PASS, FAIL or SKIP."""
    key, sep, value = text.partition("=")
    key = key.strip()
    if not sep or not key or " " in key:
        raise AuthoringError(
            "ENVELOPE_FLAG_INVALID",
            f"--check {text!r} must be name=PASS|FAIL|SKIP[ detail]",
            '--check tests="PASS 14/14"',
        )
    value = value.strip()
    if value.split(" ", 1)[0] not in CHECK_VERDICTS:
        raise AuthoringError(
            "ENVELOPE_FLAG_INVALID",
            f"--check {text!r}: the value must start with {'|'.join(CHECK_VERDICTS)}",
            '--check tests="PASS 14/14"',
        )
    return key, value


def parse_waive_flag(text: str) -> tuple[int, str]:
    """``N=reason``: the 1-based number of a copied finding and why it is waived."""
    number, sep, reason = text.partition("=")
    reason = reason.strip()
    if not sep or not number.strip().isdigit() or not reason:
        raise AuthoringError(
            "ENVELOPE_FLAG_INVALID",
            f"--waive {text!r} must be <finding-number>=<reason>",
            '--waive "2=protocol-wide format kept"',
        )
    return int(number), reason


def parse_resolve_flag(text: str) -> int | None:
    """``N`` (1-based) or ``all`` (returns ``None``)."""
    value = text.strip()
    if value == "all":
        return None
    if not value.isdigit() or int(value) < 1:
        raise AuthoringError(
            "ENVELOPE_FLAG_INVALID",
            f"--resolve {text!r} must be a finding number or all",
            "--resolve 1 --resolve 3, or --resolve all",
        )
    return int(value)


def parse_findings(text: str, kind: str) -> tuple[Finding, ...]:
    """A YAML list of findings; ``issue`` and ``evidence`` are required, ``resolution`` defaults to open."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise AuthoringError(
            "ENVELOPE_FINDINGS_INVALID",
            f"--findings-file: yaml: {exc}",
            "Fix the YAML at the reported line; quote a value that starts with [ { & * ! % @ or ` or contains ': '",
        ) from exc
    if data is None:
        return ()
    if not isinstance(data, list):
        raise AuthoringError(
            "ENVELOPE_FINDINGS_INVALID",
            "--findings-file: expected a YAML list of findings",
            "Write one `- issue: ...` item per finding",
        )
    out: list[Finding] = []
    for i, item in enumerate(data, start=1):
        try:
            finding = parse_finding(item, f"finding {i}")
        except EnvelopeFormatError as exc:
            raise AuthoringError(
                "ENVELOPE_FINDINGS_INVALID",
                f"--findings-file: {exc}",
                f"Write a mapping with only {', '.join(FINDING_KEYS[:5])} (and waiver on a waived finding)",
            ) from exc
        finding = replace(finding, issue=finding.issue.strip(), evidence=finding.evidence.strip())
        if not finding.issue or not finding.evidence:
            raise AuthoringError(
                "ENVELOPE_FINDINGS_INVALID",
                f"--findings-file: finding {i} needs issue and evidence",
                "Add the missing key",
            )
        if kind == "review" and finding.resolution != "open":
            raise AuthoringError(
                "ENVELOPE_FLAG_INVALID",
                f"--findings-file: finding {i}: a review records findings as found (open); close them in a reverify",
                "Drop resolution, or write a reverify envelope",
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
            raise AuthoringError(
                "ENVELOPE_FROM_INVALID",
                "no review envelope to carry forward",
                "Write a review envelope first, or drop --from",
            )
    else:
        path = Path(source)
        path = path if path.is_absolute() else unit_dir / path
        match = FILE.match(path.name)
        if match is None:
            raise AuthoringError(
                "ENVELOPE_FROM_INVALID",
                f"--from {source!r} is not an envelope file name",
                "Use --from latest or envelopes/<review|reverify>-NN.yaml",
            )
        try:
            data = yaml.safe_load(path.read_text("utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise AuthoringError(
                "ENVELOPE_FROM_INVALID",
                f"--from {source}: {exc}",
                "Pass an existing, well-formed review or reverify envelope",
            ) from exc
        parsed = parse_envelope(path.name, int(match.group(2)), match.group(1), data)
        if isinstance(parsed, EnvelopeError):
            raise AuthoringError(
                "ENVELOPE_FROM_INVALID",
                f"--from {source}: {parsed.reason}",
                "Pass a well-formed review or reverify envelope",
            )
        env = parsed
    if env.kind not in {"review", "reverify"}:
        raise AuthoringError(
            "ENVELOPE_FROM_INVALID",
            f"--from must name a review or reverify envelope, not {env.kind}",
            "Use --from latest or a review/reverify file",
        )
    review = env.review if env.kind == "reverify" else Path(env.file).name
    return env.findings, review


def apply_resolutions(
    findings: tuple[Finding, ...], resolve: Iterable[int | None], waive: Mapping[int, str]
) -> tuple[Finding, ...]:
    """Mark copied findings resolved (by number, or every open one for ``None``) or waived with a reason."""
    out = list(findings)
    for n in resolve:
        if n is None:
            out = [replace(f, resolution="resolved") if f.resolution == "open" else f for f in out]
            continue
        if n > len(out):
            raise AuthoringError(
                "ENVELOPE_FROM_INVALID",
                f"--resolve {n}: finding numbers are 1..{len(out)}",
                "Use a number printed by `envelope check`",
            )
        out[n - 1] = replace(out[n - 1], resolution="resolved")
    for n in sorted(waive):
        if n < 1 or n > len(out):
            raise AuthoringError(
                "ENVELOPE_FROM_INVALID",
                f"--waive {n}: finding numbers are 1..{len(out)}",
                "Use a number printed by `envelope check`",
            )
        out[n - 1] = replace(out[n - 1], resolution="waived", waiver=waive[n])
    return tuple(out)


def compose(
    *,
    unit_dir: Path,
    envelopes: Envelopes,
    kind: str,
    stage: str = "",
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
    """Validate the authoring flags of ``envelope new`` and build the envelope to write."""
    if status is None:
        status = STATUSES[0]
    if status not in STATUSES:
        raise AuthoringError(
            "ENVELOPE_STATUS_INVALID",
            f"--status {status!r} not in {'|'.join(STATUSES)}",
            f"Use one of {'|'.join(STATUSES)}",
        )
    resolve_list = [parse_resolve_flag(r) for r in resolve]
    waive_map: dict[int, str] = {}
    for w in waive:
        n, reason = parse_waive_flag(w)
        waive_map[n] = reason
    if source is None and (resolve_list or waive_map):
        raise AuthoringError(
            "ENVELOPE_FROM_INVALID",
            "--resolve/--waive need --from",
            "Add --from latest to carry the findings being closed",
        )
    if kind == "review" and source is not None:
        raise AuthoringError(
            "ENVELOPE_FLAG_INVALID",
            "a review records findings as found; use kind reverify to carry findings forward with --from",
            "Use --kind reverify --from latest",
        )
    if kind == "reverify" and source is None:
        raise AuthoringError(
            "ENVELOPE_FROM_INVALID",
            "reverify needs --from latest (or a review/reverify file) to name the round it closes",
            "Add --from latest",
        )
    if head and not REVISION.match(head):
        raise AuthoringError(
            "ENVELOPE_FLAG_INVALID",
            f"--head {head!r} must be a hexadecimal commit id",
            "Pass --head $(git rev-parse HEAD)",
        )
    check_map: dict[str, str] = {}
    for c in checks:
        key, value = parse_check_flag(c)
        check_map[key] = value
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
    data: dict[str, Any] = {
        "kind": draft.kind,
        "stage": draft.stage or "-",
        "created_at": created_at,
        "status": draft.status,
    }
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
