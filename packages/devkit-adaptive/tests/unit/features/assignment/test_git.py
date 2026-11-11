"""Assignment Git facts derived from core's worktree records and status paths."""

from pathlib import Path

import pytest
from devkit_adaptive.base.errors import WorktreeUnavailable
from devkit_adaptive.features.assignment.repositories import git
from devkit_core.core import WorktreeRecord


def test_dirty_strips_directory_slashes_and_merges_names(monkeypatch):
    # dirty_paths already lists both names of a rename, sorted; a directory keeps Git's trailing slash there.
    monkeypatch.setattr(git, "dirty_paths", lambda root: ["nested", "nested/", "new name", "old name"])
    assert git.dirty(Path("/repo")) == ["nested", "new name", "old name"]


@pytest.mark.parametrize(
    "record,available",
    [
        ({}, True),
        ({"locked": ""}, True),
        ({"prunable": ""}, False),
        ({"prunable": "moved"}, False),
        ({"bare": True}, False),
    ],
)
def test_require_worktree_refuses_bare_and_prunable_records(monkeypatch, tmp_path, record, available):
    monkeypatch.setattr(git, "worktree_records", lambda root: [WorktreeRecord(path=tmp_path, **record)])
    if available:
        assert git.require_worktree(tmp_path, tmp_path) == tmp_path.resolve()
    else:
        with pytest.raises(WorktreeUnavailable):
            git.require_worktree(tmp_path, tmp_path)


def test_require_worktree_refuses_an_unlisted_path(monkeypatch, tmp_path):
    monkeypatch.setattr(git, "worktree_records", lambda root: [])
    with pytest.raises(WorktreeUnavailable):
        git.require_worktree(tmp_path, tmp_path)
