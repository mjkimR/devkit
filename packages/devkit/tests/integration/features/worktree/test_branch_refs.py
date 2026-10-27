"""Activity branches under Git settings that change ref handling: ``branch.autoSetupMerge always`` and a tag sharing a
branch's name."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit_agt.features.worktree import StartBranch, WorktreeStatusQuery, finish, locate, plan_finish, start
from testsupport.rules import git, init_repo, write


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return init_repo(tmp_path / "repo").resolve()


def commit(root: Path, rel: str) -> str:
    write(root, rel, "x\n")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", f"add {rel}")
    return git(root, "rev-parse", "HEAD")


def upstream(repo: Path, branch: str) -> str:
    return git(repo, "for-each-ref", "--format=%(upstream)", f"refs/heads/{branch}")


# -- branch.autoSetupMerge always ---------------------------------------------------------------------------------


def test_start_creates_untracked_branches_under_auto_setup_merge_always(repo: Path) -> None:
    git(repo, "config", "branch.autoSetupMerge", "always")
    created = start(locate(repo), "dev-wt")
    commit(created.path, "wt.txt")
    assert upstream(repo, "dev-wt") == ""
    done = finish(locate(repo), "dev-wt", merge=True, network="forbid")
    assert done.merged and done.branch_deleted
    StartBranch().execute(locate(repo), "dev-sw")
    commit(repo, "sw.txt")
    assert upstream(repo, "dev-sw") == ""
    git(repo, "switch", "-q", "main")
    done = finish(locate(repo), "dev-sw", merge=True, network="forbid")
    assert done.merged and done.branch_deleted


def test_a_branch_tracking_the_local_base_is_deletable_once_merged_into_it(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    tip = commit(created.path, "work.txt")
    git(repo, "branch", "-q", "--set-upstream-to=main", "dev-demo")
    plan = plan_finish(locate(repo), "dev-demo")
    assert plan.delete_branch and plan.source_upstream == "refs/heads/main"
    done = finish(locate(repo), "dev-demo", merge=True, network="forbid")
    assert done.merged and done.branch_deleted and git(repo, "merge-base", "--is-ancestor", tip, "HEAD") == ""


# -- a tag sharing a branch's name --------------------------------------------------------------------------------


def test_a_tag_named_like_the_base_branch_leaves_the_branch_readable(repo: Path) -> None:
    git(repo, "tag", "main")
    assert locate(repo).branch == "main"
    assert WorktreeStatusQuery().execute(locate(repo)).base_branch == "main"


def test_status_names_an_unmerged_branch_shadowed_by_a_tag_by_its_branch_name(repo: Path) -> None:
    git(repo, "switch", "-q", "-c", "dev-loose")
    commit(repo, "loose.txt")
    git(repo, "switch", "-q", "main")
    git(repo, "tag", "dev-loose", "main")
    created = start(locate(repo), "dev-held")
    git(repo, "tag", "dev-held", "main")
    status = WorktreeStatusQuery().execute(locate(repo))
    assert [item.name for item in status.branches] == ["dev-loose"]
    assert any(item.branch == "dev-held" and item.path == created.path for item in status.worktrees)
