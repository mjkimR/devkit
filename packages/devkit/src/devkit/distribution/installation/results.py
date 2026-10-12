"""JSON-shaped results of distribution operations (what the CLI prints and library callers receive)."""

from __future__ import annotations

from typing import NotRequired, TypedDict

from devkit.core.receipt import AssetRecord, PackageRecord


class ActionJSON(TypedDict):
    path: str
    # ``create`` | ``update`` | ``remove`` | ``seed``
    action: str


class PackageJSON(TypedDict):
    package: str
    package_version: str
    bundle: str
    bundle_version: str


class AssetJSON(TypedDict):
    bundle: str
    id: str
    kind: str
    paths: list[str]
    entrypoints: NotRequired[list[str]]
    seeded: NotRequired[list[str]]


class SelectionJSON(TypedDict):
    agents: list[str]
    presets: dict[str, list[str]]


class DriftJSON(TypedDict):
    bundle: str
    asset: str
    path: str
    message: str


class UnprojectedJSON(TypedDict):
    bundle: str
    asset: str
    agent: str


class UnselectedJSON(TypedDict):
    bundle: str
    package: str
    presets: list[str]
    default_preset: str | None


class SyncResult(TypedDict):
    dry_run: bool
    selection: SelectionJSON
    packages: list[PackageJSON]
    assets: list[AssetJSON]
    actions: list[ActionJSON]
    drift: list[DriftJSON]
    orphans: list[str]
    stray: list[str]
    unprojected: list[UnprojectedJSON]
    unselected: list[UnselectedJSON]
    notices: list[str]


class InstructionJSON(TypedDict):
    path: str
    header: str


class ContextResult(TypedDict):
    bundle: str
    constitution: str | None
    instructions: list[InstructionJSON]


class PlaybookCandidate(TypedDict):
    bundle: str
    id: str
    name: str
    description: str
    aliases: list[str]
    path: str
    score: NotRequired[float]


class SearchResult(TypedDict):
    query: str
    results: list[PlaybookCandidate]
    truncated: bool


class OverrideStatus(TypedDict):
    bundle: str
    asset: str
    kind: str
    relative_path: str
    baseline_upstream_sha256: str
    current_upstream_sha256: str | None
    drift_detected: bool


class OverrideFileDiff(TypedDict):
    path: str
    # Unified diff upstream -> override; ``None`` when this file is not overridden.
    diff: str | None
    # Unified diff baseline -> upstream; ``None`` without a baseline copy.
    upstream_diff: str | None


class OverrideDiff(TypedDict):
    bundle: str
    asset: str
    relative_path: str
    drift_detected: bool
    baseline_upstream_sha256: str | None
    current_upstream_sha256: str
    files: list[OverrideFileDiff]


class OverrideChange(TypedDict):
    bundle: str
    asset: str
    # ``created`` | ``removed`` | ``accepted``
    status: str
    # Workspace paths written (create) or deleted (remove).
    paths: list[str]
    # The new baseline digest (accept).
    accepted_upstream_sha256: NotRequired[str]


def asset_json(asset: AssetRecord) -> AssetJSON:
    value: AssetJSON = {"bundle": asset.bundle, "id": asset.id, "kind": asset.kind, "paths": list(asset.paths)}
    if asset.entrypoints:
        value["entrypoints"] = list(asset.entrypoints)
    if asset.seeded:
        value["seeded"] = list(asset.seeded)
    return value


def package_json(package: PackageRecord) -> PackageJSON:
    return {
        "package": package.package,
        "package_version": package.package_version,
        "bundle": package.bundle,
        "bundle_version": package.bundle_version,
    }
