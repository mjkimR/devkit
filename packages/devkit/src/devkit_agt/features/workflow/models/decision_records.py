"""Workflow decision_records value contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from devkit_agt.features.workflow.models.decisions import ACTIONS as ACTIONS
from devkit_agt.features.workflow.models.errors import DecisionRecordError

CHECK_PREFIX = "check:"


HANDOFF_REQUEST = "handoff"


_TIME_OF_DAY = re.compile(r"[T ]\d{2}:\d{2}(?P<seconds>:\d{2}(?:[.,](?P<fraction>\d+))?)?")


@dataclass(frozen=True)
class Instant:
    """When a record was written, as precisely as its timestamp tells: at or after ``start`` and before ``end``.

    ``2026-10-12T09:30:00Z`` spans that whole second; ``2026-10-12T09:30:00.250000Z`` one microsecond.
    """

    start: datetime
    end: datetime


def record_instant(text: str) -> Instant | None:
    """The ``Instant`` an ISO 8601 timestamp with ``Z`` or an offset names; ``None`` when missing or malformed."""
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    if moment.tzinfo is None:
        return None
    match = _TIME_OF_DAY.search(text)
    if match is not None and match["seconds"] is None:
        width = timedelta(minutes=1)
    elif match is not None and match["fraction"] is not None:
        width = timedelta(microseconds=10 ** max(0, 6 - len(match["fraction"])))
    else:
        width = timedelta(seconds=1)
    return Instant(moment, moment + width)


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


@dataclass
class Decisions:
    records: list[Decision] = field(default_factory=list)  # ascending by seq
    errors: list[DecisionRecordError] = field(default_factory=list)
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

    def returns_end(self) -> datetime | None:
        """The end of the latest accepted ``return`` record's ``Instant``; ``None`` without one.

        Anything stamped at or after it was written after every return of these records.
        """
        ends = [
            instant.end
            for r in self.records
            if r.kind == "return" and r.action == "accept" and (instant := record_instant(r.at)) is not None
        ]
        return max(ends, default=None)
