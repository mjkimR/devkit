"""Decision records: the durable answers to the engine's human requests.

A record lives at ``<unit>/decisions/<NN>-<request>.yaml`` and is never edited
or deleted by the engine. Records name the workflow they were given in; only
records of the current workflow segment (the bound workflow, written after the
last handoff) count. Within that segment the effective decision for a request
is its latest non-``cancel`` record by sequence. Malformed records are
reported, not fatal. See ``docs/workflow/human-interaction.md``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

from devkit.workflow.ids import IDENT_PATTERN, is_ident

DECISIONS_DIR = "decisions"
FILE = re.compile(r"^(\d{2,})-(.+)\.yaml$")
REQUEST_ID = re.compile(rf"^{IDENT_PATTERN}(:[A-Za-z0-9_.-]+)?$")
ACTIONS = ("accept", "decline", "cancel")
KINDS = ("approve", "choose", "feedback", "return")
GATE_PREFIX = "gate:"
CHECK_PREFIX = "check:"
FEEDBACK_PREFIX = "feedback:"
RETURN_PREFIX = "return:"
HANDOFF_REQUEST = "handoff"
REQUIRED_KEYS = ("request", "kind", "action", "workflow", "at")
OPTIONAL_KEYS = ("stage", "value", "note", "by")


def request_slug(request_id: str) -> str:
    return request_id.replace(":", "-")


def expected_kind(request_id: str) -> str | None:
    """The kind a record answering ``request_id`` must have, or ``None`` for an unknown request form."""
    if request_id.startswith((GATE_PREFIX, CHECK_PREFIX)):
        return "approve"
    if request_id == HANDOFF_REQUEST:
        return "choose"
    if request_id.startswith(FEEDBACK_PREFIX):
        return "feedback"
    if request_id.startswith(RETURN_PREFIX):
        return "return"
    return None


def utc_timestamp(now: datetime | None = None) -> str:
    """``YYYY-MM-DDTHH:MM:SSZ`` for ``now`` (default: the current time)."""
    moment = (now or datetime.now(UTC)).astimezone(UTC).replace(microsecond=0)
    return moment.isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Decision:
    file: str  # unit-relative, e.g. decisions/01-gate-integration.yaml
    seq: int
    request: str
    kind: str
    action: str
    workflow: str
    at: str
    stage: str = ""  # the stage the request belonged to, when it had one
    value: Any = None
    note: str = ""
    by: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "request": self.request,
            "kind": self.kind,
            "action": self.action,
            "workflow": self.workflow,
            "stage": self.stage or None,
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
    max_seq: int = 0  # highest sequence of any record file, malformed ones included

    def effective(self, request_id: str) -> Decision | None:
        """Latest record for the request whose action is not ``cancel``."""
        for record in reversed(self.records):
            if record.request == request_id and record.action != "cancel":
                return record
        return None

    def segment(self, workflow: str, since: int) -> Decisions:
        """The records of one workflow segment: given in ``workflow`` with a sequence above ``since``."""
        records = [r for r in self.records if r.workflow == workflow and r.seq > since]
        return Decisions(records, list(self.errors), self.max_seq)

    def next_sequence(self) -> int:
        return self.max_seq + 1


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.isoformat()
        return utc_timestamp(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str) and value.strip():
        return value
    raise ValueError("at: expected an ISO 8601 timestamp")


def parse_record(data: Any, file: str, seq: int) -> Decision:
    """Validate one record; ``file`` is its unit-relative path, whose name must match the request."""
    if not isinstance(data, dict):
        raise ValueError("record must be a mapping")
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise ValueError(f"missing keys {missing}")
    unknown = set(data) - set(REQUIRED_KEYS) - set(OPTIONAL_KEYS)
    if unknown:
        raise ValueError(f"unknown keys {sorted(unknown)}")
    request = data["request"]
    if not isinstance(request, str) or not REQUEST_ID.match(request):
        raise ValueError("invalid request id")
    kind = expected_kind(request)
    if kind is None:
        raise ValueError(f"unknown request {request!r} (gate:, check:, handoff, feedback: or return:)")
    if data["kind"] != kind:
        raise ValueError(f"kind {data['kind']!r} does not match request {request!r} (expected {kind})")
    match = FILE.match(Path(file).name)
    if match is None or match.group(2) != request_slug(request):
        raise ValueError(f"file name must be NN-{request_slug(request)}.yaml for request {request!r}")
    action = data["action"]
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {'|'.join(ACTIONS)}")
    workflow = data["workflow"]
    if not is_ident(workflow):
        raise ValueError("workflow: expected a workflow id")
    value = data.get("value")
    if value is not None:
        if kind in ("approve", "return"):
            raise ValueError(f"a {kind} record takes no value")
        if action != "accept":
            raise ValueError("value is only valid with action accept")
        if not (isinstance(value, str) or (isinstance(value, list) and all(isinstance(v, str) for v in value))):
            raise ValueError("value must be a string or a list of strings")
    elif action == "accept" and kind in ("choose", "feedback"):
        raise ValueError(f"an accepted {kind} record needs a value")
    stage = data.get("stage")
    if stage is not None and not is_ident(stage):
        raise ValueError("stage: expected a stage id")
    if kind == "approve" and not stage:
        raise ValueError("an approve record needs the stage of the request it answers")
    return Decision(
        file=file,
        seq=seq,
        request=request,
        kind=kind,
        action=action,
        workflow=workflow,
        at=_timestamp(data["at"]),
        stage=stage or "",
        value=value,
        note=_text(data.get("note")),
        by=_text(data.get("by")),
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
        out.max_seq = max(out.max_seq, seq)
        rel = f"{DECISIONS_DIR}/{name}"
        try:
            data = yaml.safe_load(path.read_text("utf-8"))
            out.records.append(parse_record(data, rel, seq))
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            out.errors.append(DecisionError(rel, str(exc)))
    return out


def new_decision(
    decisions: Decisions,
    request: str,
    action: str,
    *,
    workflow: str,
    at: str | None = None,
    stage: str = "",
    value: Any = None,
    note: str = "",
    by: str = "",
) -> Decision:
    """The next record for ``request``; its kind follows from the request id."""
    kind = expected_kind(request)
    if kind is None:
        raise ValueError(f"unknown request {request!r}")
    seq = decisions.next_sequence()
    return Decision(
        file=f"{DECISIONS_DIR}/{seq:02d}-{request_slug(request)}.yaml",
        seq=seq,
        request=request,
        kind=kind,
        action=action,
        workflow=workflow,
        at=at or utc_timestamp(),
        stage=stage,
        value=value,
        note=note,
        by=by,
    )


def write_decision(unit_dir: Path, decision: Decision) -> Decision:
    """Write ``decision``; an existing file moves it to the next free sequence. Returns what was written."""
    directory = unit_dir / DECISIONS_DIR
    directory.mkdir(exist_ok=True)
    data: dict[str, Any] = {
        "request": decision.request,
        "kind": decision.kind,
        "action": decision.action,
        "workflow": decision.workflow,
    }
    if decision.stage:
        data["stage"] = decision.stage
    if decision.value is not None:
        data["value"] = decision.value
    if decision.note:
        data["note"] = decision.note
    if decision.by:
        data["by"] = decision.by
    data["at"] = decision.at
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    seq = decision.seq
    while True:
        name = f"{seq:02d}-{request_slug(decision.request)}.yaml"
        try:
            with (directory / name).open("x", encoding="utf-8") as handle:
                handle.write(body)
        except FileExistsError:
            seq += 1
            continue
        return replace(decision, seq=seq, file=f"{DECISIONS_DIR}/{name}")
