"""``devkit status``: a read-only summary of the installed state against the receipt.

Nothing here writes project files (it only takes the shared project lock). The
command reads the receipt, the configuration and the disk once and reports
what differs; ``devkit sync --check`` remains the gate that says whether a
sync is needed.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from devkit.core.receipt import FileRecord

from . import guidance_block
from .config import effective_selection, read_config
from .discovery import InstalledBundle
from .override_commands import override_statuses
from .receipt import read_receipt, receipt_json
from .results import AssetJSON, SelectionJSON, asset_json
from .sync import project_root, tool_identity
from .transaction import pending_journal, project_lock
from .workspace import AGENTS_FILE, signature, snapshot

# ``mode-mismatch``: same bytes, different execute bit.
FileCounts = TypedDict("FileCounts", {"ok": int, "missing": int, "modified": int, "mode-mismatch": int})
FilesStatus = TypedDict(
    "FilesStatus",
    {"counts": FileCounts, "missing": list[str], "modified": list[str], "mode-mismatch": list[str]},
)


class ToolStatus(TypedDict):
    running: dict[str, str]
    recorded: dict[str, str] | None
    match: bool | None


class SeededStatus(TypedDict):
    bundle: str
    id: str
    path: str
    present: bool


class OverrideRef(TypedDict):
    bundle: str
    asset: str


class ProjectStatus(TypedDict):
    # Whether a receipt exists; without one every other entry describes an empty installation.
    receipt: bool
    schema: int | None
    # Built-in bundles the configuration opts out of (``<bundle> = false``).
    opted_out: list[str]
    selection: SelectionJSON
    files: FilesStatus
    override_drift: list[OverrideRef]
    # ``ok`` | ``missing`` | ``modified`` | ``unowned`` | ``disabled``
    guidance_block: str
    seeded: list[SeededStatus]
    pending_journal: bool
    tool: ToolStatus


def _files_status(root: Path, files: dict[str, FileRecord]) -> FilesStatus:
    status: FilesStatus = {
        "counts": {"ok": 0, "missing": 0, "modified": 0, "mode-mismatch": 0},
        "missing": [],
        "modified": [],
        "mode-mismatch": [],
    }
    for name, recorded in sorted(files.items()):
        current = snapshot(root, name)
        if current is None:
            status["counts"]["missing"] += 1
            status["missing"].append(name)
            continue
        sha, mode = signature(current)
        if sha != recorded.sha256:
            status["counts"]["modified"] += 1
            status["modified"].append(name)
        elif mode != recorded.mode:
            status["counts"]["mode-mismatch"] += 1
            status["mode-mismatch"].append(name)
        else:
            status["counts"]["ok"] += 1
    return status


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


def project_status(root: Path, installed: list[InstalledBundle]) -> ProjectStatus:
    root = project_root(root)
    running = tool_identity()
    with project_lock(root, shared=True):
        receipt = read_receipt(root)
        config = read_config(root)
        recorded = receipt.tool if receipt is not None else None
        drift = [item for item in override_statuses(installed, receipt) if item["drift_detected"]]
        return {
            "receipt": receipt is not None,
            "schema": receipt.schema if receipt is not None else None,
            "opted_out": sorted(config.opted_out),
            "selection": {
                "agents": list(receipt.selection.agents) if receipt else [],
                "presets": {name: list(values) for name, values in receipt.selection.presets.items()}
                if receipt
                else {},
            },
            "files": _files_status(root, dict(receipt.file_records) if receipt else {}),
            "override_drift": [{"bundle": item["bundle"], "asset": item["asset"]} for item in drift],
            "guidance_block": _block_state(root, receipt.guidance_block if receipt else None, config.guidance_block),
            "seeded": [
                {
                    "bundle": entry.bundle,
                    "id": entry.id,
                    "path": entry.path,
                    "present": snapshot(root, entry.path) is not None,
                }
                for entry in (receipt.seeded if receipt else ())
            ],
            "pending_journal": pending_journal(root),
            "tool": {
                "running": {"package": running.package, "version": running.version},
                "recorded": {"package": recorded.package, "version": recorded.version} if recorded else None,
                "match": recorded == running if recorded is not None else None,
            },
        }


class InstalledJSON(TypedDict):
    package: str
    version: str
    bundle: str
    presets: list[str]
    default_preset: str | None
    builtin: bool
    selected: list[str] | None
    opted_out: bool
    assets: list[dict[str, str]]


class ProjectListing(TypedDict):
    installed: list[InstalledJSON]
    synchronized_assets: list[AssetJSON]
    seeded: list[dict[str, str]]
    overrides: dict[str, dict[str, dict[str, str]]]


def project_listing(root: Path, installed: list[InstalledBundle]) -> ProjectListing:
    """``devkit list``: installed bundles with their selection state, and what the receipt records."""
    root = project_root(root)
    with project_lock(root, shared=True):
        receipt = read_receipt(root)
        config = read_config(root)
    selected = effective_selection(installed, config)
    recorded = receipt_json(receipt) if receipt is not None else {}
    return {
        "installed": [
            {
                "package": item.package,
                "version": item.package_version,
                "bundle": item.bundle.name,
                "presets": item.bundle.preset_names,
                "default_preset": item.bundle.default_preset,
                "builtin": item.builtin,
                "selected": selected.get(item.bundle.name),
                "opted_out": item.bundle.name in config.opted_out,
                "assets": [{"id": asset.id, "kind": asset.kind} for asset in item.bundle.assets],
            }
            for item in installed
        ],
        "synchronized_assets": [asset_json(asset) for asset in receipt.asset_records] if receipt else [],
        "seeded": recorded.get("seeded", []),
        "overrides": recorded.get("overrides", {}),
    }
