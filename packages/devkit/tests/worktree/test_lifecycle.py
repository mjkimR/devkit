"""``devkit.worktree``: locate, start, finish and status against real repositories."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from devkit.advisory import ActionMode
from devkit.core.errors import ArgumentError
from devkit.worktree import (
    BaseDirtyError,
    BranchExistsError,
    ConflictError,
    DirtyError,
    FinishResult,
    MergeNotFastForwardError,
    NestedError,
    NotFoundError,
    PullRequestPolicyError,
    RunFromBaseError,
    UnmergedError,
    UnsupportedLayoutError,
    finish,
    locate,
    path_for,
    start,
    status,
)
from testsupport.rules import git, init_repo, write


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return init_repo(tmp_path / "repo").resolve()


def commit(root: Path, rel: str, text: str = "x\n") -> None:
    write(root, rel, text)
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", f"add {rel}")


def test_locate_and_the_worktree_path(repo: Path) -> None:
    base = locate(repo)
    assert (base.root, base.base, base.branch, base.linked) == (repo, repo, "main", False)
    assert path_for(base, "demo") == repo.parent / "repo-wt-demo"
    created = start(base, "demo")
    inner = locate(created.path)
    assert (inner.root, inner.base, inner.branch, inner.linked) == (created.path, repo, "demo", True)
    git(repo, "checkout", "-q", "--detach")
    assert locate(repo).branch is None


def test_a_separate_git_directory_is_an_unsupported_layout(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    git(work, "init", "-q", "--separate-git-dir", str(tmp_path / "store.git"))
    with pytest.raises(UnsupportedLayoutError) as raised:
        locate(work)
    assert raised.value.mode is ActionMode.BLOCKED


def test_start_creates_from_base_head_and_reuses_a_clean_worktree(repo: Path) -> None:
    write(repo, "uncommitted.txt", "stays in the base\n")
    result = start(locate(repo), "demo")
    assert result.created and result.path == repo.parent / "repo-wt-demo" and result.branch == "demo"
    assert git(result.path, "rev-parse", "HEAD") == git(repo, "rev-parse", "HEAD")
    assert not (result.path / "uncommitted.txt").exists() and (repo / "uncommitted.txt").exists()
    again = start(locate(repo), "demo")
    assert not again.created and again.path == result.path


def test_start_guards(repo: Path) -> None:
    created = start(locate(repo), "demo")
    with pytest.raises(NestedError) as nested:
        start(locate(created.path), "other")
    assert nested.value.mode is ActionMode.BLOCKED
    write(created.path, "wip.txt", "x\n")
    with pytest.raises(ConflictError, match="uncommitted changes") as conflict:
        start(locate(repo), "demo")
    assert conflict.value.mode is ActionMode.INTERACTION
    git(repo, "worktree", "add", "-q", "-b", "elsewhere", str(repo.parent / "repo-wt-taken"))
    with pytest.raises(ConflictError, match="on elsewhere"):
        start(locate(repo), "taken")
    git(repo, "worktree", "add", "-q", "-b", "busy", str(repo.parent / "somewhere"))
    with pytest.raises(BranchExistsError, match="checked out at"):
        start(locate(repo), "busy")
    git(repo, "branch", "existing")
    with pytest.raises(BranchExistsError, match="already exists"):
        start(locate(repo), "existing")
    (repo.parent / "repo-wt-plain").mkdir()
    with pytest.raises(ConflictError, match="not a worktree"):
        start(locate(repo), "plain")
    for bad in ("Demo", "-x", "a/b", "a b", "x" * 65, ""):
        with pytest.raises(ArgumentError):
            start(locate(repo), bad)


def test_setup_runs_once_in_a_new_worktree_without_the_callers_virtualenv(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("VIRTUAL_ENV", "/somewhere/.venv")
    setup = 'test -z "$VIRTUAL_ENV" && echo ran >> setup.log'
    result = start(locate(repo), "demo", setup=setup)
    assert result.setup == setup and result.notices == []
    assert (result.path / "setup.log").read_text() == "ran\n"
    (result.path / "setup.log").unlink()
    assert start(locate(repo), "demo", setup=setup).notices == [] and not (result.path / "setup.log").exists()


def test_a_failed_setup_is_a_warning_and_keeps_the_worktree(repo: Path) -> None:
    result = start(locate(repo), "demo", setup="echo broken >&2; exit 3")
    [warning] = result.notices
    assert warning.code == "WORKTREE_SETUP_FAILED" and warning.mode is ActionMode.CONTINUE
    assert "exited 3" in warning.message and "broken" in warning.message
    assert warning.fix is not None and warning.fix.endswith("&& echo broken >&2; exit 3")
    assert result.created and result.path.is_dir()


def test_finish_refuses_from_the_worktree_under_the_pr_policy_and_before_the_merge(repo: Path) -> None:
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    with pytest.raises(RunFromBaseError):
        finish(locate(created.path), "demo")
    with pytest.raises(PullRequestPolicyError) as policy:
        finish(locate(repo), "demo", merge=True)
    assert policy.value.mode is ActionMode.BLOCKED
    with pytest.raises(UnmergedError) as unmerged:
        finish(locate(repo), "demo")
    assert unmerged.value.result is None and created.path.is_dir()
    with pytest.raises(NotFoundError):
        finish(locate(repo), "nothing")


def test_finish_merges_resumes_after_a_dirty_worktree_and_cleans_up(repo: Path) -> None:
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    write(repo, "dirty.txt", "x\n")
    with pytest.raises(BaseDirtyError):
        finish(locate(repo), "demo", merge=True, pull_request=False)
    (repo / "dirty.txt").unlink()
    write(created.path, "wip.txt", "x\n")
    with pytest.raises(DirtyError) as dirty:
        finish(locate(repo), "demo", merge=True, pull_request=False)
    partial = dirty.value.result
    assert isinstance(partial, FinishResult)
    assert (partial.merged, partial.push, partial.removed) == (True, "no-upstream", False)
    assert (repo / "work.txt").exists() and created.path.is_dir()
    (created.path / "wip.txt").unlink()
    done = finish(locate(repo), "demo")  # already merged: no --merge needed to resume
    assert (done.merged, done.removed, done.branch_deleted) == (False, True, True)
    assert not created.path.exists() and "demo" not in git(repo, "branch", "--list", "demo")


def test_finish_without_branch_deletion_and_with_a_caller_cleanup(repo: Path) -> None:
    created = start(locate(repo), "demo")
    seen: list[tuple[bool, bool]] = []
    result = finish(
        locate(repo), "demo", delete_branch=False, before_remove=lambda r: seen.append((r.removed, r.path.is_dir()))
    )
    assert seen == [(False, True)] and result.removed and not result.branch_deleted
    assert git(repo, "branch", "--list", "demo").strip() == "demo"
    assert not created.path.exists()


def test_finish_refuses_a_merge_that_is_not_a_fast_forward(repo: Path) -> None:
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    commit(repo, "moved.txt")
    with pytest.raises(MergeNotFastForwardError) as raised:
        finish(locate(repo), "demo", merge=True, pull_request=False)
    assert raised.value.result is None and created.path.is_dir()


def _with_remote(repo: Path, tmp_path: Path) -> Path:
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "push", "-q", "-u", "origin", "main")
    return remote


def test_finish_pushes_the_merged_base_to_its_upstream(repo: Path, tmp_path: Path) -> None:
    remote = _with_remote(repo, tmp_path)
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    result = finish(locate(repo), "demo", merge=True, pull_request=False)
    assert result.push == "pushed" and result.notices == []
    assert git(remote, "rev-parse", "main") == git(repo, "rev-parse", "HEAD")


def test_a_failed_push_warns_and_the_cleanup_continues(repo: Path, tmp_path: Path) -> None:
    _with_remote(repo, tmp_path)
    git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    result = finish(locate(repo), "demo", merge=True, pull_request=False)
    assert (result.push, result.removed, result.branch_deleted) == ("failed", True, True)
    [warning] = result.notices
    assert warning.code == "WORKTREE_PUSH_FAILED" and warning.mode is ActionMode.CONTINUE
    assert warning.fix == f"git -C {repo} push origin refs/heads/main:refs/heads/main"


def test_status_reports_worktrees_and_unmerged_branches_without_changing_anything(repo: Path) -> None:
    merged = start(locate(repo), "merged")
    open_ = start(locate(repo), "open")
    commit(open_.path, "work.txt")
    write(open_.path, "wip.txt", "x\n")
    gone = start(locate(repo), "gone")
    shutil.rmtree(gone.path)
    git(repo, "branch", "orphan", "HEAD")
    git(repo, "checkout", "-q", "-b", "side")
    commit(repo, "side.txt")
    git(repo, "checkout", "-q", "main")
    git(repo, "branch", "-q", "lonely", "side")
    result = status(locate(open_.path))
    rows = {item.path.name: item for item in result.worktrees}
    assert result.base == repo and result.base_branch == "main"
    assert (rows["repo"].role, rows["repo"].merged, rows["repo"].dirty) == ("base", None, False)
    assert (rows[merged.path.name].merged, rows[merged.path.name].dirty) == (True, False)
    assert (rows[open_.path.name].merged, rows[open_.path.name].dirty) == (False, True)
    assert (rows[gone.path.name].prunable, rows[gone.path.name].dirty) == (True, None)
    assert [branch.name for branch in result.branches] == ["lonely", "side"]  # orphan is merged
    assert merged.path.is_dir() and open_.path.is_dir()


def synchronized(repo: Path) -> Path:
    """``repo`` as a committed devkit project with the ``authoring`` bundle (its rules live under managed/)."""
    subprocess.run(
        [sys.executable, "-m", "devkit", "add", "authoring", "-w", str(repo)], check=True, capture_output=True
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "devkit")
    return repo


def test_start_restores_the_managed_files_a_fresh_checkout_lacks(repo: Path) -> None:
    synchronized(repo)
    managed = Path(".devkit/managed/authoring/rules/skill_document_size/skill_document_size.py")
    assert (repo / managed).is_file() and git(repo, "check-ignore", str(managed))
    result = start(locate(repo), "demo", project=Path("."))
    assert result.synced is True and result.notices == []
    assert (result.path / managed).is_file()
    assert git(result.path, "status", "--porcelain") == ""  # sync wrote ignored files only


def test_sync_prefers_the_worktree_environment_and_skips_without_a_receipt(repo: Path, tmp_path: Path) -> None:
    assert start(locate(repo), "plain", project=Path(".")).synced is None
    write(repo, ".gitignore", ".venv/\n")  # as in any Python project, so the reused worktree is clean
    synchronized(repo)
    marker = tmp_path / "used"
    script = tmp_path / "python"  # stands in for the worktree's .venv interpreter and records that it ran
    script.write_text(f'#!/bin/sh\necho used > {marker}\nexec {sys.executable} "$@"\n')
    script.chmod(0o755)
    setup = f"mkdir -p .venv/bin && cp {script} .venv/bin/python"
    result = start(locate(repo), "demo", setup=setup, project=Path("."))
    assert result.synced is True and marker.read_text() == "used\n"
    assert start(locate(repo), "demo", project=Path(".")).synced is None  # reused: nothing runs


def test_a_failed_sync_is_a_warning_and_keeps_the_worktree(repo: Path) -> None:
    write(repo, ".devkit/installation.json", "{")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "broken receipt")
    result = start(locate(repo), "demo", project=Path("."))
    [warning] = result.notices
    assert result.synced is False and result.path.is_dir()
    assert warning.code == "WORKTREE_SYNC_FAILED" and warning.mode is ActionMode.CONTINUE
    assert "devkit sync exited 2" in warning.message
    assert warning.fix == f"cd {result.path} && {sys.executable} -m devkit sync"
