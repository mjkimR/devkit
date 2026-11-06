"""Persistent execution states and observer exit semantics."""

from __future__ import annotations

from typing import Any

TERMINAL = frozenset({"passed", "failed", "setup_failed", "cancelled", "interrupted"})
NEGATIVE = TERMINAL - {"passed"}
RunRecord = dict[str, Any]


def exit_code(record: RunRecord) -> int:
    """Keep native, execution, observer and cleanup outcomes separate."""
    if record.get("observer") in {"timeout", "unknown"} or (
        record.get("cleanup_requested")
        and record.get("cleanup", {}).get("outcome") in {"refused", "in_progress", "unfinished"}
    ):
        return 2
    outcome = record.get("outcome", record.get("phase"))
    if outcome == "unknown":
        return 2
    return 1 if outcome in NEGATIVE else 0


def public_record(record: RunRecord, *, compact: bool = False) -> RunRecord:
    """Project bounded decision fields while complete ownership remains on disk."""
    fields = (
        "run_id",
        "sha",
        "phase",
        "outcome",
        "exit_code",
        "created_at",
        "completed_at",
        "checkout",
        "log",
        "result",
    )
    if not compact:
        fields += (
            "base",
            "environment",
            "runtime",
            "started_at",
            "command_started_at",
            "observer",
            "observer_code",
            "cleanup_requested",
            "detail",
            "resources",
            "tail",
            "lines",
        )
    result: RunRecord = {key: record[key] for key in fields if key in record}
    truncated: list[str] = []
    for key, value in list(result.items()):
        if isinstance(value, str) and len(value) > 2048:
            result[key] = value[:2048]
            truncated.append(key)
    if record.get("cleanup") and not compact:
        cleanup = record["cleanup"]
        result["cleanup"] = {
            key: str(cleanup[key])[:1024] if isinstance(cleanup[key], str) else cleanup[key]
            for key in ("outcome", "code", "detail", "completed_at")
            if key in cleanup
        }
        if len(str(cleanup.get("detail", ""))) > 1024:
            truncated.append("cleanup.detail")
    if not compact:
        argv = record.get("argv", [])
        result["argv"] = [str(arg)[:256] for arg in argv[:16]]
        result["argv_count"] = len(argv)
        result["argv_truncated"] = len(argv) > 16 or any(len(str(arg)) > 256 for arg in argv[:16])
        managed = record.get("managed", [])
        result["managed"] = [
            {key: identity[key] for key in ("pid", "ppid", "pgid", "birth") if key in identity}
            for identity in managed[-16:]
        ]
        result["managed_count"] = len(managed)
        result["managed_omitted"] = max(0, len(managed) - 16)
        supervisor = record.get("supervisor")
        if supervisor:
            result["supervisor"] = {key: supervisor[key] for key in ("pid", "birth") if key in supervisor}
        result["evidence"] = {
            "manifest": str(record.get("result", "")).removesuffix("result.json") + "manifest.json",
            "state": str(record.get("result", "")).removesuffix("result.json") + "state.json",
        }
    result["truncated_fields"] = truncated
    return result
