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


def test_dashboard_reads_only_candidate_frontmatter(repo: Path) -> None:
    files = {
        "docs/roadmap/MS-a.md": "---\nid: MS-a\nstatus: active\n---\nBODY MUST NOT APPEAR\n",
        "docs/roadmap/README.md": "ignore",
        "docs/roadmap/nested/MS-b.md": "ignore",
        "docs/proposals/PROP-a/proposal.md": "---\nid: PROP-a\n---\nproposal body",
        "docs/proposals/PROP-a/plan.md": "ignore",
        "specs/month/unit/feedback/deep/a.md": "---\nid: FB-a\nseverity: critical\n---\nfeedback body",
        "specs/month/unit/feedback/README.md": "ignore",
        "docs/materials/feedback/plain.md": "# No frontmatter\nbody",
    }
    for path, content in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    (repo / "docs/roadmap/MS-alias.md").symlink_to(repo / "docs/roadmap/MS-a.md")
    reader = WorkingTreeReader(repo)
    milestones = reader.dashboard_headers("milestones")
    assert milestones == {
        "items": [
            {"path": "docs/roadmap/MS-a.md", "content": "---\nid: MS-a\nstatus: active\n---\n", "encoding": "utf-8"}
        ],
        "errors": [],
    }
    proposals = reader.dashboard_headers("proposals")
    assert "proposal body" not in str(proposals)
    assert "PROP-a" in str(proposals)
    feedback = reader.dashboard_headers("feedback")
    assert "feedback body" not in str(feedback)
    assert "FB-a" in str(feedback)
    assert "README" not in str(feedback)
    assert "docs/materials/feedback/plain.md" in str(feedback)
    with pytest.raises(ReadError) as caught:
        reader.dashboard_headers("../outside")
    assert caught.value.code == "VIEWER_PATH_INVALID"


def test_dashboard_header_errors_and_absent_roots(repo: Path) -> None:
    reader = WorkingTreeReader(repo)
    assert reader.dashboard_headers("milestones") == {"items": [], "errors": []}
    folder = repo / "docs/roadmap"
    folder.mkdir()
    (folder / "MS-bad.md").write_text("---\nid: broken\n")
    result = reader.dashboard_headers("milestones")
    assert result["items"] == []
    assert "unterminated YAML frontmatter" in str(result["errors"])
    with pytest.raises(ReadError):
        reader.frontmatter("../outside")


def test_frontmatter_does_not_decode_body(repo: Path) -> None:
    target = repo / "docs/a.md"
    target.write_bytes(b"---\r\nid: MS-a\r\n---\r\n\xff\xfe")
    assert WorkingTreeReader(repo).frontmatter("docs/a.md") == "---\r\nid: MS-a\r\n---\r\n"
    target.write_bytes(b"# Title\n\xff\xfe")
    assert WorkingTreeReader(repo).frontmatter("docs/a.md") == ""


@pytest.mark.parametrize(
    ("raw", "envelope"),
    [
        (b"\xef\xbb\xbf---\nid: MS-a\n---\nbody\n", "---\nid: MS-a\n---\n"),
        (b"--- \nid: MS-a\n--- \nbody\n", "---\nid: MS-a\n---\n"),
        (b"---\nid: MS-a\n...\nbody\n", "---\nid: MS-a\n---\n"),
        (b"---\n---\nbody\n", "---\n---\n"),
        (b" ---\nid: MS-a\n---\n", ""),
    ],
)
def test_frontmatter_follows_the_core_grammar(repo: Path, raw: bytes, envelope: str) -> None:
    (repo / "docs/a.md").write_bytes(raw)
    assert WorkingTreeReader(repo).frontmatter("docs/a.md") == envelope


def test_dashboard_lists_a_milestone_core_accepts(repo: Path) -> None:
    folder = repo / "docs/roadmap"
    folder.mkdir()
    (folder / "MS-bom.md").write_bytes(b"\xef\xbb\xbf--- \nid: MS-bom\n...\n")
    result = WorkingTreeReader(repo).dashboard_headers("milestones")
    assert result == {
        "items": [{"path": "docs/roadmap/MS-bom.md", "content": "---\nid: MS-bom\n---\n", "encoding": "utf-8"}],
        "errors": [],
    }


@pytest.mark.parametrize("status", ["done", "dropped"])
def test_dashboard_archive_and_nested_detail(repo: Path, status: str) -> None:
    path = f"docs/roadmap/_archive/MS-{status}.md"
    target = repo / path
    target.parent.mkdir(parents=True)
    header = f"---\nid: MS-{status}\nstatus: {status}\n---\n"
    target.write_text(header + "# Retained detail\n")
    nested = target.parent / "year/MS-ignore.md"
    nested.parent.mkdir()
    nested.write_text("ignore unrelated nesting")
    reader = WorkingTreeReader(repo)
    assert reader.dashboard_headers("milestones") == {
        "items": [{"path": path, "content": header, "encoding": "utf-8"}],
        "errors": [],
    }
    assert reader.blob(path) == target.read_bytes()
    assert path in {item.path for item in reader.tree("docs/roadmap/_archive")}
