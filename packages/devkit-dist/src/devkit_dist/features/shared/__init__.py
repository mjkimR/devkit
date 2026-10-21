"""Public immutable shared-artifact API and installed adapter selection."""

from devkit_dist.features.shared.models.api import (
    Artifact,
    ArtifactMetadata,
    Page,
    PutRequest,
    RepositoryContext,
    SharedArtifactAdapter,
    SweepResult,
)
from devkit_dist.features.shared.usecases.service import adapter

__all__ = [
    "Artifact",
    "ArtifactMetadata",
    "Page",
    "PutRequest",
    "RepositoryContext",
    "SharedArtifactAdapter",
    "SweepResult",
    "adapter",
]
