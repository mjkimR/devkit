"""Read the selected repository's metadata and committed documents."""

import base64
from collections.abc import Iterable
from http import HTTPStatus

from devkit_viewer.features.browse.models.errors import ReadError
from devkit_viewer.features.browse.models.repository import Repository
from devkit_viewer.features.browse.repositories.git import GitReader


def list_repositories(repositories: Iterable[Repository]) -> dict[str, object]:
    return {
        "repos": [{"id": repo.id, "default_branch": GitReader(repo.root).default_branch()} for repo in repositories]
    }


def read_repository(repo: Repository, endpoint: str, target: str, ref: str) -> dict[str, object]:
    reader = GitReader(repo.root)
    if endpoint == "info":
        return {"repo_id": repo.id, "default_branch": reader.default_branch()}
    if endpoint == "refs":
        return {"default_branch": reader.default_branch(), "branches": reader.branches()}
    if endpoint not in ("tree", "blob"):
        raise ReadError(HTTPStatus.NOT_FOUND, "VIEWER_NOT_FOUND", f"no API endpoint '/api/repos/{repo.id}/{endpoint}'")
    ref = ref or reader.default_branch()
    if endpoint == "tree":
        return {"items": [item.as_json() for item in reader.tree(ref, target)]}
    data = reader.blob(ref, target)
    return {"path": target, "encoding": "base64", "content": base64.b64encode(data).decode(), "size": len(data)}
