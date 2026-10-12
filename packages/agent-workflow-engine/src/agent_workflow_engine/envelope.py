"""``<unit>/envelopes/<kind>-NN.yaml``: loading, validation and review state."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ENVELOPES_DIR = "envelopes"
KIND = re.compile(r"^[a-z][a-z0-9-]*$")
FILE = re.compile(r"^([a-z][a-z0-9-]*)-(\d{2})\.ya?ml$")
REVIEW_REF = re.compile(r"^review-\d{2}\.ya?ml$")
RESOLUTIONS = ("open", "resolved", "waived")
STATUSES = ("completed", "needs_input", "failed")


@dataclass(frozen=True)
class Finding:
    issue: str = ""
    evidence: str = ""
    failure_condition: str = ""
    suggested_action: str = ""
    resolution: str = "open"


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
            "checks": dict(self.checks),
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
