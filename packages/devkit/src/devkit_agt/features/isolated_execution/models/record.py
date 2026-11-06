"""Persistent execution states and observer exit semantics."""

from __future__ import annotations

from typing import Any

TERMINAL = frozenset({"passed", "failed", "setup_failed", "cancelled", "interrupted"})
NEGATIVE = TERMINAL - {"passed"}
RunRecord = dict[str, Any]


def exit_code(record: RunRecord) -> int:
    """Keep native, execution, observer and cleanup outcomes separate."""
    if record.get("observer") in {"timeout", "unknown"} or (
        record.get("cleanup_requested") and record.get("cleanup", {}).get("outcome") == "refused"
    ):
        return 2
    outcome = record.get("outcome", record.get("phase"))
    if outcome == "unknown":
        return 2
    return 1 if outcome in NEGATIVE else 0
