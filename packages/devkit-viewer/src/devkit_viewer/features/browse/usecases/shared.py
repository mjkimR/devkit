"""Shared space artifacts: listing and reading live shared artifacts (such as proposal reviews)."""

from __future__ import annotations

import os
from http import HTTPStatus
from typing import Any

from devkit.advisory import AdvisoryError
from devkit_core.base.usecase import BaseUseCase
from devkit_dist.features.project.repositories.local_config import read_effective_config
from devkit_dist.features.shared.models.api import GENERATION
from devkit_dist.features.shared.models.errors import ExpiredError, MissingError, SharedError, WorkspaceError
from devkit_dist.features.shared.repositories.local import LocalAdapter, discover

from devkit_viewer.features.browse.models.errors import ReadError
from devkit_viewer.features.browse.models.repository import Repository


def _local_adapter(repo: Repository) -> LocalAdapter:
    configured = read_effective_config(repo.root).values["shared"]["adapter"]
    if os.environ.get("DEVKIT_SHARED_ADAPTER", configured) != "local":
        raise ReadError(HTTPStatus.NOT_FOUND, "VIEWER_SHARED_UNAVAILABLE", "shared space requires the local adapter")
    return LocalAdapter(discover(repo.root))


class ListSharedArtifactsUseCase(BaseUseCase):
    def execute(
        self,
        repo: Repository,
        *,
        kind: str | None = None,
        slug: str | None = None,
    ) -> dict[str, Any]:
        """List live shared artifacts in the repository's shared store."""
        try:
            adapter = _local_adapter(repo)
        except (AdvisoryError, WorkspaceError, SharedError, ReadError, OSError):
            return {"artifacts": []}

        try:
            items = []
            with adapter._operation() as budget:
                now = adapter.clock()
                for path in adapter._paths(budget):
                    try:
                        artifact = adapter._read(path, budget)
                        m = artifact.metadata
                        if not m.live(now):
                            continue
                        if kind is not None and m.kind != kind:
                            continue
                        if slug is not None and m.slug != slug:
                            continue
                        items.append(m.to_dict())
                    except Exception:
                        continue
            items.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
            return {"artifacts": items}
        except Exception:
            return {"artifacts": []}


class ReadSharedArtifactUseCase(BaseUseCase):
    def execute(self, repo: Repository, generation_id: str) -> dict[str, Any]:
        """Read a specific shared artifact by generation ID."""
        if not GENERATION.fullmatch(generation_id):
            raise ReadError(HTTPStatus.BAD_REQUEST, "VIEWER_SHARED_INVALID", "invalid artifact generation")
        try:
            adapter = _local_adapter(repo)
            artifact = adapter.get(f"shared://{adapter.repository_namespace}/{generation_id}")
        except MissingError as exc:
            raise ReadError(HTTPStatus.NOT_FOUND, exc.code, "artifact not found") from exc
        except ExpiredError as exc:
            raise ReadError(HTTPStatus.GONE, exc.code, "artifact expired") from exc
        except (AdvisoryError, SharedError) as exc:
            raise ReadError(HTTPStatus.BAD_REQUEST, getattr(exc, "code", "VIEWER_SHARED_INVALID"), str(exc)) from exc
        return {
            "metadata": artifact.metadata.to_dict(),
            "content": artifact.content,
            "artifact_uri": artifact.metadata.artifact_uri,
        }
