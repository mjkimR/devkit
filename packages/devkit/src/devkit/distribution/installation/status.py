"""``devkit status`` and ``devkit list``: read-only reports of the installed state.

Nothing here writes project files (it only takes the shared project lock).
``devkit status`` reads the receipt, the configuration and the disk once and
reports what differs; what needs acting on is collected under ``errors``.
``devkit sync --check`` remains the gate that says whether a sync is needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from devkit.advisory import Actor, AdvisoryError, ExitCode
from devkit.core.receipt import AssetRecord, FileRecord, OverrideRecord, Receipt, SeededRecord, Selection, ToolRecord
from devkit.distribution.content import signature
from devkit.distribution.errors import NotSynchronizedError, OverrideDriftError, PendingTransactionError
from devkit.distribution.installation import guidance_block
from devkit.distribution.installation.config import effective_selection, read_config
from devkit.distribution.installation.discovery import InstalledBundle
from devkit.distribution.installation.override_commands import override_statuses
from devkit.distribution.installation.receipt import read_receipt
from devkit.distribution.installation.results import (
    asset_json,
    overrides_json,
    seeded_json,
    selection_json,
    tool_json,
)
from devkit.distribution.installation.sync import edited_files_error, require_project_dir, tool_identity
from devkit.distribution.installation.transaction import pending_journal, project_lock
from devkit.distribution.installation.workspace import AGENTS_FILE, snapshot

_EMPTY_SELECTION = Selection((), {})


@dataclass(frozen=True)
class FilesStatus:
    """Receipt-owned files compared with the disk; ``mode_mismatch``: same bytes, different execute bit."""

    ok: int = 0
    missing: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    mode_mismatch: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": {
                "ok": self.ok,
                "missing": len(self.missing),
                "modified": len(self.modified),
                "mode-mismatch": len(self.mode_mismatch),
            },
            "missing": list(self.missing),
            "modified": list(self.modified),
            "mode-mismatch": list(self.mode_mismatch),
        }


@dataclass(frozen=True)
class SeededStatus:
    record: SeededRecord
    present: bool

    def to_dict(self) -> dict[str, Any]:
        return {"bundle": self.record.bundle, "id": self.record.id, "path": self.record.path, "present": self.present}


@dataclass(frozen=True)
class ToolStatus:
    running: ToolRecord
    recorded: ToolRecord | None

    @property
    def match(self) -> bool | None:
        """Whether the receipt was written by the running devkit; ``None`` without a recorded tool."""
        return self.recorded == self.running if self.recorded is not None else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "running": tool_json(self.running),
            "recorded": tool_json(self.recorded) if self.recorded is not None else None,
            "match": self.match,
        }


@dataclass(frozen=True)
class ProjectStatus:
    """``devkit status``. ``errors`` are the problems to act on; ``ok`` when there are none."""

    # Whether a receipt exists; without one every other entry describes an empty installation.
    receipt: bool
    schema: int | None
    # Built-in bundles the configuration opts out of (``<bundle> = false``).
    opted_out: list[str]
    selection: Selection
    files: FilesStatus
    # ``(bundle, asset)`` of every override whose upstream changed since its baseline.
    override_drift: list[tuple[str, str]]
    # ``ok`` | ``missing`` | ``modified`` | ``unowned`` | ``disabled``
    guidance_block: str
    seeded: list[SeededStatus]
    pending_journal: bool
    tool: ToolStatus
    errors: list[AdvisoryError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt": self.receipt,
            "schema": self.schema,
            "opted_out": list(self.opted_out),
            "selection": selection_json(self.selection),
            "files": self.files.to_dict(),
            "override_drift": [{"bundle": bundle, "asset": asset} for bundle, asset in self.override_drift],
            "guidance_block": self.guidance_block,
            "seeded": [item.to_dict() for item in self.seeded],
            "pending_journal": self.pending_journal,
            "tool": self.tool.to_dict(),
            "errors": [error.to_dict() for error in self.errors],
        }


def _files_status(root: Path, files: dict[str, FileRecord]) -> FilesStatus:
    ok = 0
    missing: list[str] = []
    modified: list[str] = []
    mode_mismatch: list[str] = []
    for name, recorded in sorted(files.items()):
        current = snapshot(root, name)
        if current is None:
            missing.append(name)
            continue
        sha, mode = signature(current)
        if sha != recorded.sha256:
            modified.append(name)
        elif mode != recorded.mode:
            mode_mismatch.append(name)
        else:
            ok += 1
    return FilesStatus(ok, missing, modified, mode_mismatch)


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


def _problems(files: FilesStatus, journal: bool, drift: list[tuple[str, str]]) -> list[AdvisoryError]:
    """What ``devkit status`` exits 1 for: missing, modified or mode-mismatched files, a journal, override drift."""
    findings = ExitCode.FINDINGS
    problems: list[AdvisoryError] = []
    if files.missing:
        problems.append(
            NotSynchronizedError(
                f"managed files are missing: {', '.join(files.missing)}",
                target_files=files.missing,
                exit_code=findings,
            )
        )
    if files.modified:
        problems.append(
            edited_files_error(
                f"managed files were edited: {', '.join(files.modified)}", files.modified, exit_code=findings
            )
        )
    if files.mode_mismatch:
        problems.append(
            edited_files_error(
                f"managed files changed their execute bit: {', '.join(files.mode_mismatch)}",
                files.mode_mismatch,
                exit_code=findings,
            )
        )
    if journal:
        problems.append(PendingTransactionError("an interrupted synchronization left its journal", exit_code=findings))
    if drift:
        listed = [f"{bundle}:{asset}" for bundle, asset in drift]
        problems.append(
            OverrideDriftError(
                f"upstream changed behind overrides: {', '.join(listed)}",
                guardrail=False,
                actor=Actor.USER,
                what_to_report="Whether each override should take over the upstream change",
                fix=f"Review with `devkit override diff {listed[0]}`, then record it with"
                f" `devkit override accept {listed[0]}`",
                exit_code=findings,
            )
        )
    return problems


def get_project_status(root: Path, installed: list[InstalledBundle]) -> ProjectStatus:
    """``devkit status``: the installed state against the receipt, without writing anything."""
    root = require_project_dir(root)
    with project_lock(root, shared=True):
        receipt = read_receipt(root)
        config = read_config(root)
        files = _files_status(root, dict(receipt.file_records) if receipt else {})
        drift = [(item.bundle, item.asset) for item in override_statuses(installed, receipt) if item.drift_detected]
        journal = pending_journal(root)
        return ProjectStatus(
            receipt=receipt is not None,
            schema=receipt.schema if receipt is not None else None,
            opted_out=sorted(config.opted_out),
            selection=receipt.selection if receipt is not None else _EMPTY_SELECTION,
            files=files,
            override_drift=drift,
            guidance_block=_block_state(root, receipt.guidance_block if receipt else None, config.guidance_block),
            seeded=[
                SeededStatus(entry, snapshot(root, entry.path) is not None)
                for entry in (receipt.seeded if receipt else ())
            ],
            pending_journal=journal,
            tool=ToolStatus(tool_identity(), receipt.tool if receipt is not None else None),
            errors=_problems(files, journal, drift),
        )


@dataclass(frozen=True)
class InstalledEntry:
    """An installed bundle with its selection state in the project."""

    item: InstalledBundle
    # The presets the project deploys; ``None`` when the bundle is not selected.
    selected: list[str] | None
    opted_out: bool

    def to_dict(self) -> dict[str, Any]:
        bundle = self.item.bundle
        return {
            "package": self.item.package,
            "version": self.item.package_version,
            "bundle": bundle.name,
            "presets": bundle.preset_names,
            "default_preset": bundle.default_preset,
            "builtin": self.item.builtin,
            "auto_select": self.item.auto_selected,
            "selected": self.selected,
            "opted_out": self.opted_out,
            "assets": [{"id": asset.id, "kind": asset.kind} for asset in bundle.assets],
        }


@dataclass(frozen=True)
class ProjectListing:
    """``devkit list``: installed bundles, and what the receipt records as synchronized."""

    installed: list[InstalledEntry]
    synchronized_assets: tuple[AssetRecord, ...] = ()
    seeded: tuple[SeededRecord, ...] = ()
    overrides: dict[str, dict[str, OverrideRecord]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "installed": [entry.to_dict() for entry in self.installed],
            "synchronized_assets": [asset_json(asset) for asset in self.synchronized_assets],
            "seeded": seeded_json(self.seeded),
            "overrides": overrides_json(self.overrides),
        }


def get_project_listing(root: Path, installed: list[InstalledBundle]) -> ProjectListing:
    """``devkit list``: installed bundles with their selection state, and what the receipt records."""
    root = require_project_dir(root)
    with project_lock(root, shared=True):
        receipt = read_receipt(root)
        config = read_config(root)
    selected = effective_selection(installed, config)
    entries = [
        InstalledEntry(item, selected.get(item.bundle.name), item.bundle.name in config.opted_out) for item in installed
    ]
    if receipt is None:
        return ProjectListing(entries)
    return ProjectListing(entries, receipt.asset_records, receipt.seeded, _plain_overrides(receipt))


def _plain_overrides(receipt: Receipt) -> dict[str, dict[str, OverrideRecord]]:
    return {bundle: dict(records) for bundle, records in receipt.overrides.items()}
