"""Results of distribution operations: frozen dataclasses whose ``to_dict()`` is the JSON the CLI prints.

Records shared with the receipt (``AssetRecord``, ``PackageRecord``,
``Selection``, ...) are the ``devkit_dist.features.project.repositories.receipt`` types themselves; the
``*_json`` functions here are their one JSON form, used by the receipt writer
and every result alike.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from devkit.advisory import AdvisoryError

from devkit_dist.features.distribution.models.drift import Drift
from devkit_dist.features.distribution.models.unprojected import Unprojected
from devkit_dist.features.project.models.invocation import AGENT_INVOCATION
from devkit_dist.features.project.models.receipt import (
    AssetRecord,
    OverrideRecord,
    PackageRecord,
    SeededRecord,
    Selection,
    ToolRecord,
)


def asset_json(asset: AssetRecord) -> dict[str, Any]:
    value: dict[str, Any] = {"bundle": asset.bundle, "id": asset.id, "kind": asset.kind, "paths": list(asset.paths)}
    if asset.entrypoints:
        value["entrypoints"] = list(asset.entrypoints)
    if asset.seeded:
        value["seeded"] = list(asset.seeded)
    return value


def package_json(package: PackageRecord) -> dict[str, str]:
    return {
        "package": package.package,
        "package_version": package.package_version,
        "bundle": package.bundle,
        "bundle_version": package.bundle_version,
    }


def selection_json(selection: Selection) -> dict[str, Any]:
    return {
        "agents": list(selection.agents),
        "presets": {name: list(values) for name, values in selection.presets.items()},
    }


def tool_json(tool: ToolRecord) -> dict[str, str]:
    return {"package": tool.package, "version": tool.version}


def seeded_json(seeded: tuple[SeededRecord, ...]) -> list[dict[str, str]]:
    return [{"bundle": item.bundle, "id": item.id, "path": item.path} for item in seeded]


def overrides_json(overrides: Mapping[str, Mapping[str, OverrideRecord]]) -> dict[str, dict[str, dict[str, str]]]:
    return {
        bundle: {
            asset_id: {
                "kind": record.kind,
                "relative_path": record.relative_path,
                "baseline_upstream_sha256": record.baseline_upstream_sha256,
                "override_sha256": record.override_sha256,
            }
            for asset_id, record in assets.items()
        }
        for bundle, assets in overrides.items()
    }


@dataclass(frozen=True)
class Action:
    """One planned write of a synchronization."""

    path: str
    # ``create`` | ``update`` | ``remove`` | ``seed``
    action: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "action": self.action}


@dataclass(frozen=True)
class Unselected:
    """An installed bundle the synchronization did not deploy; ``opted_out`` when ``[presets]`` sets it to ``false``."""

    bundle: str
    package: str
    presets: list[str]
    default_preset: str | None
    opted_out: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle": self.bundle,
            "package": self.package,
            "presets": list(self.presets),
            "default_preset": self.default_preset,
            "opted_out": self.opted_out,
        }


@dataclass
class SyncResult:
    """What ``devkit sync`` (``add``, ``remove``) planned and, unless ``dry_run``, wrote.

    ``notices`` are coded ``SyncNotice`` entries (an orphaned file, a tool
    version change, post-sync extension output); they never fail the sync.
    """

    dry_run: bool
    selection: Selection
    packages: list[PackageRecord]
    assets: list[AssetRecord]
    actions: list[Action]
    drift: list[Drift]
    stray: list[str]
    unprojected: list[Unprojected]
    unselected: list[Unselected]
    notices: list[AdvisoryError] = field(default_factory=list)
    execution_environment: str = "local"

    def to_dict(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "execution_environment": self.execution_environment,
            "selection": selection_json(self.selection),
            "packages": [package_json(item) for item in self.packages],
            "assets": [asset_json(asset) for asset in self.assets],
            "actions": [item.to_dict() for item in self.actions],
            "drift": [item.to_dict() for item in self.drift],
            "stray": list(self.stray),
            "unprojected": [item.to_dict() for item in self.unprojected],
            "unselected": [item.to_dict() for item in self.unselected],
            "notices": [notice.to_dict() for notice in self.notices],
        }


@dataclass(frozen=True)
class Instruction:
    """An instruction of a bundle's context: its absolute path and raw YAML header (never the body)."""

    path: str
    header: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "header": self.header}


@dataclass(frozen=True)
class ContextDocument:
    """A project document of a bundle's declared context directory: its absolute path and frontmatter ``title`` and
    ``summary``, each ``None`` when it cannot be read as a string."""

    path: str
    title: str | None
    summary: str | None

    def to_dict(self) -> dict[str, str | None]:
        return {"path": self.path, "title": self.title, "summary": self.summary}


@dataclass(frozen=True)
class ContextResult:
    """``devkit get-context``: a bundle's constitution, instruction catalog and context documents."""

    bundle: str
    constitution: str | None
    instructions: list[Instruction]
    documents: list[ContextDocument] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle": self.bundle,
            "constitution": self.constitution,
            "instructions": [item.to_dict() for item in self.instructions],
            "documents": [item.to_dict() for item in self.documents],
        }


@dataclass(frozen=True)
class PlaybookCandidate:
    """A playbook's metadata and readable path; ``score`` is set once it is ranked. Only ``name`` and ``description``
    are searched; ``aliases`` are identity metadata (previous asset IDs)."""

    bundle: str
    id: str
    name: str
    description: str
    aliases: list[str]
    path: str
    score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "bundle": self.bundle,
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "aliases": list(self.aliases),
            "path": self.path,
        }
        if self.score is not None:
            value["score"] = self.score
        return value


@dataclass(frozen=True)
class SearchResult:
    """``devkit playbook search``: ranked candidates within the byte budget; ``truncated`` when some were cut.

    ``mode`` is the ranking that ran (``lexical``, ``dense`` or ``hybrid``; ``auto`` resolves to one of them).
    """

    query: str
    mode: str
    results: list[PlaybookCandidate]
    truncated: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "mode": str(self.mode),
            "results": [item.to_dict() for item in self.results],
            "truncated": self.truncated,
        }


@dataclass(frozen=True)
class OverrideStatus:
    """A tracked override; ``current_upstream_sha256`` is ``None`` when its bundle or asset is gone."""

    bundle: str
    asset: str
    kind: str
    relative_path: str
    baseline_upstream_sha256: str
    current_upstream_sha256: str | None

    @property
    def drift_detected(self) -> bool:
        return (
            self.current_upstream_sha256 is not None and self.current_upstream_sha256 != self.baseline_upstream_sha256
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle": self.bundle,
            "asset": self.asset,
            "kind": self.kind,
            "relative_path": self.relative_path,
            "drift_detected": self.drift_detected,
        }


@dataclass(frozen=True)
class OverrideFileDiff:
    path: str
    # Unified diff upstream -> override; ``None`` when this file is not overridden.
    diff: str | None
    # Unified diff baseline -> upstream; ``None`` without a baseline copy.
    upstream_diff: str | None

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "diff": self.diff, "upstream_diff": self.upstream_diff}


@dataclass(frozen=True)
class OverrideDiff:
    """``devkit override diff``: per file, upstream vs override and recorded baseline vs current upstream."""

    bundle: str
    asset: str
    relative_path: str
    drift_detected: bool
    baseline_upstream_sha256: str | None
    current_upstream_sha256: str
    files: list[OverrideFileDiff]

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle": self.bundle,
            "asset": self.asset,
            "relative_path": self.relative_path,
            "drift_detected": self.drift_detected,
            "files": [item.to_dict() for item in self.files],
        }


@dataclass(frozen=True)
class OverrideChange:
    """``devkit override create|remove|accept``: what changed under ``.devkit/overrides/``.

    ``notices`` are those of the synchronization ``create`` and ``remove`` run
    (post-sync extension output included); ``accept`` does not synchronize.
    """

    bundle: str
    asset: str
    # ``created`` | ``removed`` | ``accepted``
    status: str
    # Workspace paths written (create) or deleted (remove).
    paths: list[str]
    # The new baseline digest (accept).
    accepted_upstream_sha256: str | None = None
    notices: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "bundle": self.bundle,
            "asset": self.asset,
            "status": self.status,
            "paths": list(self.paths),
        }
        if self.accepted_upstream_sha256 is not None:
            value["accepted_upstream_sha256"] = self.accepted_upstream_sha256
        value["notices"] = [notice.to_dict() for notice in self.notices]
        return value


@dataclass(frozen=True)
class ConfigurationReport:
    """``devkit config show --effective``: effective checkout preferences and their sources.

    ``notices``: warnings that change no exit code (an unsupported ``[presentation] language`` resolved to ``en``).
    """

    configuration: dict[str, Any]
    sources: dict[str, str]
    execution_environment: str
    presentation_language: dict[str, Any]
    notices: list[AdvisoryError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "configuration": self.configuration,
            "sources": self.sources,
            "execution_environment": self.execution_environment,
            "presentation_language": self.presentation_language,
            "notices": [notice.to_dict() for notice in self.notices],
        }


@dataclass(frozen=True)
class PlaybookResult:
    """An exact procedure with effective content identity and context requirements; ``alias`` is the declared alias
    the request named (``None`` for the exact asset ID)."""

    bundle: str
    id: str
    name: str
    description: str
    aliases: list[str]
    body: str
    path: str
    sha256: str
    alias: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle": self.bundle,
            "id": self.id,
            "alias": self.alias,
            "name": self.name,
            "description": self.description,
            "aliases": list(self.aliases),
            "body": self.body,
            "source": {"path": self.path, "sha256": self.sha256},
            "context": {
                "bundle": self.bundle,
                "argv": [*AGENT_INVOCATION.split(), "get-context", self.bundle],
                "policy": "once-per-agent-context",
            },
        }
