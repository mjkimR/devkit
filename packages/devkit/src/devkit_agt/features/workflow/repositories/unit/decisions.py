"""Decision records: the durable answers to the engine's human requests.

A record lives at ``<unit>/decisions/<NN>-<request>.yaml`` and is never edited
or deleted by the engine. Records name the workflow they were given in; only
records of the current workflow segment (the bound workflow, written after the
last handoff) count. Within that segment the effective decision for a request
is its latest non-``cancel`` record by sequence. Malformed records are
reported, not fatal. See ``docs/capabilities/delivery/CAP-DLV-human-interaction.md``.
"""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml
from devkit_core.core.yaml import safe_load

from devkit_agt.features.workflow.models.decision_records import _TIME_OF_DAY as _TIME_OF_DAY
from devkit_agt.features.workflow.models.decision_records import CHECK_PREFIX as CHECK_PREFIX
from devkit_agt.features.workflow.models.decision_records import HANDOFF_REQUEST as HANDOFF_REQUEST
from devkit_agt.features.workflow.models.decision_records import Decision as Decision
from devkit_agt.features.workflow.models.decision_records import Decisions as Decisions
from devkit_agt.features.workflow.models.decision_records import Instant as Instant
from devkit_agt.features.workflow.models.decision_records import record_instant as record_instant
from devkit_agt.features.workflow.models.decisions import ACTIONS as ACTIONS
from devkit_agt.features.workflow.models.errors import DecisionRecordError, RequestUnknownError
from devkit_agt.features.workflow.models.ids import IDENT_PATTERN, is_ident
from devkit_agt.features.workflow.repositories.unit.records import as_text, is_temporary, write_numbered

DECISIONS_DIR = "decisions"
FILE = re.compile(r"(\d{2,})-(.+)\.yaml")
REQUEST_ID = re.compile(rf"{IDENT_PATTERN}(:[A-Za-z0-9_.-]+)?")

KINDS = ("approve", "choose", "feedback", "return")
GATE_PREFIX = "gate:"
FEEDBACK_PREFIX = "feedback:"
RETURN_PREFIX = "return:"
REQUIRED_KEYS = ("request", "kind", "action", "workflow", "at")
OPTIONAL_KEYS = ("stage", "value", "note", "by")


def is_request_id(value: object) -> bool:
    """Whether ``value`` is a request id in full: ``<ident>`` or ``<ident>:<name>``."""
    return isinstance(value, str) and REQUEST_ID.fullmatch(value) is not None


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


# The time of day in an ISO 8601 timestamp: hours and minutes, optionally seconds and a fraction.


def utc_timestamp(now: datetime | None = None, *, after: datetime | None = None) -> str:
    """``YYYY-MM-DDTHH:MM:SS[.ffffff]Z`` for ``now`` (default: the current time), or ``after`` when ``now`` is earlier.

    The fraction is written to the microsecond and omitted when it is zero, which reads back as a whole second.
    """
    moment = (now or datetime.now(UTC)).astimezone(UTC)
    if after is not None and moment < after:
        moment = after.astimezone(UTC)
    return moment.isoformat().replace("+00:00", "Z")


def _timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.isoformat()
        return utc_timestamp(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str) and value.strip():
        return value
    raise DecisionRecordError("at: expected an ISO 8601 timestamp")


def parse_record(data: Any, file: str, seq: int) -> Decision:
    """Validate one record; ``file`` is its unit-relative path, whose name must match the request."""
    if not isinstance(data, dict):
        raise DecisionRecordError("record must be a mapping")
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise DecisionRecordError(f"missing keys {missing}")
    unknown = set(data) - set(REQUIRED_KEYS) - set(OPTIONAL_KEYS)
    if unknown:
        raise DecisionRecordError(f"unknown keys {sorted(unknown)}")
    request = data["request"]
    if not is_request_id(request):
        raise DecisionRecordError("invalid request id")
    kind = expected_kind(request)
    if kind is None:
        raise DecisionRecordError(f"unknown request {request!r} (gate:, check:, handoff, feedback: or return:)")
    if data["kind"] != kind:
        raise DecisionRecordError(f"kind {data['kind']!r} does not match request {request!r} (expected {kind})")
    match = FILE.fullmatch(Path(file).name)
    if match is None or match.group(2) != request_slug(request):
        raise DecisionRecordError(f"file name must be NN-{request_slug(request)}.yaml for request {request!r}")
    action = data["action"]
    if action not in ACTIONS:
        raise DecisionRecordError(f"action must be one of {'|'.join(ACTIONS)}")
    workflow = data["workflow"]
    if not is_ident(workflow):
        raise DecisionRecordError("workflow: expected a workflow id")
    value = data.get("value")
    if value is not None:
        if kind in ("approve", "return"):
            raise DecisionRecordError(f"a {kind} record takes no value")
        if action != "accept":
            raise DecisionRecordError("value is only valid with action accept")
        if not (isinstance(value, str) or (isinstance(value, list) and all(isinstance(v, str) for v in value))):
            raise DecisionRecordError("value must be a string or a list of strings")
    elif action == "accept" and kind in ("choose", "feedback"):
        raise DecisionRecordError(f"an accepted {kind} record needs a value")
    stage = data.get("stage")
    if stage is not None and not is_ident(stage):
        raise DecisionRecordError("stage: expected a stage id")
    if kind == "approve" and not stage:
        raise DecisionRecordError("an approve record needs the stage of the request it answers")
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
        note=as_text(data.get("note")),
        by=as_text(data.get("by")),
    )


def load_decisions(unit_dir: Path) -> Decisions:
    """Every ``decisions/NN-*.yaml`` record of the unit; a malformed one is collected as ``DecisionRecordError``."""
    out = Decisions()
    directory = unit_dir / DECISIONS_DIR
    if not directory.is_dir():
        return out
    entries: list[tuple[int, str, Path]] = []
    for path in directory.iterdir():
        match = None if is_temporary(path.name) else FILE.fullmatch(path.name)
        if match and path.is_file():
            entries.append((int(match.group(1)), path.name, path))
    for seq, name, path in sorted(entries):
        out.max_seq = max(out.max_seq, seq)
        rel = f"{DECISIONS_DIR}/{name}"
        try:
            data = safe_load(path.read_text("utf-8"), source=rel)
            out.records.append(parse_record(data, rel, seq))
        except DecisionRecordError as exc:
            exc.file = rel
            out.errors.append(exc)
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            out.errors.append(DecisionRecordError(str(exc), file=rel))
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
        raise RequestUnknownError(
            f"unknown request {request!r}",
            fix="Use gate:<gate>, check:<name>, handoff, feedback:<target> or return:<stage>",
        )
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
    """Write ``decision`` whole under a sequence no other record holds, whatever its request. Returns what was written.

    The sequence is ``decision.seq``, or the next one above every record file
    present when a concurrent writer took it (``write_numbered``).
    """
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
    slug = request_slug(decision.request)
    path, seq = write_numbered(
        unit_dir / DECISIONS_DIR, decision.seq, lambda n: f"{n:02d}-{slug}.yaml", _sequence_of, body
    )
    return replace(decision, seq=seq, file=f"{DECISIONS_DIR}/{path.name}")


def _sequence_of(name: str) -> int | None:
    """The sequence a ``decisions/`` file name holds, whatever request it answers."""
    match = FILE.fullmatch(name)
    return int(match.group(1)) if match else None
