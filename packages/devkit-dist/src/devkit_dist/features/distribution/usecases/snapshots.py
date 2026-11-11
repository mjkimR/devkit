"""Typed source snapshot creation and explicit refresh application operations."""

from __future__ import annotations

from pathlib import Path

from devkit_core.base.errors import ArgumentError
from devkit_core.base.usecase import BaseUseCase

from devkit_dist.features.distribution.models.snapshots import SnapshotConflictError, SnapshotResult
from devkit_dist.features.distribution.repositories.snapshots import read_tree, replace_snapshot, snapshot_lock
from devkit_dist.features.distribution.services.installation.config import read_config
from devkit_dist.features.distribution.services.installation.receipt import read_receipt
from devkit_dist.features.distribution.services.snapshots.operations import destination_path, result, validate_package
from devkit_dist.features.distribution.services.snapshots.provenance import load_provenance
from devkit_dist.features.distribution.services.snapshots.source import prepare_candidate


class CreateBundleSnapshot(BaseUseCase):
    """Create a complete local content wrapper without installing or synchronizing it."""

    def execute(self, root: Path, source: Path, destination: Path, package: str) -> SnapshotResult:
        root = root.resolve()
        source = source.absolute()
        destination = destination_path(root, destination, source)
        with snapshot_lock(root):
            if destination.exists():
                raise SnapshotConflictError("snapshot creation requires a new destination directory")
            candidate = prepare_candidate(source, package)
            outcome = result(root, destination, candidate, previous=None, old_files={}, preview=False, selected=set())
            replace_snapshot(destination, candidate.files, validate_package, creating=True)
            return outcome


class RefreshBundleSnapshot(BaseUseCase):
    """Preview sources (neither digest) or apply only the reviewed current/candidate digest pair (both digests)."""

    def execute(
        self,
        root: Path,
        destination: Path,
        source: Path,
        *,
        expect: str | None = None,
        candidate: str | None = None,
    ) -> SnapshotResult:
        check = _preview(expect, candidate)
        root = root.resolve()
        source = source.absolute()
        destination = destination_path(root, destination, source)
        with snapshot_lock(root):
            old_files = read_tree(destination)
            previous = load_provenance(old_files)
            prepared = prepare_candidate(source, previous["package"])
            if prepared.provenance["source"]["name"] != previous["source"]["name"]:
                raise SnapshotConflictError("refresh source provider does not match the recorded provider")
            if not check and (expect != previous["digest"] or candidate != prepared.digest):
                raise SnapshotConflictError(
                    "refresh apply requires matching --expect and --candidate digests; preview again"
                )
            config = read_config(root)
            selected = set(config.presets)
            receipt = read_receipt(root, check_disk=False)
            if receipt is not None:
                selected.update(receipt.selection.presets)
            outcome = result(
                root, destination, prepared, previous=previous, old_files=old_files, preview=check, selected=selected
            )
            if not check and any(outcome.changes.values()):
                replace_snapshot(
                    destination, prepared.files, validate_package, creating=False, previous_files=old_files
                )
            return outcome


def _preview(expect: str | None, candidate: str | None) -> bool:
    """Whether refresh previews (neither digest); ``ArgumentError`` naming the missing flag when only one is given."""
    if expect is None and candidate is None:
        return True
    if expect is not None and candidate is not None:
        return False
    missing = "--candidate" if candidate is None else "--expect"
    raise ArgumentError(
        f"refresh apply requires both --expect and --candidate; {missing} is missing",
        target_files=[missing],
        fix="Preview without --expect and --candidate, then pass both digests it returns",
    )
