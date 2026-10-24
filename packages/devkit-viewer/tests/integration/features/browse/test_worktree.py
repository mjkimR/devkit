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


def test_recursive_tree_uses_metadata_and_excludes_symlinks_and_git(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    nested = repo / "docs/sub/feedback"
    nested.mkdir(parents=True)
    (nested / "issue.md").write_text("feedback")
    (nested / ".git").mkdir()
    (nested / ".git/secret").write_text("hidden")
    (nested / "outside").symlink_to(repo.parent, target_is_directory=True)
    (repo / "docs/alias.md").symlink_to(repo / "docs/a.md")

    def refuse_content(*args: object, **kwargs: object) -> None:
        raise AssertionError("recursive metadata must not read file bodies")

    monkeypatch.setattr(Path, "read_bytes", refuse_content)
    monkeypatch.setattr(Path, "read_text", refuse_content)
    items = WorkingTreeReader(repo).tree("docs", recursive=True)
    assert {item.path for item in items} == {"docs/a.md", "docs/sub", "docs/sub/feedback", "docs/sub/feedback/issue.md"}
    assert next(item.size for item in items if item.path.endswith("issue.md")) == 8
    with pytest.raises(ReadError) as caught:
        WorkingTreeReader(repo).tree("docs/sub/feedback/outside", recursive=True)
    assert caught.value.code == "VIEWER_PATH_NOT_FOUND"


@pytest.mark.parametrize("path", ["../outside", ".git", "docs/../.git", "/docs"])
def test_recursive_tree_rejects_invalid_paths(repo: Path, path: str) -> None:
    with pytest.raises(ReadError) as caught:
        WorkingTreeReader(repo).tree(path, recursive=True)
    assert caught.value.code == "VIEWER_PATH_INVALID"
