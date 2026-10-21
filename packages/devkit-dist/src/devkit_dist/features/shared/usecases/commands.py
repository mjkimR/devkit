"""Shared artifact operations exposed consistently by CLI and MCP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from devkit_core.base.usecase import BaseUseCase

from devkit_dist.features.shared.models.api import PutRequest, SharedArtifactAdapter
from devkit_dist.features.shared.usecases.service import adapter


def _result(selected: SharedArtifactAdapter, value: dict[str, Any]) -> dict[str, Any]:
    return {**value, "adapter": selected.adapter_id, "repository_namespace": selected.repository_namespace}


class PutArtifact(BaseUseCase):
    """Validate and store an immutable artifact, returning its receipt."""

    def execute(self, workspace: Path, request: PutRequest) -> dict[str, Any]:
        request.validate()
        selected = adapter(workspace)
        return _result(selected, selected.put(request).receipt_dict())


class GetArtifact(BaseUseCase):
    """Read an exact artifact including its content."""

    def execute(self, workspace: Path, artifact_uri: str) -> dict[str, Any]:
        selected = adapter(workspace)
        return _result(selected, selected.get(artifact_uri).to_dict())


class ListArtifacts(BaseUseCase):
    """Read a bounded artifact metadata page."""

    def execute(
        self,
        workspace: Path,
        kind: str,
        slug: str,
        *,
        source_sha: str | None = None,
        language: str | None = None,
        cursor: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        selected = adapter(workspace)
        page = selected.list(kind, slug, source_sha=source_sha, language=language, cursor=cursor, limit=limit)
        return _result(selected, page.to_dict())


class SweepArtifacts(BaseUseCase):
    """Inspect or apply a bounded expired-artifact cleanup."""

    def execute(self, workspace: Path, *, apply: bool = False, cursor: str | None = None) -> dict[str, Any]:
        selected = adapter(workspace)
        return _result(selected, selected.sweep(apply=apply, cursor=cursor).to_dict())
