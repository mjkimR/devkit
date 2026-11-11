"""Unit identity and observed-path granularity of one pinned or live source."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from spec_support.scope import GIT_ENV, git, write

from devkit_spec.features.scope.models.deadline import Deadline
from devkit_spec.features.scope.models.model import Granularity, ScopeSet
from devkit_spec.features.scope.models.observation import Candidate
from devkit_spec.features.scope.repositories.source import FilesystemReader, ReadBudget, TreeReader
from devkit_spec.features.scope.services.observation import add_paths, committed, identify


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


# The committed-range cases of the retired registry pipeline (observe_git), now covered by collect's only
# implementation (``CAP-COLL-work-scope-registry`` 4.1, 4.9).


def _range_repo(tmp_path: Path) -> Path:
    root = tmp_path / "range"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    for path in ("src/a.py", "src/b.py", "src/shared.py"):
        write(root, path, "x = 0\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "base")
    return root


def _committed(root: Path, base: str, cap: str = "") -> tuple[list[str], list[str]]:
    paths, issues, _ = committed(root, git(root, "rev-parse", "task"), base, cap, Deadline(10))
    return sorted(paths), [issue.reason for issue in issues]


def test_a_merged_base_branch_is_not_observed_but_a_conflict_resolution_is(tmp_path: Path) -> None:
    root = _range_repo(tmp_path)
    registration = git(root, "rev-parse", "HEAD")
    git(root, "switch", "-q", "-c", "task")
    write(root, "src/a.py", "a = 1\n")
    write(root, "src/shared.py", "s = 'task'\n")
    git(root, "commit", "-qam", "task")
    git(root, "switch", "-q", "main")
    write(root, "src/b.py", "b = 1\n")
    write(root, "src/shared.py", "s = 'main'\n")
    git(root, "commit", "-qam", "upstream")
    git(root, "switch", "-q", "task")
    merge = subprocess.run(
        ["git", "merge", "-q", "main"], cwd=root, env={**os.environ, **GIT_ENV}, capture_output=True, check=False
    )
    assert merge.returncode == 1, "the merge conflicts on src/shared.py"
    write(root, "src/shared.py", "s = 'resolved'\n")
    git(root, "commit", "-qam", "merge main")
    main = git(root, "rev-parse", "main")
    assert _committed(root, main) == (["src/a.py", "src/shared.py"], []), "branch-relative"
    assert _committed(root, main, registration) == (["src/a.py", "src/shared.py"], []), "registered cap"
    assert _committed(root, "", registration)[1] == ["unknown-base"]


def test_a_base_on_another_branch_never_widens_past_the_registration_cap(tmp_path: Path) -> None:
    root = _range_repo(tmp_path)
    git(root, "switch", "-q", "-c", "other")
    write(root, "src/b.py", "b = 'other'\n")
    git(root, "commit", "-qam", "other")
    git(root, "switch", "-q", "main")
    write(root, "src/shared.py", "s = 'main'\n")  # main moves on after other forked
    git(root, "commit", "-qam", "main")
    registration = git(root, "rev-parse", "HEAD")
    git(root, "switch", "-q", "-c", "task")
    write(root, "src/a.py", "a = 2\n")
    git(root, "commit", "-qam", "task")
    other = git(root, "rev-parse", "other")
    assert _committed(root, other, registration) == (["src/a.py"], []), "the range starts at the cap"


def test_a_task_registered_after_its_own_commit_keeps_only_paths_both_ranges_change(tmp_path: Path) -> None:
    root = _range_repo(tmp_path)
    git(root, "switch", "-q", "-c", "task")
    write(root, "src/a.py", "a = 2\n")
    git(root, "commit", "-qam", "task")
    registration = git(root, "rev-parse", "HEAD")
    git(root, "switch", "-q", "main")
    write(root, "src/b.py", "b = 2\n")
    git(root, "commit", "-qam", "upstream")
    git(root, "switch", "-q", "task")
    git(root, "merge", "-q", "--no-edit", "main")  # the fork point and the cap have diverged
    write(root, "src/shared.py", "s = 'task'\n")
    git(root, "commit", "-qam", "after the merge")
    assert _committed(root, git(root, "rev-parse", "main"), registration) == (["src/shared.py"], [])
