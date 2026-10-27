"""Read the selected repository's metadata, saved documents and Planning proposals."""

import base64
from collections.abc import Iterable
from http import HTTPStatus

from devkit_core.base.usecase import BaseUseCase

from devkit_viewer.features.browse.models.errors import ReadError
from devkit_viewer.features.browse.models.repository import Repository
from devkit_viewer.features.browse.repositories.planning import planning_proposals, source_blob, source_tree
from devkit_viewer.features.browse.repositories.worktree import WorkingTreeReader


class ListRepositoriesUseCase(BaseUseCase):
    def execute(self, repositories: Iterable[Repository]) -> dict[str, object]:
        return {
            "repos": [{"id": repo.id, "default_branch": WorkingTreeReader(repo.root).branch()} for repo in repositories]
        }


class ReadRepositoryUseCase(BaseUseCase):
    def execute(
        self,
        repo: Repository,
        endpoint: str,
        target: str,
        *,
        recursive: bool = False,
        source: str = "",
    ) -> dict[str, object]:
        """Answer one read endpoint; ``source`` selects a Planning source for ``tree`` and ``blob`` only."""
        reader = WorkingTreeReader(repo.root)
        if endpoint == "info":
            return {"repo_id": repo.id, "default_branch": reader.branch()}
        if endpoint == "dashboard-list":
            return reader.dashboard_headers(target)
        if endpoint == "planning-proposals":
            return planning_proposals(repo.root)
        if endpoint not in ("tree", "blob"):
            raise ReadError(
                HTTPStatus.NOT_FOUND, "VIEWER_NOT_FOUND", f"no API endpoint '/api/repos/{repo.id}/{endpoint}'"
            )
        if endpoint == "tree":
            items = (
                source_tree(repo.root, source, target, recursive=recursive)
                if source
                else reader.tree(target, recursive=recursive)
            )
            return {"items": [item.as_json() for item in items]}
        data = source_blob(repo.root, source, target) if source else reader.blob(target)
        return {"path": target, "encoding": "base64", "content": base64.b64encode(data).decode(), "size": len(data)}
