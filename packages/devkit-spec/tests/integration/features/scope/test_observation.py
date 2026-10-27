"""Unit identity and observed-path granularity of one pinned or live source."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from spec_support.scope import git, write

from devkit_spec.features.scope.models.deadline import Deadline
from devkit_spec.features.scope.models.model import Granularity, ScopeSet
from devkit_spec.features.scope.models.observation import Candidate
from devkit_spec.features.scope.repositories.source import FilesystemReader, ReadBudget, TreeReader
from devkit_spec.features.scope.services.observation import add_paths, identify


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "dev-cleanup")
    for name, identity in (("20261027-cleanup", "SPEC-cleanup"), ("20261001-hook-cleanup", "SPEC-hook-cleanup")):
        write(root, f"specs/2026-10/{name}/spec.md", f"---\nid: {identity}\nstatus: in-progress\n---\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "units")
    return root


def candidate(root: Path) -> Candidate:
    return Candidate(source_id="worktree:x", ref="refs/heads/dev-cleanup", branch="dev-cleanup", worktree=str(root))


@pytest.mark.parametrize("pinned", [False, True])
def test_activity_slug_matches_only_the_exact_unit_name(repo: Path, pinned: bool) -> None:
    deadline = Deadline(10)
    reader = (
        TreeReader(repo, git(repo, "rev-parse", "HEAD"), deadline, ReadBudget())
        if pinned
        else FilesystemReader(repo, deadline, ReadBudget())
    )
    unit, meta = identify(candidate(repo), reader, repo, deadline)
    assert (unit, meta["id"]) == ("specs/2026-10/20261027-cleanup", "SPEC-cleanup")


def test_unreadable_observed_paths_keep_unknown_granularity(repo: Path, tmp_path: Path) -> None:
    outside = tmp_path / "outside.txt"
    outside.write_text("x")
    (repo / "escape").symlink_to(outside)
    (repo / "plain").write_text("x")
    (repo / "plain-child").write_text("x")
    os.mkfifo(repo / "pipe")
    scope = ScopeSet(id="x")
    reader = FilesystemReader(repo, Deadline(10), ReadBudget())
    add_paths(scope, ["escape", "pipe", "plain-child/inner", "plain"], reader, Deadline(10))
    assert [(p.path, p.kind) for p in scope.observed] == [
        ("escape", Granularity.UNKNOWN),
        ("pipe", Granularity.UNKNOWN),
        ("plain-child/inner", Granularity.UNKNOWN),
        ("plain", Granularity.FILE),
    ]
