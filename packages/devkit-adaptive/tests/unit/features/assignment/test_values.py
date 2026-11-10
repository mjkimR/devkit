"""Pure path-prefix, parser and event policy checks."""

from pathlib import Path

import pytest
from devkit_adaptive.features.assignment.models.values import covers, fold, overlaps
from devkit_adaptive.features.assignment.repositories.git import parse_status, parse_worktrees


@pytest.mark.parametrize(
    "entry,path,expected",
    [("src", "src/a", True), ("src", "src", True), ("src", "src-other", False), (".", "anything", True)],
)
def test_literal_prefix(entry, path, expected):
    assert covers(entry, path) is expected
    assert overlaps(entry, path) is expected


def test_status_names_and_worktree_flags():
    assert parse_status(b"R  new name\0old name\0?? nested/\0") == ["nested", "new name", "old name"]
    records = parse_worktrees(
        b"worktree /tmp/a\0HEAD abc\0branch refs/heads/main\0\0worktree /tmp/b\0prunable moved\0\0"
    )
    assert next(record for path, record in records.items() if path == Path("/tmp/b").resolve())["prunable"] == "moved"


def test_fold_replaces_return_and_preserves_event_values():
    events = [
        {"id": "a1", "event": "assigned", "data": {"id": "a1", "status": "open"}},
        {"id": "a1", "event": "returned", "data": {"status": "failed"}},
        {"id": "a1", "event": "verified", "data": {"result": "fail"}},
        {"id": "a1", "event": "returned", "data": {"status": "completed"}},
    ]
    result = fold(events)["a1"]
    assert result["status"] == "returned" and result["return"]["status"] == "completed"
    assert result["verification"] is None
    assert events[0]["data"] == {"id": "a1", "status": "open"}
