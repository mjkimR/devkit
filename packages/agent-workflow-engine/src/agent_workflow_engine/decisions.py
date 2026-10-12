"""Decision records: the durable answers to the engine's human requests.

A record lives at ``<unit>/decisions/<NN>-<request>.yaml`` and is never edited
or deleted by the engine. The effective decision for a request is its latest
non-``cancel`` record by sequence. Malformed records are reported, not fatal.
See ``docs/workflow/human-interaction.md``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DECISIONS_DIR = "decisions"
FILE = re.compile(r"^(\d{2,})-(.+)\.yaml$")
REQUEST_ID = re.compile(r"^[a-z][a-z0-9-]*(:[A-Za-z0-9_.-]+)?$")
ACTIONS = ("accept", "decline", "cancel")
KINDS = ("approve", "choose", "feedback")
FEEDBACK_PREFIX = "feedback:"


def request_slug(request_id: str) -> str:
    return request_id.replace(":", "-")


@dataclass(frozen=True)
class Decision:
    file: str  # unit-relative, e.g. decisions/01-gate-integration.yaml
    seq: int
    request: str
    kind: str
    action: str
    value: Any = None
    note: str = ""
    by: str = ""
    at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "request": self.request,
            "kind": self.kind,
            "action": self.action,
            "value": self.value,
            "note": self.note,
            "by": self.by,
            "at": self.at,
        }


@dataclass(frozen=True)
class DecisionError:
    file: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"file": self.file, "reason": self.reason}


@dataclass
class Decisions:
    records: list[Decision] = field(default_factory=list)  # ascending by seq
    errors: list[DecisionError] = field(default_factory=list)

    def effective(self, request_id: str) -> Decision | None:
        """Latest record for the request whose action is not ``cancel``."""
        for record in reversed(self.records):
            if record.request == request_id and record.action != "cancel":
                return record
        return None

    def latest(self, request_id: str) -> Decision | None:
        for record in reversed(self.records):
            if record.request == request_id:
                return record
        return None

    def next_sequence(self) -> int:
        return (self.records[-1].seq if self.records else 0) + 1


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def parse_record(data: Any, file: str, seq: int) -> Decision:
    if not isinstance(data, dict):
        raise ValueError("record must be a mapping")
    request = data.get("request")
    if not isinstance(request, str) or not REQUEST_ID.match(request):
        raise ValueError("missing or invalid request id")
    kind = data.get("kind")
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {'|'.join(KINDS)}")
    action = data.get("action")
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {'|'.join(ACTIONS)}")
    value = data.get("value")
    if value is not None and not (
        isinstance(value, str) or (isinstance(value, list) and all(isinstance(v, str) for v in value))
    ):
        raise ValueError("value must be a string or a list of strings")
    at = data.get("at")
    if not isinstance(at, str) or not at:
        raise ValueError("missing at timestamp")
    return Decision(
        file=file,
        seq=seq,
        request=request,
        kind=kind,
        action=action,
        value=value,
        note=_text(data.get("note")),
        by=_text(data.get("by")),
        at=at,
    )


def load_decisions(unit_dir: Path) -> Decisions:
    out = Decisions()
    directory = unit_dir / DECISIONS_DIR
    if not directory.is_dir():
        return out
    entries: list[tuple[int, str, Path]] = []
    for path in directory.iterdir():
        match = FILE.match(path.name)
        if path.is_file() and match:
            entries.append((int(match.group(1)), path.name, path))
    for seq, name, path in sorted(entries):
        rel = f"{DECISIONS_DIR}/{name}"
        try:
            data = yaml.safe_load(path.read_text("utf-8"))
            out.records.append(parse_record(data, rel, seq))
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            out.errors.append(DecisionError(rel, str(exc)))
    return out


def write_decision(unit_dir: Path, decision: Decision) -> Path:
    """Write ``decision`` to its file; the file must not exist."""
    directory = unit_dir / DECISIONS_DIR
    directory.mkdir(exist_ok=True)
    path = directory / Path(decision.file).name
    if path.exists():
        raise FileExistsError(path)
    data: dict[str, Any] = {"request": decision.request, "kind": decision.kind, "action": decision.action}
    if decision.value is not None:
        data["value"] = decision.value
    if decision.note:
        data["note"] = decision.note
    if decision.by:
        data["by"] = decision.by
    data["at"] = decision.at
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), "utf-8")
    return path


def new_decision(
    decisions: Decisions, request: str, kind: str, action: str, at: str, value: Any = None, note: str = "", by: str = ""
) -> Decision:
    seq = decisions.next_sequence()
    return Decision(
        file=f"{DECISIONS_DIR}/{seq:02d}-{request_slug(request)}.yaml",
        seq=seq,
        request=request,
        kind=kind,
        action=action,
        value=value,
        note=note,
        by=by,
        at=at,
    )
