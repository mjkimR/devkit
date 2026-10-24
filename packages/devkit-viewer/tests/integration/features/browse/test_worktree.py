from __future__ import annotations

from pathlib import Path

import pytest
from viewer_fixtures import MakeRepo, git

from devkit_viewer.features.browse.models.errors import ReadError
from devkit_viewer.features.browse.repositories.worktree import WorkingTreeReader, check_path


@pytest.fixture
def repo(make_repo: MakeRepo) -> Path:
    return make_repo("alpha", {"docs/a.md": "committed\n"})


def test_tree_and_blob_read_saved_uncommitted_and_untracked_files(repo: Path) -> None:
    (repo / "docs/a.md").write_text("saved edit\n")
    (repo / "docs/new.md").write_text("untracked\n")
    reader = WorkingTreeReader(repo)
    assert reader.blob("docs/a.md") == b"saved edit\n"
    assert {item.path for item in reader.tree("docs")} == {"docs/a.md", "docs/new.md"}


def test_branch_reports_checkout_and_detached_head(repo: Path) -> None:
    reader = WorkingTreeReader(repo)
    assert reader.branch() == "main"
    git(repo, "switch", "-q", "--detach", "HEAD")
    assert WorkingTreeReader(repo).branch() == "HEAD"


@pytest.mark.parametrize(
    "path", ["../outside", "docs/../outside", "./docs", "/docs", "docs//a.md", "docs\\a.md", ".git/config"]
)
def test_invalid_repository_paths(path: str) -> None:
    with pytest.raises(ReadError) as caught:
        check_path(path)
    assert (caught.value.status, caught.value.code) == (400, "VIEWER_PATH_INVALID")


def test_missing_paths_return_stable_error(repo: Path) -> None:
    with pytest.raises(ReadError) as caught:
        WorkingTreeReader(repo).blob("docs/missing.md")
    assert (caught.value.status, caught.value.code) == (404, "VIEWER_PATH_NOT_FOUND")
