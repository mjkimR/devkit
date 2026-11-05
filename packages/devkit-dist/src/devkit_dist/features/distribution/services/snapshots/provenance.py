"""Canonical snapshot provenance and source-drift comparison."""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

from devkit_core.base.errors import UnsafePathError
from devkit_core.core.paths import normalize_relpath

from devkit_dist.features.distribution.models.content import Content, json_content, sha256, signature
from devkit_dist.features.distribution.models.snapshots import SnapshotConflictError, SnapshotInvalidError
from devkit_dist.features.project.models.strict_json import strict_json_loads

DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def inventory(files: dict[str, Content]) -> dict[str, dict[str, str | int]]:
    """Ordered file identities; snapshot.json never hashes itself."""
    return {rel: {"sha256": sha256(item.data), "mode": item.mode} for rel, item in sorted(files.items())}


def seal(metadata: dict[str, Any], files: dict[str, Content]) -> dict[str, Any]:
    record = {**metadata, "files": inventory(files)}
    return {**record, "digest": sha256(json_content(record).data)}


def load_provenance(files: dict[str, Content]) -> dict[str, Any]:
    """Verify schema, aggregate and payload before considering a refresh."""
    try:
        data = strict_json_loads(files["snapshot.json"].data, reject_constants=True)
        if not isinstance(data, dict) or set(data) != {"schema", "package", "source", "bundles", "files", "digest"}:
            raise ValueError("expected schema-1 snapshot fields")
        if type(data["schema"]) is not int or data["schema"] != 1:
            raise ValueError("unsupported snapshot schema")
        if not isinstance(data["package"], str) or not isinstance(data["source"], dict):
            raise ValueError("invalid source or local package identity")
        source = data["source"]
        if set(source) != {"name", "version", "commit", "requires_python", "metadata_sha256"}:
            raise ValueError("invalid source identity fields")
        if not all(isinstance(source[k], str) and source[k] for k in ("name", "version", "requires_python")):
            raise ValueError("source identity must be static strings")
        if source["commit"] is not None and not re.fullmatch(r"[0-9a-f]{40,64}", source["commit"]):
            raise ValueError("invalid source commit")
        if not DIGEST.fullmatch(source["metadata_sha256"]):
            raise ValueError("invalid metadata digest")
        if not isinstance(data["bundles"], dict) or not data["bundles"]:
            raise ValueError("expected nonempty bundle identities")
        for name, item in data["bundles"].items():
            if not isinstance(name, str) or not isinstance(item, dict) or set(item) != {"version", "module"}:
                raise ValueError("invalid bundle identity")
            if not all(isinstance(item[k], str) and item[k] for k in ("version", "module")):
                raise ValueError("invalid bundle version or module")
        if not isinstance(data["files"], dict):
            raise ValueError("invalid file inventory")
        for rel, item in data["files"].items():
            normalize_relpath(rel, canonical=True)
            if rel == "snapshot.json" or not isinstance(item, dict) or set(item) != {"sha256", "mode"}:
                raise ValueError("invalid payload inventory entry")
            if not isinstance(item["sha256"], str) or not DIGEST.fullmatch(item["sha256"]):
                raise ValueError("invalid payload digest")
            if type(item["mode"]) is not int or item["mode"] not in (0o644, 0o755):
                raise ValueError("invalid executable mode")
        digest = data["digest"]
        if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
            raise ValueError("invalid aggregate digest")
        if sha256(json_content({k: v for k, v in data.items() if k != "digest"}).data) != digest:
            raise ValueError("aggregate digest mismatch")
    except (KeyError, ValueError, TypeError, UnicodeError, UnsafePathError) as exc:
        raise SnapshotInvalidError(f"invalid snapshot.json: {exc}") from exc
    actual = inventory({rel: value for rel, value in files.items() if rel != "snapshot.json"})
    if actual != data["files"]:
        paths = sorted(key for key in actual.keys() | data["files"].keys() if actual.get(key) != data["files"].get(key))
        raise SnapshotConflictError("snapshot has authored changes", *paths, target_files=paths)
    return data


def file_changes(old: dict[str, Content], new: dict[str, Content]) -> dict[str, list[str]]:
    """Deterministic changes include bytes and executable modes."""
    return {
        "added": sorted(new.keys() - old.keys()),
        "modified": sorted(k for k in old.keys() & new.keys() if signature(old[k]) != signature(new[k])),
        "removed": sorted(old.keys() - new.keys()),
    }


def validate_relative_inventory(files: dict[str, Content]) -> None:
    """Generated names are canonical and contain no file/directory collision."""
    for rel in files:
        normalize_relpath(rel, canonical=True)
        if any(parent.as_posix() in files for parent in PurePosixPath(rel).parents):
            raise SnapshotInvalidError(f"snapshot file/directory collision: {rel}")
