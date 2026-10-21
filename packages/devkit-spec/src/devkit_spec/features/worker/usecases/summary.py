"""Compact transport projection of complete worker evidence, without changing its verdict."""

from __future__ import annotations

from typing import Any


def summarize_inspection(result: dict[str, Any]) -> dict[str, Any]:
    """Project ``inspect(details=False)``; preserve actionable evidence and unknown diagnostics."""
    checks = {}
    for name, original in result["checks"].items():
        check = {key: value for key, value in original.items() if key != "result"}
        payload = original.get("result")
        if name == "envelopes" and isinstance(payload, dict):
            # inspect already projects these through Envelopes.inspection_dict: metadata and current findings.
            check["result"] = payload
        elif name == "workflow" and isinstance(payload, dict) and "workflow" in payload:
            check["result"] = {key: value for key, value in payload.items() if key not in {"stage", "done"}}
            stage = payload.get("stage")
            if isinstance(stage, dict):
                check["result"]["stage"] = {
                    key: value for key, value in stage.items() if key in {"id", "role", "isolation", "returns"}
                }
            else:
                check["result"]["stage"] = stage
        elif name == "rules" and isinstance(payload, dict) and "violations" in payload:
            check["result"] = {
                key: value for key, value in payload.items() if key in {"violations", "errors", "notices", "summary"}
            }
        elif original["status"] != "pass" or _actionable(payload):
            # Unknown failure shapes and non-JSON stdout must remain diagnosable.
            check["result"] = payload
        checks[name] = check
    return {**result, "checks": checks}


def _actionable(payload: Any) -> bool:
    """Successful wrapped commands can still contain warnings or a workflow's next action."""
    if not isinstance(payload, dict):
        return False
    return any(
        payload.get(key)
        for key in (
            "error",
            "errors",
            "notices",
            "violations",
            "unmet",
            "requests",
            "next_skill",
            "delegate",
            "gate",
            "waiting",
            "handoff",
            "stale_approvals",
            "blocked",
            "problems",
            "pending_questions",
            "malformed_workers",
            "stdout",
        )
    )
