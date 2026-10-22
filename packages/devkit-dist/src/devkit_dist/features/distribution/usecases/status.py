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

from devkit.advisory import Actor, AdvisoryError, ExitCode, Level
from devkit_core.core.logs import get_logger

from devkit_dist.features.distribution.models.content import signature
from devkit_dist.features.distribution.models.errors import (
    GuidanceBlockError,
    NotSynchronizedError,
    OverrideDriftError,
    PendingTransactionError,
    UnsafeWorkspaceError,
)
from devkit_dist.features.distribution.models.results import (
    asset_json,
    overrides_json,
    seeded_json,
    selection_json,
    tool_json,
)
from devkit_dist.features.distribution.services.installation import guidance_block
from devkit_dist.features.distribution.services.installation.config import (
    ProjectConfig,
    effective_selection,
    missing_selection_error,
    read_config,
)
from devkit_dist.features.distribution.services.installation.discovery import (
    InstalledBundle,
    unusable_bundles,
    unusable_notices,
)
from devkit_dist.features.distribution.services.installation.engines import engine_notices
from devkit_dist.features.distribution.services.installation.local_render import runtime_receipt
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.services.installation.transaction import pending_journal, project_lock
from devkit_dist.features.distribution.services.installation.workspace import AGENTS_FILE, occupied, snapshot
from devkit_dist.features.distribution.usecases.override_commands import override_statuses
from devkit_dist.features.distribution.usecases.sync import (
    block_conflict,
    edited_files_error,
    guidance_block_error,
    planned_guidance_block,
    read_deployed,
    require_project_dir,
    tool_identity,
)
from devkit_dist.features.host import HostError, InspectHost
from devkit_dist.features.project.repositories.local_config import read_effective_config
from devkit_dist.features.project.repositories.receipt import (
    AssetRecord,
    FileRecord,
    OverrideRecord,
    Receipt,
    SeededRecord,
    Selection,
    ToolRecord,
)
from devkit_dist.features.project.services.presentation import language_notices

_EMPTY_SELECTION = Selection((), {})
logger = get_logger(__name__)


@dataclass(frozen=True)
class FilesStatus:
    """Receipt-owned files compared with the disk.

    ``stale``: differs from the receipt but is as this clone's last sync left it (the receipt moved, for example
    with a pull; ``devkit sync`` brings it up to date); ``mode_mismatch``: same bytes, different execute bit;
    ``unsafe``: a symlink or non-regular file where the receipt records a file.
    """

    ok: int = 0
    missing: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    mode_mismatch: list[str] = field(default_factory=list)
    unsafe: list[str] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": {
                "ok": self.ok,
                "missing": len(self.missing),
                "stale": len(self.stale),
                "modified": len(self.modified),
                "mode-mismatch": len(self.mode_mismatch),
                "unsafe": len(self.unsafe),
            },
            "missing": list(self.missing),
            "stale": list(self.stale),
            "modified": list(self.modified),
            "mode-mismatch": list(self.mode_mismatch),
            "unsafe": list(self.unsafe),
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
    """``devkit status``. ``errors`` are the problems to act on; ``ok`` when there are none.

    ``notices``: warnings that change no exit code (an installed package the project does not deploy failed to load,
    an unsupported ``[presentation] language`` resolved to ``en``, deployed rule, gate or workflow assets that no
    installed engine runs).
    """

    # Whether a receipt exists; without one every other entry describes an empty installation.
    receipt: bool
    schema: int | None
    # Built-in bundles the configuration opts out of (``<bundle> = false``).
    opted_out: list[str]
    selection: Selection
    files: FilesStatus
    # ``(bundle, asset)`` of every override whose upstream changed since its baseline.
    override_drift: list[tuple[str, str]]
    # ``ok`` | ``missing`` | ``modified`` | ``unowned`` | ``disabled`` | ``invalid``
    guidance_block: str
    seeded: list[SeededStatus]
    pending_journal: bool
    tool: ToolStatus
    host_hooks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[AdvisoryError] = field(default_factory=list)
    notices: list[AdvisoryError] = field(default_factory=list)

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
            "host_hooks": self.host_hooks,
            "errors": [error.to_dict() for error in self.errors],
            "notices": [notice.to_dict() for notice in self.notices],
        }


def _unusable_packages(
    installed: list[InstalledBundle], selected: dict[str, list[str]]
) -> tuple[list[AdvisoryError], list[AdvisoryError]]:
    """Load errors of installed packages: a problem when the project selects the bundle, else a warning."""
    problems: list[AdvisoryError] = []
    warnings: list[AdvisoryError] = []
    for name, error in sorted(unusable_bundles(installed).items()):
        if name in selected:
            problem = error.with_level(Level.ERROR)
            problem.exit_code = ExitCode.FINDINGS
            problems.append(problem)
        else:
            warnings.append(error.with_level(Level.WARNING))
    return problems, warnings


def _missing_packages(
    installed: list[InstalledBundle], selected: dict[str, list[str]], config: ProjectConfig
) -> list[AdvisoryError]:
    """``SELECTION_INVALID`` (exit ``1``) for selected bundles that no installed package provides, as ``devkit sync``
    raises it: an entry of ``config.toml``, or a bundle the receipt records deployed (``retained_selection``)."""
    known = {item.bundle.name for item in installed} | unusable_bundles(installed).keys()
    missing = sorted(set(selected) - known)
    if not missing:
        return []
    problem = missing_selection_error(missing, [name for name in missing if name not in config.presets])
    problem.exit_code = ExitCode.FINDINGS
    return [problem]


def _files_status(root: Path, files: dict[str, FileRecord]) -> FilesStatus:
    deployed = read_deployed(root)
    ok = 0
    missing: list[str] = []
    stale: list[str] = []
    modified: list[str] = []
    mode_mismatch: list[str] = []
    unsafe: list[str] = []
    for name, recorded in sorted(files.items()):
        try:
            current = snapshot(root, name)
        except UnsafeWorkspaceError:
            unsafe.append(name)
            continue
        if current is None:
            missing.append(name)
            continue
        sha, mode = signature(current)
        left = deployed.get(name)
        if (
            (sha, mode) != (recorded.sha256, recorded.mode)
            and left is not None
            and (sha, mode)
            == (
                left.sha256,
                left.mode,
            )
        ):
            stale.append(name)
        elif sha != recorded.sha256:
            modified.append(name)
        elif mode != recorded.mode:
            mode_mismatch.append(name)
        else:
            ok += 1
    return FilesStatus(ok, missing, modified, mode_mismatch, unsafe, stale)


@dataclass(frozen=True)
class _BlockState:
    # ``ok`` | ``missing`` | ``modified`` | ``unowned`` | ``disabled`` | ``invalid``
    state: str
    # The ``BLOCK_CONFLICTS`` state ``devkit sync`` would raise; ``None`` when it would raise none.
    conflict: str | None = None
    # Why ``AGENTS.md`` cannot be read safely (``invalid``).
    error: AdvisoryError | None = None


def _planned_block(
    root: Path, installed: list[InstalledBundle], config: ProjectConfig, receipt: Receipt | None
) -> str | None:
    """The block a plain ``devkit sync`` would write; ``None`` when planning that sync fails (status reports why)."""
    try:
        return planned_guidance_block(root, installed, config, receipt)
    except AdvisoryError as exc:
        logger.debug("guidance block not planned: %s", exc.message)
        return None


def _block_state(
    root: Path, installed: list[InstalledBundle], config: ProjectConfig, receipt: Receipt | None
) -> _BlockState:
    """The guidance block state and the conflict ``devkit sync`` would raise for it (``block_conflict``).

    An ``unowned`` block is compared with the block a sync would write: an
    identical one is adopted by the next sync, so it is no conflict.
    """
    if not config.guidance_block:
        return _BlockState("disabled")
    try:
        current = snapshot(root, AGENTS_FILE)
        existing = guidance_block.extract(guidance_block.decode(current.data if current else None))
    except (UnsafeWorkspaceError, GuidanceBlockError) as exc:
        exc.exit_code = ExitCode.FINDINGS
        return _BlockState("invalid", error=exc)
    if existing is None:
        return _BlockState("missing")
    recorded = receipt.guidance_block if receipt is not None else None
    if recorded is None:
        desired = _planned_block(root, installed, config, receipt)
        return _BlockState("unowned", block_conflict(existing, None, desired))
    conflict = block_conflict(existing, recorded, None)
    return _BlockState("ok" if conflict is None else "modified", conflict)


def _problems(
    files: FilesStatus, journal: bool, drift: list[tuple[str, str]], block: _BlockState
) -> list[AdvisoryError]:
    """What ``devkit status`` exits 1 for: missing, stale, modified, mode-mismatched or unsafe files, a journal, override
    drift, a root ``AGENTS.md`` that cannot be read safely, and a guidance block in the ``SYNC_CONFLICT`` a sync raises
    for it, as for an edited managed file: ``modified``, or ``unowned`` and not the block the sync would adopt."""
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
    if files.stale:
        problems.append(
            NotSynchronizedError(
                f"managed files are behind the receipt: {', '.join(files.stale)}",
                target_files=files.stale,
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
    if files.unsafe:
        problems.append(
            UnsafeWorkspaceError(
                f"managed paths are symlinks or not regular files: {', '.join(files.unsafe)}",
                target_files=files.unsafe,
                what_to_report="Whether to replace these paths with the files devkit deploys;"
                " devkit never reads or writes through a symlink",
                exit_code=findings,
            )
        )
    if block.error is not None:
        problems.append(block.error)
    if block.conflict is not None:
        problems.append(guidance_block_error(block.conflict, exit_code=findings))
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
        receipt = read_receipt(root, check_disk=False)
        config = read_config(root)
        effective_receipt = runtime_receipt(root, receipt) if receipt else None
        files = _files_status(root, dict(effective_receipt.file_records) if effective_receipt else {})
        # Drift of deployed assets only, as ``devkit sync`` reports it; records kept for assets that are not
        # deployed (a deselected bundle, a narrowed preset) are reported when the asset is selected again.
        deployed = {(asset.bundle, asset.id) for asset in receipt.asset_records} if receipt else set()
        drift = [
            (item.bundle, item.asset)
            for item in override_statuses(installed, receipt)
            if item.drift_detected and (item.bundle, item.asset) in deployed
        ]
        block = _block_state(root, installed, config, receipt)
        journal = pending_journal(root)
        selected = effective_selection(installed, config, receipt)
        packages, warnings = _unusable_packages(installed, selected)
        packages.extend(_missing_packages(installed, selected, config))
        desired_environment = read_effective_config(root).values["execution"]["environment"]
        if receipt is not None and receipt.execution_environment != desired_environment:
            packages.append(
                NotSynchronizedError(
                    f"render environment is {receipt.execution_environment or 'unrecorded'}; desired {desired_environment}",
                    target_files=[".devkit/installation.json"],
                    exit_code=ExitCode.FINDINGS,
                )
            )
        host_hooks: list[dict[str, Any]] = []
        host_errors: list[AdvisoryError] = []
        for host in sorted({record.host for record in receipt.host_hooks} if receipt else set()):
            try:
                host_report = InspectHost().execute(root, host, check_handlers=False)
                host_hooks.extend(host_report.hooks)
                host_errors.extend(host_report.errors)
            except HostError as exc:
                host_errors.append(exc)
        return ProjectStatus(
            receipt=receipt is not None,
            schema=receipt.schema if receipt is not None else None,
            opted_out=sorted(config.opted_out),
            selection=receipt.selection if receipt is not None else _EMPTY_SELECTION,
            files=files,
            override_drift=drift,
            guidance_block=block.state,
            seeded=[SeededStatus(entry, occupied(root, entry.path)) for entry in (receipt.seeded if receipt else ())],
            pending_journal=journal,
            tool=ToolStatus(tool_identity(), receipt.tool if receipt is not None else None),
            host_hooks=host_hooks,
            errors=[*packages, *_problems(files, journal, drift, block), *host_errors],
            notices=[*warnings, *language_notices(root), *engine_notices(receipt.asset_records if receipt else ())],
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
    """``devkit list``: installed bundles, and what the receipt records as synchronized.

    ``notices``: a warning per installed package the project does not deploy that failed to load.
    """

    installed: list[InstalledEntry]
    synchronized_assets: tuple[AssetRecord, ...] = ()
    seeded: tuple[SeededRecord, ...] = ()
    overrides: dict[str, dict[str, OverrideRecord]] = field(default_factory=dict)
    notices: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "installed": [entry.to_dict() for entry in self.installed],
            "synchronized_assets": [asset_json(asset) for asset in self.synchronized_assets],
            "seeded": seeded_json(self.seeded),
            "overrides": overrides_json(self.overrides),
            "notices": [notice.to_dict() for notice in self.notices],
        }


def get_project_listing(root: Path, installed: list[InstalledBundle]) -> ProjectListing:
    """``devkit list``: installed bundles with their selection state, and what the receipt records."""
    root = require_project_dir(root)
    with project_lock(root, shared=True):
        # Like ``devkit status``, a listing does not check the recorded paths on disk: a symlinked managed file is
        # reported by ``devkit status`` and refused by ``devkit sync``, never a reason to fail a read-only listing.
        receipt = read_receipt(root, check_disk=False)
        config = read_config(root)
    selected = effective_selection(installed, config, receipt)
    notices = unusable_notices(installed, selected)
    entries = [
        InstalledEntry(item, selected.get(item.bundle.name), item.bundle.name in config.opted_out) for item in installed
    ]
    if receipt is None:
        return ProjectListing(entries, notices=notices)
    return ProjectListing(entries, receipt.asset_records, receipt.seeded, _plain_overrides(receipt), notices)


def _plain_overrides(receipt: Receipt) -> dict[str, dict[str, OverrideRecord]]:
    return {bundle: dict(records) for bundle, records in receipt.overrides.items()}
