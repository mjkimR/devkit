"""Immutable installation receipt contracts shared by project readers and features."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

RECEIPT_PATH = ".devkit/installation.json"
SYNC_COMMAND = "devkit sync"  # restores missing managed copies (the fix of a missing asset file)
CONFIG_PATH = ".devkit/config.toml"
MANAGED_PATH = ".devkit/managed"
OVERRIDES_PATH = ".devkit/overrides"
AGENTS_FILE = "AGENTS.md"
GUIDANCE_START = "<!-- DEVKIT:START -->"
GUIDANCE_END = "<!-- DEVKIT:END -->"
SCHEMA = 1
FILE_MODES = frozenset({0o644, 0o755})


@dataclass(frozen=True)
class PackageRecord:
    package: str
    package_version: str
    bundle: str
    bundle_version: str


@dataclass(frozen=True)
class Selection:
    agents: tuple[str, ...]
    presets: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class AssetRecord:
    """One synchronized asset. ``paths`` are the deployed files (an override replaces its managed copy)."""

    bundle: str
    id: str
    kind: str
    paths: tuple[str, ...]
    entrypoints: tuple[str, ...] = ()
    seeded: tuple[str, ...] = ()

    def files(self, suffix: str = "") -> tuple[str, ...]:
        """``entrypoints`` then ``paths`` ending in ``suffix``, without duplicates."""
        out: list[str] = []
        for rel in (*self.entrypoints, *self.paths):
            if rel.endswith(suffix) and rel not in out:
                out.append(rel)
        return tuple(out)


@dataclass(frozen=True)
class FileRecord:
    sha256: str
    mode: int

    def matches(self, data: bytes) -> bool:
        """Whether ``data`` has the recorded SHA-256."""
        return hashlib.sha256(data).hexdigest() == self.sha256


@dataclass(frozen=True)
class ToolRecord:
    package: str
    version: str


@dataclass(frozen=True)
class OverrideRecord:
    kind: str
    relative_path: str
    baseline_upstream_sha256: str
    override_sha256: str


@dataclass(frozen=True)
class SeededRecord:
    bundle: str
    id: str
    path: str


@dataclass(frozen=True)
class HostHookRecord:
    """One owned matcher group in a shared host configuration file; host code defines its rendering."""

    host: str
    asset: str
    event: str
    handler: str
    command: str
    matcher: str
    timeout: int


@dataclass(frozen=True)
class Receipt:
    """A validated receipt. Mappings are read-only views."""

    schema: int
    packages: tuple[PackageRecord, ...]
    selection: Selection
    asset_records: tuple[AssetRecord, ...]
    file_records: Mapping[str, FileRecord]
    tool: ToolRecord | None = None
    overrides: Mapping[str, Mapping[str, OverrideRecord]] = field(default_factory=lambda: MappingProxyType({}))
    seeded: tuple[SeededRecord, ...] = ()
    guidance_block: str | None = None
    host_hooks: tuple[HostHookRecord, ...] = ()
    execution_environment: str | None = None

    def assets(self, kind: str | None = None) -> tuple[AssetRecord, ...]:
        """Asset records in receipt order, optionally only those of one ``kind``."""
        if kind is None:
            return self.asset_records
        return tuple(asset for asset in self.asset_records if asset.kind == kind)

    def file(self, path: str) -> FileRecord | None:
        """The ``files`` entry of a workspace-relative path, if the receipt owns it."""
        return self.file_records.get(path)

    def file_hash(self, path: str) -> str | None:
        """The recorded SHA-256 of a workspace-relative path, if the receipt owns it."""
        record = self.file_records.get(path)
        return record.sha256 if record is not None else None
