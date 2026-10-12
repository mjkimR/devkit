"""``<unit>/envelopes/<kind>-NN.yaml``: the envelope model, loading, validation and review state."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from devkit.advisory import Actor, Retry
from devkit.workflow.errors import WorkflowError, input_error
from devkit.workflow.ids import IDENT_PATTERN

ENVELOPES_DIR = "envelopes"
KIND = re.compile(rf"^{IDENT_PATTERN}$")
FILE = re.compile(rf"^({IDENT_PATTERN})-(\d{{2,}})\.ya?ml$")
REVIEW_REF = re.compile(r"^review-\d{2,}\.ya?ml$")
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
    """A malformed envelope file, collected by ``load_envelopes`` instead of raised."""

    file: str
    reason: str
    code: str = "ENVELOPE_INVALID"

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "file": self.file, "reason": self.reason}


class EnvelopeFormatError(WorkflowError):
    """A finding or list inside an envelope document is malformed (``ENVELOPE_INVALID``)."""

    code = "ENVELOPE_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


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

    def all(self) -> list[Envelope]:
        """Every loaded envelope, ordered by file name."""
        return sorted((e for items in self.by_kind.values() for e in items), key=lambda e: e.file)


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _text_list(value: Any, what: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise EnvelopeFormatError(f"{what}: expected a list of strings")
    return tuple(_text(v) for v in value)


def parse_finding(item: Any, where: str) -> Finding:
    """One finding mapping; raises ``EnvelopeFormatError`` naming ``where``."""
    if not isinstance(item, dict):
        raise EnvelopeFormatError(f"{where}: expected a mapping")
    unknown = set(item) - set(FINDING_KEYS)
    if unknown:
        raise EnvelopeFormatError(f"{where}: unknown keys {sorted(unknown)}")
    resolution = _text(item.get("resolution")) or "open"
    if resolution not in RESOLUTIONS:
        raise EnvelopeFormatError(f"{where}.resolution {resolution!r} not in {'|'.join(RESOLUTIONS)}")
    return Finding(
        issue=_text(item.get("issue")),
        evidence=_text(item.get("evidence")),
        failure_condition=_text(item.get("failure_condition")),
        suggested_action=_text(item.get("suggested_action")),
        resolution=resolution,
        waiver=_text(item.get("waiver")),
    )


def parse_envelope(rel: str, seq: int, name_kind: str, data: Any) -> Envelope | EnvelopeError:
    """Validate one envelope document read from ``rel``."""
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
    if status not in STATUSES:
        return EnvelopeError(rel, f"status {status!r} not in {'|'.join(STATUSES)}")
    review = _text(data.get("review"))
    if kind == "reverify" and not REVIEW_REF.match(review):
        return EnvelopeError(rel, "reverify needs `review: review-NN.yaml` naming the review round it closes")
    raw_findings = data.get("findings") or []
    if not isinstance(raw_findings, list):
        return EnvelopeError(rel, "findings: expected a list")
    try:
        findings = tuple(parse_finding(item, f"findings[{i}]") for i, item in enumerate(raw_findings))
        assumptions = _text_list(data.get("assumptions"), "assumptions")
        unverified = _text_list(data.get("unverified_areas"), "unverified_areas")
    except EnvelopeFormatError as exc:
        return EnvelopeError(rel, str(exc))
    raw_checks = data.get("checks") or {}
    if not isinstance(raw_checks, dict):
        return EnvelopeError(rel, "checks: expected a mapping")
    scope = data.get("diff_scope") or {}
    if not isinstance(scope, dict):
        return EnvelopeError(rel, "diff_scope: expected a mapping with base and head")
    return Envelope(
        kind=kind,
        status=status,
        file=rel,
        seq=seq,
        stage=_text(data.get("stage")),
        summary=_text(data.get("summary")),
        review=review,
        findings=findings,
        checks={str(k): _text(v) for k, v in raw_checks.items()},
        diff_base=_text(scope.get("base")),
        diff_head=_text(scope.get("head")),
        assumptions=assumptions,
        unverified_areas=unverified,
    )


def read_envelope(path: Path, rel: str) -> Envelope | EnvelopeError:
    """Read and validate the envelope file at ``path`` (reported as ``rel``)."""
    match = FILE.match(path.name)
    if match is None:
        return EnvelopeError(rel, "file name must be <kind>-<NN>.yaml with kind matching [a-z][a-z0-9-]*")
    try:
        data = yaml.safe_load(path.read_text("utf-8"))
    except (OSError, UnicodeError) as exc:
        return EnvelopeError(rel, str(exc))
    except yaml.YAMLError as exc:
        return EnvelopeError(rel, f"yaml: {exc}")
    return parse_envelope(rel, int(match.group(2)), match.group(1), data)


def load_envelopes(unit_dir: Path) -> Envelopes:
    """Read ``unit_dir/envelopes``; a missing directory yields an empty set."""
    out = Envelopes()
    directory = unit_dir / ENVELOPES_DIR
    if not directory.is_dir():
        return out
    for entry in sorted(directory.iterdir()):
        if entry.is_dir() or entry.suffix not in {".yaml", ".yml"}:
            continue
        parsed = read_envelope(entry, f"{ENVELOPES_DIR}/{entry.name}")
        if isinstance(parsed, EnvelopeError):
            out.errors.append(parsed)
            continue
        out.by_kind.setdefault(parsed.kind, []).append(parsed)
    for items in out.by_kind.values():
        items.sort(key=lambda e: e.seq)
    return out


def write_next(unit_dir: Path, kind: str, body: str) -> tuple[Path, int]:
    """Write ``body`` as the next ``envelopes/<kind>-NN.yaml``; existing files are never overwritten.

    The sequence follows the highest number of any ``<kind>-NN`` file present,
    malformed ones included. Returns the path and the sequence number.
    """
    if not KIND.match(kind):
        raise input_error(
            f"kind {kind!r} must match [a-z][a-z0-9-]*", code="KIND_INVALID", fix="Use a lowercase kind such as review"
        )
    directory = unit_dir / ENVELOPES_DIR
    directory.mkdir(parents=True, exist_ok=True)
    taken = [
        int(m.group(2))
        for entry in directory.iterdir()
        if (m := FILE.match(entry.name)) is not None and m.group(1) == kind
    ]
    seq = max(taken, default=0) + 1
    while True:
        path = directory / f"{kind}-{seq:02d}.yaml"
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(body)
        except FileExistsError:
            seq += 1
            continue
        return path, seq
