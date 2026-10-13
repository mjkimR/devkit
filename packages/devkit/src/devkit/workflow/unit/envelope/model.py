"""``<unit>/envelopes/<kind>-NN.yaml``: the envelope model, loading, validation and review state."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from devkit.workflow.definition.ids import IDENT_HINT, IDENT_PATTERN, is_ident
from devkit.workflow.errors import EnvelopeFormatError, EnvelopeKindError
from devkit.workflow.unit.records import as_text, write_numbered

ENVELOPES_DIR = "envelopes"
FILE = re.compile(rf"({IDENT_PATTERN})-(\d{{2,}})\.ya?ml")
REVIEW_REF = re.compile(r"review-\d{2,}\.ya?ml")
RESOLUTIONS = ("open", "resolved", "waived")
STATUSES = ("completed", "needs_input", "failed")
FINDING_KEYS = ("issue", "evidence", "failure_condition", "suggested_action", "resolution", "waiver")


@dataclass(frozen=True)
class Finding:
    issue: str = ""
    evidence: str = ""
    failure_condition: str = ""
    suggested_action: str = ""
    resolution: str = "open"
    waiver: str = ""  # why a waived finding is accepted

    def to_dict(self) -> dict[str, str]:
        out = {"issue": self.issue, "evidence": self.evidence}
        if self.failure_condition:
            out["failure_condition"] = self.failure_condition
        if self.suggested_action:
            out["suggested_action"] = self.suggested_action
        out["resolution"] = self.resolution
        if self.waiver:
            out["waiver"] = self.waiver
        return out


@dataclass(frozen=True)
class Envelope:
    """One envelope. ``file`` and ``seq`` are empty for an envelope not yet written."""

    kind: str
    status: str = "completed"
    file: str = ""  # unit-relative, e.g. envelopes/review-01.yaml
    seq: int = 0
    stage: str = ""
    created_at: str = ""  # ISO 8601 UTC, as `envelope new` writes it; empty when the file has none
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

    def all(self) -> list[Envelope]:
        """Every loaded envelope, ordered by file name."""
        return sorted((e for items in self.by_kind.values() for e in items), key=lambda e: e.file)


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
    return Finding(
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
    scope = data.get("diff_scope") or {}
    if not isinstance(scope, dict):
        raise EnvelopeFormatError("diff_scope: expected a mapping with base and head")
    return Envelope(
        kind=kind,
        status=status,
        file=rel,
        seq=seq,
        stage=as_text(data.get("stage")),
        created_at=as_text(data.get("created_at")),
        summary=as_text(data.get("summary")),
        review=review,
        findings=findings,
        checks={str(k): as_text(v) for k, v in raw_checks.items()},
        diff_base=as_text(scope.get("base")),
        diff_head=as_text(scope.get("head")),
        assumptions=_text_list(data.get("assumptions"), "assumptions"),
        unverified_areas=_text_list(data.get("unverified_areas"), "unverified_areas"),
    )


def read_envelope(path: Path, rel: str) -> Envelope:
    """Read and validate the envelope file at ``path`` (reported as ``rel``); raises ``EnvelopeFormatError``."""
    match = FILE.fullmatch(path.name)
    if match is None:
        raise EnvelopeFormatError(f"file name must be <kind>-<NN>.yaml with kind matching {IDENT_HINT}", file=rel)
    try:
        data = yaml.safe_load(path.read_text("utf-8"))
    except (OSError, UnicodeError) as exc:
        raise EnvelopeFormatError(str(exc), file=rel) from exc
    except yaml.YAMLError as exc:
        raise EnvelopeFormatError(f"yaml: {exc}", file=rel) from exc
    return parse_envelope(rel, int(match.group(2)), match.group(1), data)


def load_envelopes(unit_dir: Path) -> Envelopes:
    """Read ``unit_dir/envelopes``; a missing directory yields an empty set, a malformed file an entry in ``errors``."""
    out = Envelopes()
    directory = unit_dir / ENVELOPES_DIR
    if not directory.is_dir():
        return out
    for entry in sorted(directory.iterdir()):
        if entry.is_dir() or entry.suffix not in {".yaml", ".yml"}:
            continue
        try:
            parsed = read_envelope(entry, f"{ENVELOPES_DIR}/{entry.name}")
        except EnvelopeFormatError as exc:
            out.errors.append(exc)
            continue
        out.by_kind.setdefault(parsed.kind, []).append(parsed)
    for items in out.by_kind.values():
        items.sort(key=lambda e: e.seq)
    return out


def write_envelope(unit_dir: Path, kind: str, body: str) -> tuple[Path, int]:
    """Write ``body`` as the next ``envelopes/<kind>-NN.yaml``; existing files are never overwritten.

    The sequence follows the highest number of any ``<kind>-NN`` file present,
    malformed ones included. Returns the path and the sequence number. Raises
    ``EnvelopeKindError`` (``ENVELOPE_KIND_INVALID``) for a malformed kind.
    """
    if not is_ident(kind):
        raise EnvelopeKindError(f"kind {kind!r} must match {IDENT_HINT}")
    directory = unit_dir / ENVELOPES_DIR
    taken = (
        [int(m.group(2)) for e in directory.iterdir() if (m := FILE.fullmatch(e.name)) and m.group(1) == kind]
        if directory.is_dir()
        else []
    )
    return write_numbered(directory, max(taken, default=0) + 1, lambda n: f"{kind}-{n:02d}.yaml", body)
