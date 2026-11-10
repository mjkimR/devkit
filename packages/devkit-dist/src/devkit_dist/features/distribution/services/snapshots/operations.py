"""Snapshot destination, staging validation and consumer-next-action policy."""

from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from devkit_core.base.errors import UnsafePathError
from devkit_core.core.paths import normalize_relpath

from devkit_dist.features.distribution.models.snapshots import (
    SnapshotCandidate,
    SnapshotConflictError,
    SnapshotInvalidError,
    SnapshotResult,
)
from devkit_dist.features.distribution.repositories.snapshots import read_tree, symlinked_ancestor
from devkit_dist.features.distribution.services.bundles import load_bundle
from devkit_dist.features.distribution.services.snapshots.provenance import file_changes, load_provenance

PROTECTED = frozenset({".git", ".devkit", ".agents", ".claude", ".codex"})


def destination_path(root: Path, destination: Path, source: Path) -> Path:
    requested = destination if destination.is_absolute() else root / destination
    try:
        rel = requested.relative_to(root).as_posix()
        parts = normalize_relpath(rel, canonical=True).parts
    except (ValueError, UnsafePathError) as exc:
        linked = symlinked_ancestor(requested)
        try:
            resolved = requested.resolve()
        except (OSError, RuntimeError):  # Python 3.12 raises RuntimeError for a symlink loop
            linked = None
        if linked is not None and resolved.is_relative_to(root):
            raise SnapshotInvalidError(
                f"snapshot destination path has a symlinked component: {linked}",
                fix=f"Pass the resolved destination path instead: {resolved}",
            ) from exc
        raise SnapshotInvalidError("snapshot destination must be a new directory inside the consumer root") from exc
    if any(part.casefold() in PROTECTED for part in parts) or parts[0].casefold() == "agents.md":
        raise SnapshotInvalidError("snapshot destination overlaps Git, devkit or agent state")
    path = root
    for part in parts:
        path /= part
        if path.is_symlink():
            raise SnapshotInvalidError(f"snapshot destination has a symlinked component: {path}")
        if path != requested and (path / "snapshot.json").exists():
            raise SnapshotConflictError("snapshot destination is nested inside another snapshot")
    physical, origin = requested.resolve(), source.resolve()
    if physical.is_relative_to(origin) or origin.is_relative_to(physical):
        raise SnapshotInvalidError("snapshot destination and source must not overlap")
    return requested


def validate_package(root: Path) -> None:
    record = load_provenance(read_tree(root))
    for name, item in record["bundles"].items():
        resource = root / "src" / Path(*item["module"].split(".")) / "bundle"
        bundle = load_bundle(resource)
        if bundle.name != name or bundle.version != item["version"]:
            raise SnapshotInvalidError("staged bundle identity differs from provenance")


def result(
    root: Path,
    destination: Path,
    candidate: SnapshotCandidate,
    *,
    previous: dict[str, Any] | None,
    old_files: dict,
    preview: bool,
    selected: set[str],
) -> SnapshotResult:
    changes = file_changes(old_files, candidate.files)
    changed = any(changes.values())
    creating = previous is None
    status = "created" if creating else "preview" if preview else "updated" if changed else "unchanged"
    bundles = {name: item["version"] for name, item in candidate.provenance["bundles"].items()}
    removed = sorted((set(previous["bundles"]) - set(bundles)) & selected) if previous else []
    packaging_changed = old_files.get("pyproject.toml") != candidate.files["pyproject.toml"]
    package = candidate.provenance["package"]
    actions: list[dict[str, str]] = []
    relative = destination.relative_to(root).as_posix()
    if creating:
        upstream = candidate.provenance["source"]["name"]
        actions.extend(
            [
                {
                    "code": "SNAPSHOT_REPLACE_PROVIDER",
                    "command": f"uv remove --dev {shlex.quote(upstream)}",
                    "detail": "Run --dev only for a direct dev-group requirement; skip when absent. Use the owning group for other direct requirements and resolve transitive origin requirements separately",
                },
                {"code": "SNAPSHOT_INSTALL_LOCAL", "command": f"uv add --dev --editable {shlex.quote(relative)}"},
            ]
        )
    elif packaging_changed:
        actions.append(
            {"code": "SNAPSHOT_REINSTALL_PACKAGE", "command": f"uv sync --reinstall-package {shlex.quote(package)}"}
        )
    actions.extend(
        {"code": "SNAPSHOT_DESELECT_REMOVED", "command": f"uv run devkit remove {shlex.quote(name)}"}
        for name in removed
    )
    actions.append({"code": "SNAPSHOT_SYNC", "command": "uv run devkit sync"})
    return SnapshotResult(
        status=status,
        code=f"BUNDLE_SNAPSHOT_{status.upper()}",
        destination=relative,
        package=package,
        bundles=bundles,
        current_digest=previous["digest"] if previous else None,
        candidate_digest=candidate.digest,
        changes=changes,
        packaging_changed=packaging_changed,
        removed_selected=removed,
        actions=actions,
    )
