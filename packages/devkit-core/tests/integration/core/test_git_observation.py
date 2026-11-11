"""``worktree_records`` and ``status_records`` over real repositories."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest
from devkit_core.core import StatusRecord, WorktreeRecord, run_git, status_records, worktree_records

ZERO = "0" * 40


def _commit(repo: Path, name: str = "a.txt", content: str = "a\n") -> str:
    (repo / name).write_text(content)
    run_git(repo, "add", "--", name)
    run_git(repo, "commit", "-q", "-m", name)
    return run_git(repo, "rev-parse", "HEAD").decode().strip()


def test_worktree_kinds(repo: Path, tmp_path: Path) -> None:
    head = _commit(repo)
    tmp_path = tmp_path.resolve()
    linked, detached, locked, reason, prunable = (tmp_path / name for name in ("l", "d", "k", "r", "p"))
    newline = tmp_path / "new\nline"
    run_git(repo, "worktree", "add", "-q", "-b", "feature", str(linked))
    run_git(repo, "worktree", "add", "-q", "--detach", str(detached))
    run_git(repo, "worktree", "add", "-q", "--detach", str(locked))
    run_git(repo, "worktree", "lock", str(locked))
    run_git(repo, "worktree", "add", "-q", "--detach", str(reason))
    run_git(repo, "worktree", "lock", "--reason", "on a stick", str(reason))
    run_git(repo, "worktree", "add", "-q", "--detach", str(prunable))
    run_git(repo, "worktree", "add", "-q", "--detach", str(newline))
    shutil.rmtree(prunable)

    records = {record.path: record for record in worktree_records(repo)}
    assert next(iter(records)) == repo
    assert records[repo] == WorktreeRecord(repo, head, "refs/heads/main")
    assert records[linked] == WorktreeRecord(linked, head, "refs/heads/feature")
    assert records[detached] == WorktreeRecord(detached, head, None, detached=True)
    assert records[locked].locked == "" and records[reason].locked == "on a stick"
    assert records[detached].locked is None and records[detached].prunable is None
    assert records[prunable].prunable is not None
    assert records[newline] == WorktreeRecord(newline, head, None, detached=True)


def test_unborn_and_bare(repo: Path, tmp_path: Path) -> None:
    assert worktree_records(repo) == [WorktreeRecord(repo, ZERO, "refs/heads/main")]
    _commit(repo)
    bare = (tmp_path / "bare.git").resolve()
    run_git(repo, "clone", "-q", "--bare", str(repo), str(bare))
    linked = (tmp_path / "from-bare").resolve()
    run_git(bare, "worktree", "add", "-q", str(linked))
    first, second = worktree_records(bare)
    assert first == WorktreeRecord(bare, None, None, bare=True)
    assert second.path == linked and second.branch is not None and not second.bare


def test_rename_copy_and_untracked_nested_repository(repo: Path) -> None:
    _commit(repo, "old.txt", "content\n" * 20)
    run_git(repo, "mv", "old.txt", "new.txt")
    nested = repo / "nested"
    nested.mkdir()
    run_git(nested, "init", "-q")
    assert status_records(repo) == [
        StatusRecord("R ", "new.txt", "old.txt"),
        StatusRecord("??", "nested/"),
    ]


def test_copy_is_one_record_with_its_source(repo: Path) -> None:
    _commit(repo, "a.txt", "content\n" * 20)
    run_git(repo, "config", "status.renames", "copies")
    (repo / "a.txt").write_text("content\n" * 20 + "changed\n")
    (repo / "b.txt").write_text("content\n" * 20)
    run_git(repo, "add", "-A")
    assert StatusRecord("C ", "b.txt", "a.txt") in status_records(repo)


def test_pathspecs_untracked_and_options(repo: Path) -> None:
    _commit(repo)
    (repo / "dir").mkdir()
    (repo / "dir/x").write_text("x")
    (repo / "a.txt").write_text("changed\n")
    assert status_records(repo, "dir") == [StatusRecord("??", "dir/x")]
    assert status_records(repo, untracked="normal") == [StatusRecord(" M", "a.txt"), StatusRecord("??", "dir/")]
    assert status_records(repo, untracked="no", optional_locks=True) == [
        StatusRecord(" M", "a.txt")
    ]


def test_non_utf8_path(repo: Path) -> None:
    _commit(repo)
    name = os.fsdecode(b"bad-\xff")
    try:
        (repo / name).write_text("x")
    except OSError:
        pytest.skip("the file system refuses a non-UTF-8 name")
    record = status_records(repo)[0]
    assert record.path.encode("utf-8", "surrogateescape") == b"bad-\xff"
