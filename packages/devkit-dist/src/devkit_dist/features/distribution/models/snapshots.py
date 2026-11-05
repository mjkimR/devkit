"""Bundle source snapshot values and actionable failures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from devkit_dist.features.distribution.models.content import Content
from devkit_dist.features.distribution.models.errors import DistributionError


class SnapshotInvalidError(DistributionError):
    """Snapshot metadata or a requested filesystem path is invalid."""

    code = "BUNDLE_SNAPSHOT_INVALID"
    input_error = True
    fix = "Use a valid source checkout and a snapshot destination inside the consumer root"


class SnapshotUnsupportedError(SnapshotInvalidError):
    """The provider needs runtime code or an unsupported source layout."""

    code = "BUNDLE_SNAPSHOT_UNSUPPORTED"
    fix = "Use a static content-only provider with self-contained bundle resources; keep runtime dependencies separately installed"


class SnapshotConflictError(DistributionError):
    """Local content, reviewed digests or another snapshot operation prevent adoption."""

    code = "BUNDLE_SNAPSHOT_CONFLICT"
    input_error = True
    fix = "Keep consumer adaptations in devkit overrides, restore snapshot sources, then preview refresh and use both returned digests"


class SnapshotWriteError(DistributionError):
    """A staged snapshot write failed; the prior directory is restored when possible."""

    code = "BUNDLE_SNAPSHOT_WRITE_FAILED"
    fix = "Resolve the reported filesystem failure and retry; preserve any reported recovery backup"


@dataclass(frozen=True)
class SnapshotCandidate:
    """A complete wrapper payload and its path-free provenance."""

    files: dict[str, Content]
    provenance: dict[str, Any]

    @property
    def digest(self) -> str:
        return self.provenance["digest"]


@dataclass(frozen=True)
class SnapshotResult:
    """One JSON-only operation result; actions name commands the consumer runs next."""

    status: str
    code: str
    destination: str
    package: str
    bundles: dict[str, str]
    current_digest: str | None
    candidate_digest: str
    changes: dict[str, list[str]]
    packaging_changed: bool
    removed_selected: list[str]
    actions: list[dict[str, str]]

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "notices": []}
