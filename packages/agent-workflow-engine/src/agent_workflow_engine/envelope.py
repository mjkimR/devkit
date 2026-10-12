"""``<unit>/envelopes/<kind>-NN.yaml``: loading, validation, review state and authoring."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import yaml

ENVELOPES_DIR = "envelopes"
KIND = re.compile(r"^[a-z][a-z0-9-]*$")
FILE = re.compile(r"^([a-z][a-z0-9-]*)-(\d{2})\.ya?ml$")
REVIEW_REF = re.compile(r"^review-\d{2}\.ya?ml$")
RESOLUTIONS = ("open", "resolved", "waived")
STATUSES = ("completed", "needs_input", "failed")
CHECK_VERDICTS = ("PASS", "FAIL", "SKIP")
FROM_LATEST = "latest"


@dataclass(frozen=True)
class Finding:
    issue: str = ""
    evidence: str = ""
    failure_condition: str = ""
    suggested_action: str = ""
    resolution: str = "open"

    def to_dict(self) -> dict[str, str]:
        out = {"issue": self.issue, "evidence": self.evidence}
        if self.failure_condition:
            out["failure_condition"] = self.failure_condition
        if self.suggested_action:
            out["suggested_action"] = self.suggested_action
        out["resolution"] = self.resolution
        return out


@dataclass(frozen=True)
class Envelope:
    file: str  # unit-relative, e.g. envelopes/review-01.yaml
    seq: int
    kind: str
    status: str
    stage: str = ""
    summary: str = ""
    review: str = ""  # reverify: the review-NN.yaml it closes
    findings: tuple[Finding, ...] = ()
    checks: dict[str, str] = field(default_factory=dict)
    diff_base: str = ""
    diff_head: str = ""
    assumptions: tuple[str, ...] = ()
    unverified_areas: tuple[str, ...] = ()

    def open_findings(self) -> int:
        return sum(1 for f in self.findings if f.resolution == "open")

    def check_pass(self, key: str) -> bool:
        return self.checks.get(key, "").startswith("PASS")

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "seq": self.seq,
            "kind": self.kind,
            "status": self.status,
            "stage": self.stage,
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
        }


@dataclass(frozen=True)
class EnvelopeError:
    file: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"file": self.file, "reason": self.reason}


@dataclass
class Envelopes:
    by_kind: dict[str, list[Envelope]] = field(default_factory=dict)
    errors: list[EnvelopeError] = field(default_factory=list)

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

    def next_sequence(self, kind: str) -> int:
        items = self.by_kind.get(kind)
        return (items[-1].seq + 1) if items else 1


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _text_list(value: Any, what: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{what}: expected a list of strings")
    return tuple(_text(v) for v in value)


def _parse(rel: str, seq: int, name_kind: str, data: Any) -> Envelope | EnvelopeError:
    if not isinstance(data, dict):
        return EnvelopeError(rel, "yaml: expected a mapping")
    kind = _text(data.get("kind"))
    if not kind:
        return EnvelopeError(rel, "missing required key kind")
    if kind != name_kind:
        return EnvelopeError(rel, f"kind {kind!r} does not match file name kind {name_kind!r}")
    status = _text(data.get("status"))
    if not status:
        return EnvelopeError(rel, "missing required key status")
    review = _text(data.get("review"))
    if kind == "reverify" and not REVIEW_REF.match(review):
        return EnvelopeError(rel, "reverify needs `review: review-NN.yaml` naming the review round it closes")
    findings: list[Finding] = []
    raw_findings = data.get("findings") or []
    if not isinstance(raw_findings, list):
        return EnvelopeError(rel, "findings: expected a list")
    for i, item in enumerate(raw_findings):
        if not isinstance(item, dict):
            return EnvelopeError(rel, f"findings[{i}]: expected a mapping")
        resolution = _text(item.get("resolution")) or "open"
        if resolution not in RESOLUTIONS:
            return EnvelopeError(rel, f"findings[{i}].resolution {resolution!r} not in {'|'.join(RESOLUTIONS)}")
        findings.append(
            Finding(
                issue=_text(item.get("issue")),
                evidence=_text(item.get("evidence")),
                failure_condition=_text(item.get("failure_condition")),
                suggested_action=_text(item.get("suggested_action")),
                resolution=resolution,
            )
        )
    raw_checks = data.get("checks") or {}
    if not isinstance(raw_checks, dict):
        return EnvelopeError(rel, "checks: expected a mapping")
    scope = data.get("diff_scope") or {}
    if not isinstance(scope, dict):
        return EnvelopeError(rel, "diff_scope: expected a mapping with base and head")
    try:
        assumptions = _text_list(data.get("assumptions"), "assumptions")
        unverified = _text_list(data.get("unverified_areas"), "unverified_areas")
    except ValueError as exc:
        return EnvelopeError(rel, str(exc))
    return Envelope(
        file=rel,
        seq=seq,
        kind=kind,
        status=status,
        stage=_text(data.get("stage")),
        summary=_text(data.get("summary")),
        review=review,
        findings=tuple(findings),
        checks={str(k): _text(v) for k, v in raw_checks.items()},
        diff_base=_text(scope.get("base")),
        diff_head=_text(scope.get("head")),
        assumptions=assumptions,
        unverified_areas=unverified,
    )


def load_envelopes(unit_dir: Path) -> Envelopes:
    """Read ``unit_dir/envelopes``; a missing directory yields an empty set."""
    out = Envelopes()
    directory = unit_dir / ENVELOPES_DIR
    if not directory.is_dir():
        return out
    for entry in sorted(directory.iterdir()):
        if entry.is_dir():
            continue
        rel = f"{ENVELOPES_DIR}/{entry.name}"
        match = FILE.match(entry.name)
        if match is None:
            if entry.suffix in {".yaml", ".yml"}:
                out.errors.append(
                    EnvelopeError(rel, "file name must be <kind>-<NN>.yaml with kind matching [a-z][a-z0-9-]*")
                )
            continue
        try:
            data = yaml.safe_load(entry.read_text("utf-8"))
        except (OSError, UnicodeError) as exc:
            out.errors.append(EnvelopeError(rel, str(exc)))
            continue
        except yaml.YAMLError as exc:
            out.errors.append(EnvelopeError(rel, f"yaml: {exc}"))
            continue
        parsed = _parse(rel, int(match.group(2)), match.group(1), data)
        if isinstance(parsed, EnvelopeError):
            out.errors.append(parsed)
            continue
        out.by_kind.setdefault(parsed.kind, []).append(parsed)
    for items in out.by_kind.values():
        items.sort(key=lambda e: e.seq)
    return out


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


# -- authoring ----------------------------------------------------------------------


class AuthoringError(ValueError):
    """A flag combination or value that cannot produce a valid envelope; ``code`` names the advisory."""

    def __init__(self, code: str, message: str, fix: str) -> None:
        super().__init__(message)
        self.code = code
        self.fix = fix


@dataclass(frozen=True)
class Draft:
    """Everything ``envelope new`` writes beyond the file name."""

    kind: str
    status: str = "completed"
    stage: str = ""
    summary: str = ""
    review: str = ""
    findings: tuple[Finding, ...] = ()
    checks: dict[str, str] = field(default_factory=dict)
    diff_base: str = ""
    diff_head: str = ""
    assumptions: tuple[str, ...] = ()
    unverified_areas: tuple[str, ...] = ()

    def open_findings(self) -> int:
        return sum(1 for f in self.findings if f.resolution == "open")


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
        if not isinstance(item, dict):
            raise AuthoringError(
                "ENVELOPE_FINDINGS_INVALID",
                f"--findings-file: finding {i} must be a mapping",
                "Write issue, evidence and optional failure_condition, suggested_action, resolution",
            )
        unknown = set(item) - {"issue", "evidence", "failure_condition", "suggested_action", "resolution"}
        if unknown:
            raise AuthoringError(
                "ENVELOPE_FINDINGS_INVALID",
                f"--findings-file: finding {i}: unknown keys {sorted(unknown)}",
                "Use only issue, evidence, failure_condition, suggested_action, resolution",
            )
        issue, evidence = _text(item.get("issue")).strip(), _text(item.get("evidence")).strip()
        if not issue or not evidence:
            raise AuthoringError(
                "ENVELOPE_FINDINGS_INVALID",
                f"--findings-file: finding {i} needs issue and evidence",
                "Add the missing key",
            )
        resolution = _text(item.get("resolution")) or "open"
        if resolution not in RESOLUTIONS:
            raise AuthoringError(
                "ENVELOPE_FINDINGS_INVALID",
                f"--findings-file: finding {i} resolution {resolution!r} not in {'|'.join(RESOLUTIONS)}",
                "Use open, resolved or waived",
            )
        if kind == "review" and resolution != "open":
            raise AuthoringError(
                "ENVELOPE_FLAG_INVALID",
                f"--findings-file: finding {i}: a review records findings as found (open); close them in a reverify",
                "Drop resolution, or write a reverify envelope",
            )
        out.append(
            Finding(
                issue=issue,
                evidence=evidence,
                failure_condition=_text(item.get("failure_condition")),
                suggested_action=_text(item.get("suggested_action")),
                resolution=resolution,
            )
        )
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
        parsed = _parse(path.name, int(match.group(2)), match.group(1), data)
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
        out[n - 1] = replace(out[n - 1], resolution="waived", suggested_action=f"waived: {waive[n]}")
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
) -> Draft:
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
    return Draft(
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


def render_draft(draft: Draft, created_at: str) -> str:
    """The YAML body in a fixed key order; empty optional keys are omitted."""
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
