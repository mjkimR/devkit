"""``devkit override``: create, review, accept, remove and list project overrides.

``create`` and ``remove`` change files under ``.devkit/overrides/`` and then
synchronize, under one project lock: when the synchronization fails, the
override files are put back as they were. ``accept`` advances the recorded
baseline through the journal.
"""

from __future__ import annotations

import dataclasses
import difflib
from pathlib import Path
from types import MappingProxyType

from devkit.core.receipt import OverrideRecord, Receipt

from ..bundles.common import SLUG, BundleError
from ..bundles.manifest import Asset
from .config import effective_selection, read_config
from .discovery import InstalledBundle
from .hooks import run_post_sync
from .overrides import (
    asset_files,
    baseline_rel,
    has_override,
    overridden_files,
    override_rel,
    primary_path,
    upstream_digest,
)
from .receipt import read_receipt, receipt_content
from .results import OverrideChange, OverrideDiff, OverrideFileDiff, OverrideStatus, SyncResult
from .sync import project_root, sync_locked
from .transaction import apply_changes, project_lock, replace_file, require_no_journal
from .workspace import OVERRIDES, RECEIPT, Content, checked_path, normal_mode


def _parse_selector(selector: str) -> tuple[str, str]:
    bundle, separator, asset = selector.partition(":")
    if not separator or not bundle or not asset:
        raise BundleError(f"expected bundle:asset selector (e.g. starter:development): {selector}")
    if not SLUG.fullmatch(bundle) or not SLUG.fullmatch(asset):
        raise BundleError(f"bundle and asset must be lowercase slugs: {selector}")
    return bundle, asset


def _find(installed: list[InstalledBundle], bundle_name: str, asset_id: str) -> tuple[InstalledBundle, Asset]:
    item = next((b for b in installed if b.bundle.name == bundle_name), None)
    if item is None:
        raise BundleError(f"bundle is not installed: {bundle_name}")
    asset = item.bundle.asset(asset_id)
    if asset is None:
        raise BundleError(f"asset not found in {bundle_name}: {asset_id}")
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
        _prune_overrides(self.root, name)

    def restore(self) -> None:
        for name, before in reversed(self.saved.items()):
            replace_file(checked_path(self.root, name), before)
            if before is None:
                _prune_overrides(self.root, name)


def _prune_overrides(root: Path, name: str) -> None:
    """Remove directories left empty under ``.devkit/overrides/``, that directory included."""
    stop = (root / OVERRIDES).parent
    parent = (root / name).parent
    while parent != stop and parent.is_relative_to(stop):
        try:
            parent.rmdir()
        except OSError:
            return
        parent = parent.parent


def _require_overridable(root: Path, installed: list[InstalledBundle], item: InstalledBundle, asset: Asset) -> None:
    name = item.bundle.name
    selection = effective_selection(installed, read_config(root))
    if name not in selection:
        raise BundleError(f"bundle is not selected: {name}; select it with 'devkit add {name}' first")
    if asset.id not in item.bundle.select(selection[name]):
        raise BundleError(f"asset {name}:{asset.id} is not part of the selected presets {selection[name]}")
    if asset.seeded:
        raise BundleError(f"{name}:{asset.id} is a seeded asset; its files are project-owned, edit them directly")


def _after_sync(root: Path, result: SyncResult) -> None:
    result["notices"].extend(run_post_sync(root, dict(result)))


def create_override(
    root: Path, installed: list[InstalledBundle], selector: str, *, force: bool = False
) -> OverrideChange:
    """Copy every upstream file of an asset into ``.devkit/overrides/`` (and its baseline), then synchronize."""
    root = project_root(root)
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root):
        require_no_journal(root)
        item, asset = _find(installed, bundle_name, asset_id)
        _require_overridable(root, installed, item, asset)
        files = asset_files(item.bundle, asset)
        if not force:
            existing = [rel for rel in files if (root / override_rel(bundle_name, rel)).exists()]
            if existing:
                raise BundleError(f"override already exists: {override_rel(bundle_name, existing[0])}")
        undo = _Undo(root)
        try:
            for rel in files:
                path = item.bundle.root / rel
                content = Content(path.read_bytes(), normal_mode(path.stat().st_mode))
                undo.write(override_rel(bundle_name, rel), content)
                undo.write(baseline_rel(bundle_name, rel), content)
            result = sync_locked(root, installed)
        except BaseException:
            undo.restore()
            raise
    _after_sync(root, result)
    return {
        "bundle": bundle_name,
        "asset": asset_id,
        "status": "created",
        "paths": [override_rel(bundle_name, rel) for rel in files],
    }


def remove_override(root: Path, installed: list[InstalledBundle], selector: str) -> OverrideChange:
    """Delete an asset's override and baseline files, then synchronize the pristine upstream files."""
    root = project_root(root)
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root):
        require_no_journal(root)
        _, asset = _find(installed, bundle_name, asset_id)
        names: list[str] = []
        for _, source in asset.sources:
            for rel_of in (override_rel, baseline_rel):
                base = root / rel_of(bundle_name, source)
                found = sorted(p for p in base.rglob("*") if p.is_file()) if base.is_dir() else [base]
                names.extend(p.relative_to(root).as_posix() for p in found if p.is_file() or p.is_symlink())
        if not any(name.startswith(f"{OVERRIDES}/{bundle_name}/") for name in names):
            raise BundleError(f"no override found for {selector}")
        undo = _Undo(root)
        try:
            for name in names:
                undo.delete(name)
            result = sync_locked(root, installed)
        except BaseException:
            undo.restore()
            raise
    _after_sync(root, result)
    return {
        "bundle": bundle_name,
        "asset": asset_id,
        "status": "removed",
        "paths": [name for name in names if not name.startswith(baseline_rel(bundle_name, ""))],
    }


def _tracked(receipt: Receipt | None, bundle: str, asset: str, selector: str) -> OverrideRecord:
    record = receipt.overrides.get(bundle, {}).get(asset) if receipt is not None else None
    if record is None:
        raise BundleError(
            f"{selector} has no tracked override; create one with 'devkit override create {selector}'"
            " (or run devkit sync if its files already exist)"
        )
    return record


def accept_override(root: Path, installed: list[InstalledBundle], selector: str) -> OverrideChange:
    """Record the current upstream files as the override's baseline (after reviewing ``override diff``)."""
    root = project_root(root)
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
            apply_changes(root, {RECEIPT: receipt_content(updated)})
        except BaseException:
            undo.restore()
            raise
    return {
        "bundle": bundle_name,
        "asset": asset_id,
        "status": "accepted",
        "paths": [],
        "accepted_upstream_sha256": current,
    }


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
    root = project_root(root)
    bundle_name, asset_id = _parse_selector(selector)
    with project_lock(root, shared=True):
        require_no_journal(root)
        item, asset = _find(installed, bundle_name, asset_id)
        if not overridden_files(root, item.bundle, asset):
            raise BundleError(f"no override found for {selector}")
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
                files.append({"path": rel, "diff": diff, "upstream_diff": upstream_diff})
        return {
            "bundle": bundle_name,
            "asset": asset_id,
            "relative_path": primary_path(item.bundle, asset),
            "drift_detected": record is not None and record.baseline_upstream_sha256 != current,
            "baseline_upstream_sha256": record.baseline_upstream_sha256 if record is not None else None,
            "current_upstream_sha256": current,
            "files": files,
        }


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
                {
                    "bundle": bundle_name,
                    "asset": asset_id,
                    "kind": record.kind,
                    "relative_path": record.relative_path,
                    "baseline_upstream_sha256": record.baseline_upstream_sha256,
                    "current_upstream_sha256": current,
                    "drift_detected": current is not None and current != record.baseline_upstream_sha256,
                }
            )
    return results


def list_overrides(root: Path, installed: list[InstalledBundle]) -> list[OverrideStatus]:
    root = project_root(root)
    with project_lock(root, shared=True):
        return override_statuses(installed, read_receipt(root))
