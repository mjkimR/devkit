"""``devkit override``: create, review, accept, remove and list project overrides.

``create`` and ``remove`` change files under ``.devkit/overrides/`` and then
synchronize, under one project lock: when the synchronization fails before
it commits, the override files are put back as they were. ``accept`` advances the recorded
baseline through the journal.
"""

from __future__ import annotations

import dataclasses
import difflib
from pathlib import Path
from types import MappingProxyType

from devkit.advisory import AdvisoryError
from devkit_core.base.errors import ArgumentError

from devkit_dist.features.distribution.models.content import Content, normal_mode
from devkit_dist.features.distribution.models.errors import ConflictError, OrphanLeftNotice, SelectionError
from devkit_dist.features.distribution.models.results import (
    OverrideChange,
    OverrideDiff,
    OverrideFileDiff,
    OverrideStatus,
    SyncResult,
)
from devkit_dist.features.distribution.services.bundles.common import SLUG
from devkit_dist.features.distribution.services.bundles.manifest import Asset
from devkit_dist.features.distribution.services.installation.config import effective_selection, read_config
from devkit_dist.features.distribution.services.installation.discovery import InstalledBundle, unusable_bundles
from devkit_dist.features.distribution.services.installation.extensions import run_post_sync
from devkit_dist.features.distribution.services.installation.overrides import (
    asset_files,
    baseline_rel,
    has_override,
    overridden_files,
    override_rel,
    primary_path,
    record_overridden,
    record_source,
    upstream_digest,
)
from devkit_dist.features.distribution.services.installation.receipt import read_receipt, receipt_content
from devkit_dist.features.distribution.services.installation.transaction import (
    apply_changes,
    project_lock,
    prune_empty_parents,
    replace_file,
    require_no_journal,
)
from devkit_dist.features.distribution.services.installation.workspace import checked_path
from devkit_dist.features.distribution.usecases.sync import commit_locked, require_project_dir
from devkit_dist.features.project.repositories.receipt import OVERRIDES_PATH, RECEIPT_PATH, OverrideRecord, Receipt

# Emptied directories are pruned up to here, ``.devkit/overrides/`` itself included.
_PRUNE_STOP = OVERRIDES_PATH.rsplit("/", 1)[0]


def _parse_selector(selector: str) -> tuple[str, str]:
    bundle, separator, asset = selector.partition(":")
    if not separator or not bundle or not asset:
        raise ArgumentError(
            f"expected bundle:asset selector (e.g. starter:development): {selector}", target_files=["SELECTOR"]
        )
    if not SLUG.fullmatch(bundle) or not SLUG.fullmatch(asset):
        raise ArgumentError(f"bundle and asset must be lowercase slugs: {selector}", target_files=["SELECTOR"])
    return bundle, asset


def _find(installed: list[InstalledBundle], bundle_name: str, asset_id: str) -> tuple[InstalledBundle, Asset]:
    item = next((b for b in installed if b.bundle.name == bundle_name), None)
    if item is None:
        unusable = unusable_bundles(installed)
        if bundle_name in unusable:
            raise unusable[bundle_name]
        raise SelectionError(f"bundle is not installed: {bundle_name}", fix="List installed bundles with `devkit list`")
    asset = item.bundle.asset(asset_id)
    if asset is None:
        raise SelectionError(f"asset not found in {bundle_name}: {asset_id}", fix="List the assets with `devkit list`")
    return item, asset


class _Undo:
    """Writes and deletes under ``.devkit/overrides/`` that can be put back on failure."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.saved: dict[str, Content | None] = {}

    def _save(self, name: str) -> Path:
        path = checked_path(self.root, name)
        if name not in self.saved:
            self.saved[name] = Content(path.read_bytes(), path.stat().st_mode & 0o777) if path.exists() else None
        return path

    def write(self, name: str, content: Content) -> None:
        replace_file(self._save(name), content)

    def delete(self, name: str) -> None:
        replace_file(self._save(name), None)
        prune_empty_parents(self.root, name, stop=_PRUNE_STOP)

    def restore(self) -> None:
        for name, before in reversed(self.saved.items()):
            replace_file(checked_path(self.root, name), before)
            if before is None:
                prune_empty_parents(self.root, name, stop=_PRUNE_STOP)


def _require_overridable(root: Path, installed: list[InstalledBundle], item: InstalledBundle, asset: Asset) -> None:
    name = item.bundle.name
    selection = effective_selection(installed, read_config(root))
    if name not in selection:
        raise SelectionError(f"bundle is not selected: {name}", fix=f"Select it first with `devkit add {name}`")
    if asset.id not in item.bundle.select(selection[name]):
        raise SelectionError(
            f"asset {name}:{asset.id} is not part of the selected presets {selection[name]}",
            fix=f"Select a preset that contains it with `devkit add {name}:<preset>`",
        )
    if asset.seeded:
        raise SelectionError(
            f"{name}:{asset.id} is a seeded asset: its files are project-owned",
            fix="Edit the seeded files directly; they need no override",
        )


def _after_sync(root: Path, result: SyncResult) -> list[AdvisoryError]:
    """The sync's notices and the post-sync extensions' (run once the project lock is released)."""
    return [*result.notices, *run_post_sync(root, result.to_dict())]


def create_override(
    root: Path, installed: list[InstalledBundle], selector: str, *, force: bool = False
) -> OverrideChange:
    """Copy every upstream file of an asset into ``.devkit/overrides/`` (and its baseline), then synchronize.

    The current upstream becomes the recorded baseline, also when ``force`` replaces an existing override.
    """
    root = require_project_dir(root)
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root):
        require_no_journal(root)
        item, asset = _find(installed, bundle_name, asset_id)
        _require_overridable(root, installed, item, asset)
        files = asset_files(item.bundle, asset)
        if not force:
            existing = [rel for rel in files if (root / override_rel(bundle_name, rel)).exists()]
            if existing:
                raise ConflictError(
                    f"override already exists: {override_rel(bundle_name, existing[0])}",
                    target_files=[override_rel(bundle_name, rel) for rel in existing],
                    what_to_report="Whether to replace the existing override files with the upstream copy",
                    fix=f"Replace them with `devkit override create {selector} --force`",
                )
        undo = _Undo(root)
        try:
            for rel in files:
                path = item.bundle.root / rel
                content = Content(path.read_bytes(), normal_mode(path.stat().st_mode))
                undo.write(override_rel(bundle_name, rel), content)
                undo.write(baseline_rel(bundle_name, rel), content)
            finish = commit_locked(root, installed, rebaseline=(bundle_name, asset_id))
        except BaseException:
            undo.restore()
            raise
        result = finish()
    return OverrideChange(
        bundle_name,
        asset_id,
        "created",
        [override_rel(bundle_name, rel) for rel in files],
        notices=_after_sync(root, result),
    )


def _files_under(root: Path, name: str) -> list[str]:
    """Workspace paths of the file (or symlink) at ``name``, or of every file under the directory there."""
    base = root / name
    found = sorted(p for p in base.rglob("*") if p.is_file() or p.is_symlink()) if base.is_dir() else [base]
    return [p.relative_to(root).as_posix() for p in found if p.is_file() or p.is_symlink()]


def _removed_asset_source(root: Path, installed: list[InstalledBundle], bundle_name: str, asset_id: str) -> str | None:
    """The override source of a tracked asset its installed bundle no longer has, while files remain under it."""
    item = next((b for b in installed if b.bundle.name == bundle_name), None)
    if item is None or item.bundle.asset(asset_id) is not None:
        return None
    receipt = read_receipt(root)
    record = receipt.overrides.get(bundle_name, {}).get(asset_id) if receipt is not None else None
    if record is None or not record_overridden(root, bundle_name, record):
        return None
    return record_source(record)


def remove_override(root: Path, installed: list[InstalledBundle], selector: str) -> OverrideChange:
    """Delete an asset's override and baseline files, then synchronize the pristine upstream files.

    Only the override files of the asset's upstream files are deleted (with every baseline copy, which devkit
    writes): any other project file under the asset's override paths stays and is reported as ``ORPHAN_LEFT``.
    For a tracked override of an asset its bundle no longer has, every file under the recorded path is deleted
    and the sync drops the record.
    """
    root = require_project_dir(root)
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root):
        require_no_journal(root)
        removed = _removed_asset_source(root, installed, bundle_name, asset_id)
        if removed is not None:
            sources = [removed]
            tracked = None
        else:
            item, asset = _find(installed, bundle_name, asset_id)
            sources = [source for _, source in asset.sources]
            tracked = {override_rel(bundle_name, rel) for rel in asset_files(item.bundle, asset)}
        under = sorted({name for source in sources for name in _files_under(root, override_rel(bundle_name, source))})
        overrides = [name for name in under if tracked is None or name in tracked]
        if not overrides:
            raise SelectionError(f"no override found for {selector}", fix="List overrides with `devkit override list`")
        extra = [name for name in under if tracked is not None and name not in tracked]
        baselines = sorted(
            {name for source in sources for name in _files_under(root, baseline_rel(bundle_name, source))}
        )
        undo = _Undo(root)
        try:
            for name in [*overrides, *baselines]:
                undo.delete(name)
            finish = commit_locked(root, installed)
        except BaseException:
            undo.restore()
            raise
        result = finish()
    notices = _after_sync(root, result)
    if extra:
        notices.insert(
            0,
            OrphanLeftNotice(
                f"left project files in place under the override of {selector}: {', '.join(extra)}"
                " (no upstream file of the asset has these paths)",
                target_files=extra,
                what_to_report=f"Whether to delete {', '.join(extra)}; devkit deletes only the override files of"
                " the asset's upstream files",
            ),
        )
    return OverrideChange(bundle_name, asset_id, "removed", overrides, notices=notices)


def _tracked(receipt: Receipt | None, bundle: str, asset: str, selector: str) -> OverrideRecord:
    record = receipt.overrides.get(bundle, {}).get(asset) if receipt is not None else None
    if record is None:
        raise SelectionError(
            f"{selector} has no tracked override",
            fix=f"Create one with `devkit override create {selector}`, or run `devkit sync` if its files already exist",
        )
    return record


def accept_override(root: Path, installed: list[InstalledBundle], selector: str) -> OverrideChange:
    """Record the current upstream files as the override's baseline (after reviewing ``override diff``)."""
    root = require_project_dir(root)
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root):
        require_no_journal(root)
        receipt = read_receipt(root)
        record = _tracked(receipt, bundle_name, asset_id, selector)
        assert receipt is not None
        item, asset = _find(installed, bundle_name, asset_id)
        current = upstream_digest(item.bundle, asset)
        overrides = {bundle: dict(records) for bundle, records in receipt.overrides.items()}
        overrides[bundle_name][asset_id] = dataclasses.replace(record, baseline_upstream_sha256=current)
        updated = dataclasses.replace(
            receipt,
            overrides=MappingProxyType({bundle: MappingProxyType(records) for bundle, records in overrides.items()}),
        )
        undo = _Undo(root)
        try:
            for rel in asset_files(item.bundle, asset):
                path = item.bundle.root / rel
                undo.write(baseline_rel(bundle_name, rel), Content(path.read_bytes(), normal_mode(path.stat().st_mode)))
            apply_changes(root, {RECEIPT_PATH: receipt_content(updated)})
        except BaseException:
            undo.restore()
            raise
    return OverrideChange(bundle_name, asset_id, "accepted", [], accepted_upstream_sha256=current)


def _text(path: Path) -> list[str] | None:
    """Lines of a UTF-8 file; ``None`` when the file is absent or binary."""
    if not path.is_file():
        return None
    try:
        return path.read_text("utf-8").splitlines(keepends=True)
    except UnicodeError:
        return None


def _diff(before: list[str] | None, after: list[str] | None, before_name: str, after_name: str) -> str | None:
    if before is None or after is None:
        return None
    return "".join(difflib.unified_diff(before, after, fromfile=before_name, tofile=after_name))


def diff_override(root: Path, installed: list[InstalledBundle], selector: str) -> OverrideDiff:
    """Per file: upstream -> override, and the recorded baseline -> current upstream."""
    root = require_project_dir(root)
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root, shared=True):
        require_no_journal(root)
        item, asset = _find(installed, bundle_name, asset_id)
        if not overridden_files(root, item.bundle, asset):
            raise SelectionError(f"no override found for {selector}", fix="List overrides with `devkit override list`")
        receipt = read_receipt(root)
        record = receipt.overrides.get(bundle_name, {}).get(asset_id) if receipt is not None else None
        current = upstream_digest(item.bundle, asset)
        files: list[OverrideFileDiff] = []
        for rel in asset_files(item.bundle, asset):
            upstream = _text(item.bundle.root / rel)
            overridden = has_override(root, bundle_name, rel)
            diff = (
                _diff(upstream, _text(root / override_rel(bundle_name, rel)), f"upstream/{rel}", f"override/{rel}")
                if overridden
                else None
            )
            upstream_diff = _diff(
                _text(root / baseline_rel(bundle_name, rel)), upstream, f"baseline/{rel}", f"upstream/{rel}"
            )
            if overridden or upstream_diff:
                files.append(OverrideFileDiff(rel, diff, upstream_diff))
        return OverrideDiff(
            bundle=bundle_name,
            asset=asset_id,
            relative_path=primary_path(item.bundle, asset),
            drift_detected=record is not None and record.baseline_upstream_sha256 != current,
            baseline_upstream_sha256=record.baseline_upstream_sha256 if record is not None else None,
            current_upstream_sha256=current,
            files=files,
        )


def override_statuses(installed: list[InstalledBundle], receipt: Receipt | None) -> list[OverrideStatus]:
    """Every tracked override with its current upstream digest (``None`` when the bundle or asset is gone)."""
    bundles = {item.bundle.name: item.bundle for item in installed}
    results: list[OverrideStatus] = []
    for bundle_name, records in sorted((receipt.overrides if receipt is not None else {}).items()):
        bundle = bundles.get(bundle_name)
        for asset_id, record in sorted(records.items()):
            asset = bundle.asset(asset_id) if bundle is not None else None
            current = upstream_digest(bundle, asset) if bundle is not None and asset is not None else None
            results.append(
                OverrideStatus(
                    bundle_name, asset_id, record.kind, record.relative_path, record.baseline_upstream_sha256, current
                )
            )
    return results


def list_overrides(root: Path, installed: list[InstalledBundle]) -> list[OverrideStatus]:
    """Every tracked override of the project with its drift status."""
    root = require_project_dir(root)
    with project_lock(root, shared=True):
        return override_statuses(installed, read_receipt(root))
