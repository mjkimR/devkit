"""Planning sources over real repositories: a linked worktree, local plan branches and remote-tracking refs."""

from __future__ import annotations

import base64
import http.client
import json
import os
import threading
from collections.abc import Iterator
from pathlib import Path

import pytest
from viewer_fixtures import MakeRepo, commit_files, git

from devkit_viewer.features.browse.http.server import ViewerServer
from devkit_viewer.features.browse.models.errors import ReadError
from devkit_viewer.features.browse.models.repository import Repository
from devkit_viewer.features.browse.repositories import planning
from devkit_viewer.features.browse.repositories.planning import (
    planning_proposals,
    planning_sources,
    source_blob,
    source_tree,
)


def proposal(slug: str, text: str) -> str:
    return f"---\nid: PROP-{slug}\ntitle: {text}\nstatus: draft\n---\n# {text}\n"


@pytest.fixture
def repo(make_repo: MakeRepo, tmp_path: Path) -> Path:
    """``main`` checkout; ``plan-a`` in a linked worktree with saved edits; local and remote-tracking plan refs."""
    root = make_repo(
        "repo",
        {
            "docs/proposals/PROP-a/proposal.md": proposal("a", "main a"),
            "docs/proposals/PROP-b/proposal.md": proposal("b", "main b"),
        },
    )
    base = git(root, "rev-parse", "HEAD").strip()
    git(root, "switch", "-q", "-c", "plan-a")
    commit_files(
        root,
        {
            "docs/proposals/PROP-a/proposal.md": proposal("a", "committed a"),
            "docs/proposals/PROP-other/proposal.md": proposal("other", "stale copy"),
        },
    )
    git(root, "update-ref", "refs/remotes/origin/plan-a", "HEAD")
    git(root, "switch", "-q", "-c", "plan-b", "main")
    commit_files(root, {"docs/proposals/PROP-b/proposal.md": proposal("b", "local b")})
    git(root, "update-ref", "refs/remotes/origin/plan-b", base)
    git(root, "switch", "-q", "-c", "plan-c", "main")
    commit_files(root, {"docs/proposals/PROP-c/proposal.md": proposal("c", "remote c")})
    git(root, "update-ref", "refs/remotes/origin/plan-c", "HEAD")
    git(root, "update-ref", "refs/remotes/zeta/plan-c", base)
    git(root, "switch", "-q", "-c", "plan-new", "main")
    commit_files(
        root,
        {
            "docs/proposals/PROP-new/proposal.md": proposal("new", "only planned"),
            "docs/proposals/PROP-new/materials/m.md": "material\n",
        },
    )
    os.symlink("proposal.md", root / "docs/proposals/PROP-new/link.md")
    commit_files(root, {})
    git(root, "switch", "-q", "-c", "plan-empty", "main")
    commit_files(root, {"docs/other.md": "x\n"})
    git(root, "switch", "-q", "-c", "plan-sym", "main")
    (root / "docs/proposals/PROP-sym").mkdir()
    os.symlink("../PROP-b/proposal.md", root / "docs/proposals/PROP-sym/proposal.md")
    commit_files(root, {})
    git(root, "branch", "plan-x/nested", "main")
    git(root, "switch", "-q", "main")
    git(root, "branch", "-D", "plan-c")
    worktree = tmp_path / "wt-plan-a"
    git(root, "worktree", "add", "-q", str(worktree), "plan-a")
    (worktree / "docs/proposals/PROP-a/proposal.md").write_text(proposal("a", "saved a"), encoding="utf-8")
    (worktree / "docs/proposals/PROP-a/materials").mkdir()
    (worktree / "docs/proposals/PROP-a/materials/notes.md").write_text("untracked\n", encoding="utf-8")
    return root


def test_sources_follow_worktree_branch_remote_precedence(repo: Path) -> None:
    sources, errors = planning_sources(repo)
    assert errors == []
    assert {source_id: source.label for source_id, source in sources.items()} == {
        "worktree:plan-a": "worktree plan-a",
        "branch:plan-b": "plan-b",
        "remote:origin/plan-c": "origin/plan-c",
        "branch:plan-empty": "plan-empty",
        "branch:plan-new": "plan-new",
        "branch:plan-sym": "plan-sym",
    }
    result = planning_proposals(repo)
    items = {item["source"]: item for item in result["items"]}  # type: ignore[union-attr]
    assert "saved a" in items["worktree:plan-a"]["content"]
    assert "local b" in items["branch:plan-b"]["content"]
    assert "remote c" in items["remote:origin/plan-c"]["content"]


def test_each_plan_branch_contributes_only_its_own_proposal(repo: Path) -> None:
    result = planning_proposals(repo)
    assert [(item["source"], item["path"]) for item in result["items"]] == [  # type: ignore[union-attr]
        ("worktree:plan-a", "docs/proposals/PROP-a/proposal.md"),
        ("branch:plan-b", "docs/proposals/PROP-b/proposal.md"),
        ("remote:origin/plan-c", "docs/proposals/PROP-c/proposal.md"),
        ("branch:plan-new", "docs/proposals/PROP-new/proposal.md"),
    ]
    assert [error for error in result["errors"] if "plan-sym" in error]  # type: ignore[union-attr]


def test_scan_uses_three_batched_git_processes_and_writes_nothing(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    refs = git(repo, "for-each-ref")
    status = git(repo, "status", "--porcelain")
    calls: list[tuple[str, ...]] = []
    original = planning.run_git

    def record(cwd: Path, *args: str, **kwargs: object) -> bytes:
        calls.append(args)
        return original(cwd, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(planning, "run_git", record)
    planning_proposals(repo)
    assert sorted(call[0] for call in calls) == ["cat-file", "for-each-ref", "worktree"]
    assert ("cat-file", "--batch") in calls
    assert git(repo, "for-each-ref") == refs
    assert git(repo, "status", "--porcelain") == status


def test_checkout_on_a_plan_branch_has_no_source_for_itself(repo: Path, tmp_path: Path) -> None:
    worktree = tmp_path / "wt-plan-a"
    sources, _ = planning_sources(worktree)
    assert "worktree:plan-a" not in sources
    assert not any(source.slug == "a" for source in sources.values())


def test_source_reads_return_worktree_and_committed_content(repo: Path) -> None:
    listing = source_tree(repo, "worktree:plan-a", "docs/proposals/PROP-a", recursive=True)
    assert [item.path for item in listing] == [
        "docs/proposals/PROP-a/materials",
        "docs/proposals/PROP-a/materials/notes.md",
        "docs/proposals/PROP-a/proposal.md",
    ]
    assert source_blob(repo, "branch:plan-b", "docs/proposals/PROP-b/proposal.md").decode().count("local b") == 2
    committed = source_tree(repo, "branch:plan-new", "docs/proposals/PROP-new", recursive=True)
    assert [(item.path, item.type) for item in committed] == [
        ("docs/proposals/PROP-new/materials", "tree"),
        ("docs/proposals/PROP-new/materials/m.md", "blob"),
        ("docs/proposals/PROP-new/proposal.md", "blob"),
    ]
    shallow = source_tree(repo, "branch:plan-new", "docs/proposals/PROP-new")
    assert [item.name for item in shallow] == ["materials", "proposal.md"]


@pytest.mark.parametrize(
    ("source", "path", "code"),
    [
        ("worktree:plan-a", "docs/proposals/PROP-b/proposal.md", "VIEWER_SOURCE_PATH_REFUSED"),
        ("branch:plan-b", "docs/a.md", "VIEWER_SOURCE_PATH_REFUSED"),
        ("branch:plan-b", "docs/proposals/PROP-bb/proposal.md", "VIEWER_SOURCE_PATH_REFUSED"),
        ("branch:plan-a", "docs/proposals/PROP-a/proposal.md", "VIEWER_SOURCE_UNKNOWN"),
        ("HEAD", "docs/proposals/PROP-a/proposal.md", "VIEWER_SOURCE_UNKNOWN"),
        ("branch:plan-b^", "docs/proposals/PROP-b/proposal.md", "VIEWER_SOURCE_UNKNOWN"),
        ("branch:plan-b", "docs/proposals/PROP-b/../PROP-a/proposal.md", "VIEWER_PATH_INVALID"),
        ("branch:plan-b", "docs/proposals/PROP-b/.git/config", "VIEWER_PATH_INVALID"),
        ("branch:plan-new", "docs/proposals/PROP-new/link.md", "VIEWER_PATH_NOT_FOUND"),
        ("branch:plan-new", "docs/proposals/PROP-new/missing.md", "VIEWER_PATH_NOT_FOUND"),
    ],
)
def test_source_reads_refuse_other_paths_and_sources(repo: Path, source: str, path: str, code: str) -> None:
    with pytest.raises(ReadError) as caught:
        source_blob(repo, source, path)
    assert caught.value.code == code


def test_worktree_source_keeps_symlink_guard(repo: Path, tmp_path: Path) -> None:
    worktree = tmp_path / "wt-plan-a"
    os.symlink(repo / "README.md", worktree / "docs/proposals/PROP-a/escape.md")
    with pytest.raises(ReadError) as caught:
        source_blob(repo, "worktree:plan-a", "docs/proposals/PROP-a/escape.md")
    assert caught.value.code == "VIEWER_PATH_NOT_FOUND"
    listing = source_tree(repo, "worktree:plan-a", "docs/proposals/PROP-a")
    assert "escape.md" not in [item.name for item in listing]


@pytest.fixture
def served(repo: Path) -> Iterator[ViewerServer]:
    viewer = ViewerServer([Repository(id="repo", root=repo)], 0)
    thread = threading.Thread(target=viewer.serve_forever, daemon=True)
    thread.start()
    yield viewer
    viewer.shutdown()
    viewer.server_close()


def get(server: ViewerServer, path: str) -> tuple[int, dict]:
    connection = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
    connection.request("GET", path)
    response = connection.getresponse()
    result = response.status, json.loads(response.read())
    connection.close()
    return result


def test_http_planning_endpoints(served: ViewerServer) -> None:
    status, body = get(served, "/api/repos/repo/planning-proposals?source=branch:plan-b")
    assert status == 200
    assert {source["id"] for source in body["sources"]} >= {"worktree:plan-a", "branch:plan-b"}
    assert body["sources"][0] == {"id": "worktree:plan-a", "kind": "worktree", "label": "worktree plan-a", "slug": "a"}
    status, body = get(served, "/api/repos/repo/tree?path=docs/proposals/PROP-a&recursive=true&source=worktree:plan-a")
    assert status == 200
    assert "docs/proposals/PROP-a/materials/notes.md" in [item["path"] for item in body["items"]]
    status, body = get(served, "/api/repos/repo/blob?path=docs/proposals/PROP-b/proposal.md&source=branch:plan-b")
    assert status == 200
    assert "local b" in base64.b64decode(body["content"]).decode()
    status, body = get(served, "/api/repos/repo/blob?path=docs/proposals/PROP-b/proposal.md")
    assert "main b" in base64.b64decode(body["content"]).decode()
    status, body = get(served, "/api/repos/repo/blob?path=README.md&source=branch:plan-b")
    assert (status, body["error"]["code"]) == (400, "VIEWER_SOURCE_PATH_REFUSED")
    status, body = get(served, "/api/repos/repo/blob?path=docs/proposals/PROP-b/proposal.md&source=HEAD")
    assert (status, body["error"]["code"]) == (404, "VIEWER_SOURCE_UNKNOWN")
    status, body = get(served, "/api/repos/repo/dashboard-list?path=proposals&source=branch:plan-b")
    assert status == 200
    assert "main b" in next(item["content"] for item in body["items"] if "PROP-b" in item["path"])
    assert get(served, "/api/repos/repo/info?source=branch:plan-b") == (
        200,
        {"repo_id": "repo", "default_branch": "main"},
    )
