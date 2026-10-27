"""Shared space artifacts: listing and reading live shared artifacts (such as proposal reviews)."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_core.base.usecase import BaseUseCase
from devkit_dist.features.shared.models.api import GENERATION

from devkit_viewer.features.browse.models.errors import ReadError
from devkit_viewer.features.browse.models.repository import Repository
from devkit_viewer.features.browse.repositories.shared_space import get_artifact, local_adapter

UNAVAILABLE = ("VIEWER_SHARED_UNAVAILABLE", "shared space requires the local adapter")


class ListSharedArtifactsUseCase(BaseUseCase):
    def execute(
        self,
        repo: Repository,
        *,
        kind: str | None = None,
        slug: str | None = None,
    ) -> dict[str, Any]:
        """List live shared artifacts, newest first; an unreadable artifact is left out, an unusable store lists none."""
        try:
            entries = local_adapter(repo, *UNAVAILABLE).list_live(kind=kind, slug=slug, skip_unreadable=True)
        except (AdvisoryError, ReadError, OSError):
            return {"artifacts": []}
        items = [meta.to_dict() for meta in entries]
        items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
        return {"artifacts": items}


class ReadSharedArtifactUseCase(BaseUseCase):
    def execute(self, repo: Repository, generation_id: str) -> dict[str, Any]:
        """Read a specific shared artifact by generation ID."""
        if not GENERATION.fullmatch(generation_id):
            raise ReadError(HTTPStatus.BAD_REQUEST, "VIEWER_SHARED_INVALID", "invalid artifact generation")
        artifact = get_artifact(
            repo, generation_id, unavailable=UNAVAILABLE, not_found="artifact not found", expired="artifact expired"
        )
        return {
            "metadata": artifact.metadata.to_dict(),
            "content": artifact.content,
            "artifact_uri": artifact.metadata.artifact_uri,
        }
