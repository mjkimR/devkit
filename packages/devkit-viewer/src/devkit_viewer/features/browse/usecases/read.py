"""Read the selected repository's metadata and saved documents."""

import base64
from collections.abc import Iterable
from http import HTTPStatus

from devkit_viewer.features.browse.models.errors import ReadError
from devkit_viewer.features.browse.models.repository import Repository
from devkit_viewer.features.browse.repositories.worktree import WorkingTreeReader


def list_repositories(repositories: Iterable[Repository]) -> dict[str, object]:
    return {
        "repos": [{"id": repo.id, "default_branch": WorkingTreeReader(repo.root).branch()} for repo in repositories]
    }


def read_repository(repo: Repository, endpoint: str, target: str, *, recursive: bool = False) -> dict[str, object]:
    reader = WorkingTreeReader(repo.root)
    if endpoint == "info":
        return {"repo_id": repo.id, "default_branch": reader.branch()}
    if endpoint not in ("tree", "blob"):
        raise ReadError(HTTPStatus.NOT_FOUND, "VIEWER_NOT_FOUND", f"no API endpoint '/api/repos/{repo.id}/{endpoint}'")
    if endpoint == "tree":
        return {"items": [item.as_json() for item in reader.tree(target, recursive=recursive)]}
    data = reader.blob(target)
    return {"path": target, "encoding": "base64", "content": base64.b64encode(data).decode(), "size": len(data)}
