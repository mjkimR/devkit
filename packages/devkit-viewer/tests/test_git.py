from __future__ import annotations

from pathlib import Path

import pytest
from viewer_fixtures import MakeRepo, commit_files, git

from devkit_viewer.errors import ReadError
from devkit_viewer.git import GitReader, check_path


@pytest.fixture
def repo(make_repo: MakeRepo) -> Path:
    root = make_repo("alpha", {"docs/a.md": "main a\n", "docs/sub/b.md": "b\n", "top.txt": "t\n"})
    git(root, "switch", "-q", "-c", "plan-x")
    commit_files(root, {"docs/a.md": "plan a\n"})
    git(root, "switch", "-q", "main")
    return root


def _error(call, *args: str) -> ReadError:
    with pytest.raises(ReadError) as caught:
        call(*args)
    return caught.value


def test_tree_lists_one_directory(repo: Path) -> None:
    items = GitReader(repo).tree("main", "docs")
    assert [item.as_json() for item in items] == [
        {"name": "sub", "path": "docs/sub", "type": "tree"},
        {"name": "a.md", "path": "docs/a.md", "type": "blob", "size": len("main a\n")},
    ]


def test_tree_of_the_root(repo: Path) -> None:
    names = [(item.path, item.type) for item in GitReader(repo).tree("main", "")]
    assert names == [(".devkit", "tree"), ("docs", "tree"), ("top.txt", "blob")]


def test_blob_reads_a_branch_that_is_not_checked_out(repo: Path) -> None:
    head = git(repo, "rev-parse", "HEAD")
    reader = GitReader(repo)
    assert reader.blob("plan-x", "docs/a.md") == b"plan a\n"
    assert reader.blob("main", "docs/a.md") == b"main a\n"
    assert git(repo, "rev-parse", "HEAD") == head
    assert git(repo, "symbolic-ref", "--short", "HEAD").strip() == "main"
    assert git(repo, "status", "--porcelain") == ""
    assert (repo / "docs/a.md").read_text() == "main a\n"


def test_branches_are_local_only(repo: Path) -> None:
    git(repo, "branch", "dev-y")
    git(repo, "update-ref", "refs/remotes/origin/z", "HEAD")
    reader = GitReader(repo)
    assert reader.branches() == ["dev-y", "main", "plan-x"]
    assert reader.default_branch() == "main"


def test_detached_head_is_reported_as_head(repo: Path) -> None:
    git(repo, "switch", "-q", "--detach", "plan-x")
    reader = GitReader(repo)
    assert reader.default_branch() == "HEAD"
    assert reader.blob("HEAD", "docs/a.md") == b"plan a\n"


@pytest.mark.parametrize("ref", ["no-such-branch", "-x", "--all", ""])
def test_unknown_refs(repo: Path, ref: str) -> None:
    error = _error(GitReader(repo).tree, ref, "docs")
    assert (error.status, error.code) == (404, "VIEWER_REF_UNKNOWN")


@pytest.mark.parametrize(
    ("call", "path"),
    [("tree", "missing"), ("blob", "docs/missing.md"), ("blob", "docs"), ("blob", ""), ("tree", "top.txt")],
)
def test_missing_paths(repo: Path, call: str, path: str) -> None:
    error = _error(getattr(GitReader(repo), call), "main", path)
    assert (error.status, error.code) == (404, "VIEWER_PATH_NOT_FOUND")


@pytest.mark.parametrize("path", ["../x", "docs/../top.txt", "./docs", "docs//a.md", "/docs", "docs\\a.md", "docs/"])
def test_invalid_paths(repo: Path, path: str) -> None:
    error = _error(GitReader(repo).blob, "main", path)
    assert (error.status, error.code) == (400, "VIEWER_PATH_INVALID")
    assert _error(check_path, path).code == "VIEWER_PATH_INVALID"
