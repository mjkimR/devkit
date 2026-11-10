"""The pure parsers of ``git worktree list --porcelain -z`` and ``git status --porcelain=v1 -z``."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_core.core import GitError, StatusRecord, WorktreeRecord, parse_status_records, parse_worktree_records


def test_empty_output() -> None:
    assert parse_status_records(b"") == []
    assert parse_worktree_records(b"") == []


def test_status_records_and_both_rename_columns() -> None:
    raw = b"R  new\0old\0 R moved\0orig\0?? dir/\0 M \xff\0"
    assert parse_status_records(raw) == [
        StatusRecord("R ", "new", "old"),
        StatusRecord(" R", "moved", "orig"),
        StatusRecord("??", "dir/"),
        StatusRecord(" M", b"\xff".decode("utf-8", "surrogateescape")),
    ]


@pytest.mark.parametrize("raw", [b"R  new\0", b"C  new\0\0", b"x\0"])
def test_malformed_status_is_an_error(raw: bytes) -> None:
    with pytest.raises(GitError):
        parse_status_records(raw)


def test_worktree_fields_and_unknown_keys() -> None:
    raw = (
        b"ignored before\0worktree /a\0HEAD abc\0branch refs/heads/main\0future value\0\0"
        b"worktree /b\0HEAD abc\0detached\0locked\0prunable gone\0\0"
        b"worktree /c\nd\0bare\0\0"
    )
    assert parse_worktree_records(raw) == [
        WorktreeRecord(Path("/a"), "abc", "refs/heads/main"),
        WorktreeRecord(Path("/b"), "abc", None, detached=True, locked="", prunable="gone"),
        WorktreeRecord(Path("/c\nd"), bare=True),
    ]
