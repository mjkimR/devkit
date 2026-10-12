"""``devkit status``: a read-only summary of the installed state against the receipt.

Nothing here writes. The command reads the receipt, the configuration and the
disk once and reports what differs; ``devkit sync --check`` remains the gate
that says whether a sync is needed.
"""

from __future__ import annotations

from pathlib import Path

from . import guidance_block
from .config import read_config
from .discovery import InstalledBundle
from .overrides import list_overrides
from .sync import read_receipt, tool_identity
from .transaction import AGENTS_FILE, JOURNAL, signature, snapshot


def _files_status(root: Path, files: dict[str, dict[str, object]]) -> dict[str, object]:
    counts = {"ok": 0, "missing": 0, "modified": 0, "mode-mismatch": 0}
    paths: dict[str, list[str]] = {"missing": [], "modified": [], "mode-mismatch": []}
    for name, recorded in sorted(files.items()):
        current = snapshot(root, name)
        if current is None:
            state = "missing"
        else:
            actual = signature(current)
            if actual == recorded:
                state = "ok"
            elif actual["sha256"] == recorded["sha256"]:
                state = "mode-mismatch"
            else:
                state = "modified"
        counts[state] += 1
        if state != "ok":
            paths[state].append(name)
    return {"counts": counts, **paths}


def _block_state(root: Path, recorded: str | None, enabled: bool) -> str:
    if not enabled:
        return "disabled"
    current = snapshot(root, AGENTS_FILE)
    existing = guidance_block.extract(guidance_block.decode(current.data if current else None))
    if existing is None:
        return "missing"
    if recorded is None:
        return "unowned"
    return "ok" if guidance_block.digest(existing) == recorded else "modified"


def project_status(root: Path, installed: list[InstalledBundle]) -> dict[str, object]:
    root = root.resolve()
    receipt = read_receipt(root)
    config = read_config(root)
    running = tool_identity()
    if not receipt:
        return {
            "receipt": False,
            "pending_journal": snapshot(root, JOURNAL) is not None,
            "tool": {"running": running, "recorded": None, "match": None},
        }
    recorded_tool = receipt.get("tool")
    seeded = [
        {**entry, "present": snapshot(root, entry["path"]) is not None}
        for entry in receipt.get("seeded", [])
        if isinstance(entry, dict)
    ]
    drift = [item for item in list_overrides(root, installed) if item["drift_detected"]]
    return {
        "receipt": True,
        "schema": receipt["schema"],
        "selection": receipt["selection"],
        "files": _files_status(root, receipt["files"]),
        "override_drift": [{"bundle": item["bundle"], "asset": item["asset"]} for item in drift],
        "guidance_block": _block_state(root, receipt.get("guidance_block"), config.guidance_block),
        "seeded": seeded,
        "pending_journal": snapshot(root, JOURNAL) is not None,
        "tool": {
            "running": running,
            "recorded": recorded_tool,
            "match": recorded_tool == running if recorded_tool is not None else None,
        },
    }
