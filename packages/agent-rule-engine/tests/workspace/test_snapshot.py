from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from agent_rule_engine import SnapshotError, git_snapshot, materialize


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    (root / "docs").mkdir()
    (root / "docs/a.md").write_text("# A\n")
    (root / "run.sh").write_text("#!/bin/sh\n")
    (root / "run.sh").chmod(0o755)
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "init")
    return root


def test_staged_snapshot_ignores_unstaged_edits_and_untracked_files(repo: Path, tmp_path: Path) -> None:
    (repo / "docs/a.md").write_text("# A staged\n")
    (repo / "docs/new.md").write_text("new\n")
    _git(repo, "add", "docs")
    (repo / "docs/a.md").write_text("# A unstaged\n")
    (repo / "untracked.md").write_text("x\n")
    (repo / ".env").write_text("SECRET=1\n")

    snapshot = git_snapshot(repo, staged=True)
    assert snapshot.mode == "staged"
    assert snapshot.changed == ("docs/a.md", "docs/new.md")
    assert snapshot.deleted == ()
    assert {name for name, _, _ in snapshot.files} == {"docs/a.md", "docs/new.md", "run.sh"}

    out = tmp_path / "out"
    materialize(snapshot, out)
    assert (out / "docs/a.md").read_text() == "# A staged\n"
    assert (out / "run.sh").stat().st_mode & 0o111
    assert not (out / "untracked.md").exists() and not (out / ".env").exists()


def test_staged_snapshot_reports_deleted_paths(repo: Path) -> None:
    _git(repo, "rm", "-q", "run.sh")
    snapshot = git_snapshot(repo, staged=True)
    assert snapshot.deleted == ("run.sh",)
    assert snapshot.changed == ()


def test_ci_snapshot_uses_merge_base(repo: Path) -> None:
    _git(repo, "checkout", "-q", "-b", "feature")
    (repo / "docs/b.md").write_text("# B\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "feature")
    _git(repo, "checkout", "-q", "main")
    (repo / "docs/c.md").write_text("# C\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "main moves on")
    _git(repo, "checkout", "-q", "feature")
    (repo / "docs/b.md").write_text("# B unstaged\n")

    snapshot = git_snapshot(repo, staged=False, base="main")
    assert snapshot.mode == "ci"
    assert snapshot.changed == ("docs/b.md",)
    assert snapshot.base == _git(repo, "merge-base", "main", "feature")


def test_unborn_branch_compares_against_empty_tree(tmp_path: Path) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    (root / "a.md").write_text("a\n")
    _git(root, "add", "a.md")
    snapshot = git_snapshot(root, staged=True)
    assert snapshot.changed == ("a.md",)


def test_snapshot_errors_outside_git_and_for_bad_base(tmp_path: Path, repo: Path) -> None:
    with pytest.raises(SnapshotError, match="git write-tree failed"):
        git_snapshot(tmp_path, staged=True)
    with pytest.raises(SnapshotError, match="merge-base failed"):
        git_snapshot(repo, staged=False, base="nope/nope")
