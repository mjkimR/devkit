"""``devkit.worktree``: locate, start, finish and status against real repositories."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from devkit.advisory import ActionMode, AdvisoryError
from devkit.core.errors import ArgumentError, GitError
from devkit.worktree import (
    AddFailedError,
    BaseBehindError,
    BaseDetachedError,
    BaseDirtyError,
    BranchDeleteFailedError,
    BranchExistsError,
    BranchUnpushedError,
    ConflictError,
    DirtyError,
    FinishResult,
    LockedError,
    MergeNotFastForwardError,
    NestedError,
    NotFoundError,
    PullRequestPolicyError,
    RemoveFailedError,
    RunFromBaseError,
    UnmergedError,
    UnsupportedLayoutError,
    finish,
    lifecycle,
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


def marker(repo: Path, branch: str) -> str:
    """The ``branch.<branch>.devkitWorktree`` value in the common configuration; ``""`` when unset."""
    return git(repo, "config", "--local", "--default", "", "--get", f"branch.{branch}.devkitWorktree")


def test_locate_and_the_worktree_path(repo: Path) -> None:
    base = locate(repo)
    assert (base.root, base.base, base.branch, base.linked) == (repo, repo, "main", False)
    assert path_for(base, "dev-demo") == repo.parent / "repo-wt-dev-demo"
    created = start(base, "dev-demo")
    inner = locate(created.path)
    assert (inner.root, inner.base, inner.branch, inner.linked) == (created.path, repo, "dev-demo", True)
    git(repo, "checkout", "-q", "--detach")
    assert locate(repo).branch is None


def test_a_separate_git_directory_is_an_unsupported_layout(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    git(work, "init", "-q", "--separate-git-dir", str(tmp_path / "store.git"))
    with pytest.raises(UnsupportedLayoutError) as raised:
        locate(work)
    assert raised.value.mode is ActionMode.BLOCKED


def test_start_creates_from_base_head_and_refuses_to_start_it_again(repo: Path) -> None:
    write(repo, "uncommitted.txt", "stays in the base\n")
    result = start(locate(repo), "dev-demo")
    assert result.created and result.path == repo.parent / "repo-wt-dev-demo" and result.branch == "dev-demo"
    assert git(result.path, "rev-parse", "HEAD") == git(repo, "rev-parse", "HEAD")
    assert not (result.path / "uncommitted.txt").exists() and (repo / "uncommitted.txt").exists()
    assert marker(repo, "dev-demo") == str(result.path)
    assert git(result.path, "config", "--get", "branch.dev-demo.devkitWorktree") == str(result.path)  # common config
    with pytest.raises(BranchExistsError, match="already has its worktree"):
        start(locate(repo), "dev-demo")


def test_start_guards(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    with pytest.raises(NestedError) as nested:
        start(locate(created.path), "dev-other")
    assert nested.value.mode is ActionMode.BLOCKED
    write(created.path, "wip.txt", "x\n")
    with pytest.raises(BranchExistsError, match="already has its worktree") as existing:
        start(locate(repo), "dev-demo")  # dirty or clean, an existing branch's worktree is never started again
    assert existing.value.mode is ActionMode.INTERACTION
    git(repo, "worktree", "add", "-q", "-b", "elsewhere", str(repo.parent / "repo-wt-dev-taken"))
    with pytest.raises(ConflictError, match="on elsewhere"):
        start(locate(repo), "dev-taken")
    git(repo, "worktree", "add", "-q", "-b", "dev-busy", str(repo.parent / "somewhere"))
    with pytest.raises(BranchExistsError, match="checked out at"):
        start(locate(repo), "dev-busy")
    git(repo, "branch", "dev-existing")
    with pytest.raises(BranchExistsError, match="already exists"):
        start(locate(repo), "dev-existing")
    (repo.parent / "repo-wt-dev-plain").mkdir()
    with pytest.raises(ConflictError, match="not a worktree"):
        start(locate(repo), "dev-plain")
    for bad in ("demo", "dev-", "dev-Demo", "plan--x", "fix-demo", "dev-a/b", "dev-a b", "dev-" + "x" * 61, ""):
        with pytest.raises(ArgumentError):
            start(locate(repo), bad)


def test_start_refuses_a_registered_worktree_whose_directory_is_missing(repo: Path) -> None:
    gone = start(locate(repo), "dev-gone")
    shutil.rmtree(gone.path)
    with pytest.raises(ConflictError, match="directory is missing") as raised:
        start(locate(repo), "dev-gone")
    assert raised.value.mode is ActionMode.INTERACTION
    assert raised.value.fix == f"git -C {repo} worktree prune"


def test_setup_runs_once_in_a_new_worktree_without_the_callers_virtualenv(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("VIRTUAL_ENV", "/somewhere/.venv")
    setup = 'test -z "$VIRTUAL_ENV" && echo ran >> setup.log'
    result = start(locate(repo), "dev-demo", setup=setup)
    assert result.setup == setup and result.notices == []
    assert (result.path / "setup.log").read_text() == "ran\n"
    (result.path / "setup.log").unlink()
    with pytest.raises(BranchExistsError):  # an existing branch is never started again, so setup runs once
        start(locate(repo), "dev-demo", setup=setup)


def test_a_failed_setup_is_a_warning_and_keeps_the_worktree(repo: Path) -> None:
    result = start(locate(repo), "dev-demo", setup="echo broken >&2; exit 3")
    [warning] = result.notices
    assert warning.code == "WORKTREE_SETUP_FAILED" and warning.mode is ActionMode.CONTINUE
    assert "exited 3" in warning.message and "broken" in warning.message
    assert warning.fix is not None and warning.fix.endswith("&& echo broken >&2; exit 3")
    assert result.created and result.path.is_dir()


def _hook(repo: Path, name: str, body: str) -> None:
    hook = repo / ".git/hooks" / name
    hook.write_text("#!/bin/sh\n" + body)
    hook.chmod(0o755)


def _wait_for(path: Path, timeout: float = 5.0) -> str:
    """The text of ``path`` once a process has written it, waiting at most ``timeout`` seconds."""
    deadline = time.monotonic() + timeout
    while not path.exists():
        if time.monotonic() > deadline:
            pytest.fail(f"{path} was never written")
        time.sleep(0.02)
    return path.read_text()


def _assert_gone(pid: int, what: str, timeout: float = 5.0) -> None:
    """Fail (after killing it) when the process ``pid`` is still running ``timeout`` seconds from now."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.02)
    os.kill(pid, signal.SIGKILL)
    pytest.fail(f"{what} outlived its timeout")


def _only_the_base(repo: Path, slug: str) -> None:
    assert [entry.path for entry in status(locate(repo)).worktrees] == [repo]
    assert not (repo.parent / f"repo-wt-{slug}").exists() and git(repo, "branch", "--list", slug) == ""


def test_a_failed_worktree_add_removes_what_it_created_and_a_rerun_starts_afresh(repo: Path) -> None:
    _hook(repo, "post-checkout", "echo checkout hook broke >&2; exit 1\n")
    with pytest.raises(AddFailedError) as raised:
        start(locate(repo), "dev-demo")
    assert raised.value.code == "WORKTREE_ADD_FAILED" and raised.value.mode is ActionMode.INTERACTION
    assert "checkout hook broke" in raised.value.message and "were removed" in raised.value.message
    _only_the_base(repo, "dev-demo")
    (repo / ".git/hooks/post-checkout").unlink()
    assert start(locate(repo), "dev-demo").created


def test_a_failed_marker_write_removes_the_new_worktree_and_branch(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run_git = lifecycle.run_git

    def no_config(cwd: Path, *args: str, **options: Any) -> bytes:
        if args[:2] == ("config", "--local"):
            raise GitError("git config failed", returncode=4, stderr="error: could not lock config file")
        return run_git(cwd, *args, **options)

    monkeypatch.setattr(lifecycle, "run_git", no_config)
    with pytest.raises(
        AddFailedError, match=r"git config branch\.dev-demo\.devkitWorktree failed: error: could not lock"
    ):
        start(locate(repo), "dev-demo")
    _only_the_base(repo, "dev-demo")


def test_a_timed_out_worktree_add_removes_what_it_created(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(lifecycle, "CHECKOUT_TIMEOUT", 1.0)
    pidfile = tmp_path / "hook.pid"
    _hook(repo, "post-checkout", f"sleep 30 & echo $! > {pidfile}.tmp && mv {pidfile}.tmp {pidfile}; wait\n")
    with pytest.raises(AddFailedError, match=r"timed out after 1\.0s"):
        start(locate(repo), "dev-demo")
    _only_the_base(repo, "dev-demo")
    _assert_gone(int(_wait_for(pidfile)), "the post-checkout hook's child")


def test_a_branch_created_while_start_runs_is_left_alone(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    git(repo, "checkout", "-q", "-b", "elsewhere")
    commit(repo, "theirs.txt")
    git(repo, "checkout", "-q", "main")
    session = lifecycle._git_session

    def racing(cwd: Path, *args: str, **options: Any) -> bytes:
        if args[:2] == ("worktree", "add"):
            git(repo, "branch", "dev-demo", "elsewhere")  # another process takes the name after start checked it
        return session(cwd, *args, **options)

    monkeypatch.setattr(lifecycle, "_git_session", racing)
    with pytest.raises(BranchExistsError, match="created while start ran"):
        start(locate(repo), "dev-demo")
    assert git(repo, "rev-parse", "dev-demo") == git(repo, "rev-parse", "elsewhere")
    assert not (repo.parent / "repo-wt-dev-demo").exists()


def test_a_path_created_while_start_runs_is_left_alone(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = repo.parent / "repo-wt-dev-demo"
    session = lifecycle._git_session

    def racing(cwd: Path, *args: str, **options: Any) -> bytes:
        if args[:2] == ("worktree", "add"):
            write(path, "theirs.txt", "theirs\n")  # another process fills the path after start checked it
        return session(cwd, *args, **options)

    monkeypatch.setattr(lifecycle, "_git_session", racing)
    with pytest.raises(ConflictError, match="created while start ran"):
        start(locate(repo), "dev-demo")
    assert (path / "theirs.txt").read_text() == "theirs\n"
    assert git(repo, "branch", "--list", "dev-demo") == ""  # the branch Git created before refusing is removed


def test_a_branch_a_hook_committed_to_is_named_not_deleted(repo: Path) -> None:
    _hook(repo, "post-checkout", "git commit -q --allow-empty -m hooked && exit 1\n")
    with pytest.raises(AddFailedError) as raised:
        start(locate(repo), "dev-demo")
    assert raised.value.details == ("left: branch dev-demo (it no longer points at the base HEAD it was created from)",)
    assert git(repo, "branch", "--list", "dev-demo")


def test_what_a_failed_worktree_add_cannot_remove_is_named_with_its_command(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _hook(repo, "post-checkout", "exit 1\n")
    session = lifecycle._git_session

    def no_removal(cwd: Path, *args: str, **options: Any) -> bytes:
        if args[:2] == ("worktree", "remove"):
            raise GitError("git worktree failed", returncode=128, stderr="fatal: cannot remove")
        return session(cwd, *args, **options)

    monkeypatch.setattr(lifecycle, "_git_session", no_removal)
    with pytest.raises(AddFailedError) as raised:
        start(locate(repo), "dev-demo")
    path = repo.parent / "repo-wt-dev-demo"
    assert raised.value.details == (f"left: worktree {path}", "left: branch dev-demo")
    assert raised.value.fix == (
        f"Once the user agrees, git -C {repo} worktree remove --force --force {path} && git -C {repo} branch -D dev-demo,"
        " then rerun the same command"
    )
    monkeypatch.undo()
    git(repo, "worktree", "remove", "--force", "--force", str(path))
    git(repo, "branch", "-D", "dev-demo")


def test_a_timed_out_removal_names_the_half_removed_worktree(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    created = start(locate(repo), "dev-demo")
    git(repo, "merge", "-q", "--ff-only", "dev-demo")
    session = lifecycle._git_session

    def timing_out(cwd: Path, *args: str, **options: Any) -> bytes:
        if args[:2] == ("worktree", "remove"):
            assert options["timeout"] == lifecycle.CHECKOUT_TIMEOUT
            raise GitError("git worktree timed out after 1800.0s in somewhere") from subprocess.TimeoutExpired(
                ["git"], 1800.0
            )
        return session(cwd, *args, **options)

    monkeypatch.setattr(lifecycle, "_git_session", timing_out)
    with pytest.raises(RemoveFailedError, match="may be partly deleted") as raised:
        finish(locate(repo), "dev-demo")
    assert raised.value.fix == (
        f"Once the user agrees, git -C {repo} worktree remove --force {created.path}, then rerun the same command"
    )


def test_a_setup_that_times_out_is_stopped_with_its_children(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(lifecycle, "SETUP_TIMEOUT", 1.0)
    pidfile = tmp_path / "child.pid"
    result = start(
        locate(repo), "dev-demo", setup=f"sleep 30 & echo $! > {pidfile}.tmp && mv {pidfile}.tmp {pidfile}; wait"
    )
    [warning] = result.notices
    assert warning.code == "WORKTREE_SETUP_FAILED" and "did not finish within" in warning.message
    _assert_gone(int(_wait_for(pidfile)), "the setup's child")


def test_status_treats_a_worktree_on_an_unborn_branch_as_unmerged(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    git(created.path, "switch", "-q", "--orphan", "fresh")
    rows = {item.path: item for item in status(locate(repo)).worktrees}
    assert (rows[created.path].branch, rows[created.path].head, rows[created.path].merged) == ("fresh", None, False)


def test_finish_refuses_from_the_worktree_under_the_pr_policy_and_before_the_merge(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    with pytest.raises(RunFromBaseError):
        finish(locate(created.path), "dev-demo")
    with pytest.raises(PullRequestPolicyError) as policy:
        finish(locate(repo), "dev-demo", merge=True, pull_request="required")
    assert policy.value.mode is ActionMode.BLOCKED
    with pytest.raises(UnmergedError) as unmerged:
        finish(locate(repo), "dev-demo")
    assert unmerged.value.result is None and created.path.is_dir()
    with pytest.raises(NotFoundError):
        finish(locate(repo), "dev-nothing")


def test_finish_refuses_a_worktree_that_is_not_on_the_slugs_branch(repo: Path) -> None:
    detached = start(locate(repo), "dev-detached")
    git(detached.path, "checkout", "-q", "--detach")
    commit(detached.path, "lost.txt")  # on no branch: the branch "dev-detached" is still merged
    moved = start(locate(repo), "dev-moved")
    git(moved.path, "switch", "-q", "-c", "elsewhere")
    commit(moved.path, "work.txt")
    head = git(repo, "rev-parse", "HEAD")
    rows = {item.path: item for item in status(locate(repo)).worktrees}
    for slug, path in (("dev-detached", detached.path), ("dev-moved", moved.path)):
        assert rows[path].merged is False  # status and finish judge the same commits
        for merge in (False, True):
            with pytest.raises(ConflictError, match=f"not {slug};") as raised:
                finish(locate(repo), slug, merge=merge, pull_request="auto")
            assert raised.value.result is None and raised.value.mode is ActionMode.INTERACTION
        assert path.is_dir() and git(repo, "branch", "--list", slug)
    with pytest.raises(ArgumentError):
        finish(locate(repo), "main")  # not an activity branch
    git(repo, "switch", "-q", "-c", "dev-base")
    for merge in (False, True):
        with pytest.raises(ConflictError, match="the base checkout's branch"):
            finish(locate(repo), "dev-base", merge=merge, pull_request="auto")
    assert git(repo, "rev-parse", "HEAD") == head and git(repo, "branch", "--list", "dev-base")


def test_finish_refuses_a_locked_worktree_before_the_merge(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    git(repo, "worktree", "lock", "--reason", "in use", str(created.path))
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(LockedError) as raised:
        finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert raised.value.code == "WORKTREE_LOCKED" and raised.value.result is None
    assert raised.value.fix == f"git -C {repo} worktree unlock {created.path}"
    assert git(repo, "rev-parse", "HEAD") == head and created.path.is_dir()
    git(repo, "worktree", "unlock", str(created.path))
    assert finish(locate(repo), "dev-demo", merge=True, pull_request="auto").branch_deleted


def test_finish_merge_refuses_a_detached_base(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    git(repo, "checkout", "-q", "--detach")
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(BaseDetachedError) as raised:
        finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert raised.value.code == "WORKTREE_BASE_DETACHED" and raised.value.mode is ActionMode.INTERACTION
    assert raised.value.result is None and git(repo, "rev-parse", "HEAD") == head
    assert created.path.is_dir() and git(repo, "branch", "--list", "dev-demo")


def test_a_failed_branch_deletion_carries_the_result_and_a_rerun_deletes_the_branch(
    repo: Path, refuse_deleting: Callable[[Path, str], Path]
) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    hook = refuse_deleting(repo, "dev-demo")
    with pytest.raises(BranchDeleteFailedError) as raised:
        finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    partial = raised.value.result
    assert isinstance(partial, FinishResult) and raised.value.mode is ActionMode.INTERACTION
    assert (partial.merged, partial.removed, partial.branch_deleted) == (True, True, False)
    assert not created.path.exists() and git(repo, "branch", "--list", "dev-demo")
    assert marker(repo, "dev-demo") == str(created.path)
    hook.unlink()
    done = finish(locate(repo), "dev-demo")  # no worktree left, the merged branch remains: only the deletion runs
    assert (done.merged, done.removed, done.branch_deleted) == (False, True, True)
    assert git(repo, "branch", "--list", "dev-demo") == "" and marker(repo, "dev-demo") == ""  # branch -d drops it
    with pytest.raises(NotFoundError):
        finish(locate(repo), "dev-demo")
    git(repo, "checkout", "-q", "-b", "dev-spike")
    commit(repo, "dev-spike.txt")
    git(repo, "checkout", "-q", "main")
    with pytest.raises(NotFoundError, match="not merged"):
        finish(locate(repo), "dev-spike")
    assert git(repo, "branch", "--list", "dev-spike")


def test_finish_without_a_worktree_never_deletes_a_branch_start_did_not_create(repo: Path) -> None:
    git(repo, "branch", "dev-release")  # merged into the base HEAD, no worktree, no marker
    with pytest.raises(NotFoundError, match=r"no branch\.dev-release\.devkitWorktree marker") as raised:
        finish(locate(repo), "dev-release")
    assert raised.value.result is None and raised.value.mode is ActionMode.INTERACTION
    assert raised.value.fix == f"Once the user agrees, git -C {repo} branch -d dev-release"
    assert git(repo, "branch", "--list", "dev-release")
    created = start(locate(repo), "dev-demo")
    git(repo, "worktree", "remove", str(created.path))  # removed by hand: the marked branch resumes
    done = finish(locate(repo), "dev-demo")
    assert (done.removed, done.branch_deleted) == (True, True) and git(repo, "branch", "--list", "dev-demo") == ""


def test_finish_keeping_the_branch_never_resumes_a_branch_start_did_not_create(repo: Path) -> None:
    git(repo, "branch", "dev-old")  # merged into the base HEAD, no worktree, no marker
    seen: list[FinishResult] = []
    with pytest.raises(NotFoundError, match=r"no branch\.dev-old\.devkitWorktree marker") as raised:
        finish(locate(repo), "dev-old", delete_branch=False, before_remove=seen.append)
    assert raised.value.code == "WORKTREE_NOT_FOUND" and raised.value.result is None
    assert raised.value.fix is not None and "branch -d" not in raised.value.fix  # the configuration keeps branches
    assert seen == [] and git(repo, "branch", "--list", "dev-old").strip() == "dev-old"


def test_finish_keeping_the_branch_resumes_after_a_removed_worktree_until_it_completes(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    git(repo, "worktree", "remove", str(created.path))  # what a stopped run leaves: the marked branch resumes
    seen: list[bool | None] = []
    done = finish(locate(repo), "dev-demo", delete_branch=False, before_remove=lambda r: seen.append(r.removed))
    assert seen == [True] and (done.removed, done.branch_deleted) == (True, False)
    assert git(repo, "branch", "--list", "dev-demo").strip() == "dev-demo" and marker(repo, "dev-demo") == ""
    with pytest.raises(NotFoundError):
        finish(locate(repo), "dev-demo", delete_branch=False, before_remove=lambda r: seen.append(r.removed))
    assert seen == [True]  # the completed finish removed the marker: nothing runs again


def test_finish_keeping_a_branch_from_before_the_marker_completes_with_its_worktree(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    git(repo, "config", "--local", "--unset", "branch.dev-demo.devkitWorktree")  # a branch from before the marker
    first = finish(locate(repo), "dev-demo", delete_branch=False)
    assert (first.removed, first.branch_deleted) == (True, False) and not created.path.exists()
    assert git(repo, "branch", "--list", "dev-demo").strip() == "dev-demo"
    with pytest.raises(NotFoundError, match="not resumed automatically"):
        finish(locate(repo), "dev-demo", delete_branch=False)  # without a worktree only the marker resumes


def test_finish_with_a_worktree_needs_no_marker(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    git(repo, "config", "--local", "--unset", "branch.dev-demo.devkitWorktree")  # a branch from before the marker
    done = finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert (done.merged, done.removed, done.branch_deleted) == (True, True, True)
    assert not created.path.exists() and git(repo, "branch", "--list", "dev-demo") == ""


def test_a_failed_removal_carries_the_result_and_a_rerun_resumes(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "sub/work.txt")
    (created.path / "sub").chmod(0o555)  # Git cannot delete the file inside it
    try:
        with pytest.raises(RemoveFailedError) as raised:
            finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    finally:
        (created.path / "sub").chmod(0o755)
    partial = raised.value.result
    assert isinstance(partial, FinishResult) and raised.value.code == "WORKTREE_REMOVE_FAILED"
    assert (partial.merged, partial.removed, partial.branch_deleted) == (True, False, False)
    done = finish(locate(repo), "dev-demo")
    assert done.removed and done.branch_deleted and git(repo, "branch", "--list", "dev-demo") == ""


def test_finish_merges_resumes_after_a_dirty_worktree_and_cleans_up(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    write(repo, "dirty.txt", "x\n")
    with pytest.raises(BaseDirtyError):
        finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    (repo / "dirty.txt").unlink()
    write(created.path, "wip.txt", "x\n")
    with pytest.raises(DirtyError) as dirty:
        finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    partial = dirty.value.result
    assert isinstance(partial, FinishResult)
    assert (partial.merged, partial.push, partial.removed) == (True, "no-upstream", False)
    assert (repo / "work.txt").exists() and created.path.is_dir()
    (created.path / "wip.txt").unlink()
    done = finish(locate(repo), "dev-demo")  # already merged: no --merge needed to resume
    assert (done.merged, done.removed, done.branch_deleted) == (False, True, True)
    assert not created.path.exists() and "dev-demo" not in git(repo, "branch", "--list", "dev-demo")


def test_finish_without_branch_deletion_and_with_a_caller_cleanup(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    seen: list[tuple[bool | None, bool]] = []
    result = finish(
        locate(repo), "dev-demo", delete_branch=False, before_remove=lambda r: seen.append((r.removed, r.path.is_dir()))
    )
    assert seen == [(False, True)] and result.removed and not result.branch_deleted
    assert git(repo, "branch", "--list", "dev-demo").strip() == "dev-demo" and marker(repo, "dev-demo") == ""
    assert not created.path.exists()


def test_an_advisory_the_caller_cleanup_raises_carries_the_partial_result(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")

    class CleanupError(AdvisoryError):
        code = "CALLER_CLEANUP_FAILED"

    def cleanup(result: FinishResult) -> None:
        raise CleanupError("the caller's cleanup failed")

    with pytest.raises(CleanupError) as raised:
        finish(locate(repo), "dev-demo", merge=True, pull_request="auto", before_remove=cleanup)
    partial = getattr(raised.value, "result", None)
    assert isinstance(partial, FinishResult)
    assert (partial.merged, partial.push, partial.removed, partial.branch_deleted) == (
        True,
        "no-upstream",
        False,
        False,
    )
    assert created.path.is_dir() and (repo / "work.txt").exists()
    done = finish(locate(repo), "dev-demo")  # the merge stays done: the rerun resumes with the removal
    assert done.removed and done.branch_deleted


def test_finish_refuses_a_merge_that_is_not_a_fast_forward(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    commit(repo, "moved.txt")
    with pytest.raises(MergeNotFastForwardError) as raised:
        finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert raised.value.result is None and created.path.is_dir()


def _with_remote(repo: Path, tmp_path: Path) -> Path:
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "push", "-q", "-u", "origin", "main")
    return remote


def test_finish_pushes_the_merged_base_to_its_upstream(repo: Path, tmp_path: Path) -> None:
    remote = _with_remote(repo, tmp_path)
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    result = finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert result.push == "pushed" and result.notices == []
    assert git(remote, "rev-parse", "main") == git(repo, "rev-parse", "HEAD")


def test_a_failed_push_warns_and_the_cleanup_continues(repo: Path, tmp_path: Path) -> None:
    _with_remote(repo, tmp_path)
    git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    result = finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert (result.push, result.removed, result.branch_deleted) == ("failed", True, True)
    [warning] = result.notices
    assert warning.code == "WORKTREE_PUSH_FAILED" and warning.mode is ActionMode.CONTINUE
    assert warning.fix == f"git -C {repo} push origin refs/heads/main:refs/heads/main"


def moved_on(remote: Path, tmp_path: Path) -> None:
    """Push a commit to ``remote``'s ``main`` from another clone."""
    other = tmp_path / "other"
    git(tmp_path, "clone", "-q", "-b", "main", str(remote), str(other))
    git(other, "config", "user.email", "t@example.com")
    git(other, "config", "user.name", "t")
    commit(other, "theirs.txt")
    git(other, "push", "-q", "origin", "main")


def test_finish_refuses_to_merge_when_the_upstream_moved_on(repo: Path, tmp_path: Path) -> None:
    remote = _with_remote(repo, tmp_path)
    moved_on(remote, tmp_path)
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(BaseBehindError) as raised:
        finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert raised.value.code == "WORKTREE_BASE_BEHIND" and raised.value.result is None
    assert raised.value.fix == f"git -C {repo} pull --ff-only origin refs/heads/main"
    assert git(repo, "rev-parse", "HEAD") == head and created.path.is_dir()


def test_a_push_rejected_by_a_moved_upstream_has_its_own_code(repo: Path, tmp_path: Path) -> None:
    remote = _with_remote(repo, tmp_path)
    moved_on(remote, tmp_path)
    git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))  # the fetch fails: the check is skipped
    git(repo, "remote", "set-url", "--push", "origin", str(remote))
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    result = finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert (result.merged, result.push, result.removed, result.branch_deleted) == (True, "rejected", True, True)
    [warning] = result.notices
    assert warning.code == "WORKTREE_PUSH_REJECTED" and warning.mode is ActionMode.CONTINUE
    push = f"git -C {repo} push origin refs/heads/main:refs/heads/main"
    assert warning.fix == f"git -C {repo} pull --rebase origin refs/heads/main && {push}"


def test_finish_refuses_before_the_merge_when_the_branch_upstream_lacks_its_commits(repo: Path, tmp_path: Path) -> None:
    _with_remote(repo, tmp_path)
    created = start(locate(repo), "dev-demo")
    commit(created.path, "one.txt")
    git(created.path, "push", "-q", "-u", "origin", "dev-demo")
    commit(created.path, "two.txt")
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(BranchUnpushedError) as raised:
        finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert raised.value.code == "WORKTREE_BRANCH_UNPUSHED" and raised.value.result is None
    assert raised.value.fix == f"git -C {repo} push origin refs/heads/dev-demo:refs/heads/dev-demo"
    assert git(repo, "rev-parse", "HEAD") == head and created.path.is_dir()
    git(repo, "push", "-q", "origin", "refs/heads/dev-demo:refs/heads/dev-demo")
    done = finish(locate(repo), "dev-demo", merge=True, pull_request="auto")
    assert (done.push, done.removed, done.branch_deleted) == ("pushed", True, True)


def test_status_reports_worktrees_and_unmerged_branches_without_changing_anything(repo: Path) -> None:
    merged = start(locate(repo), "dev-merged")
    open_ = start(locate(repo), "dev-open")
    commit(open_.path, "work.txt")
    write(open_.path, "wip.txt", "x\n")
    gone = start(locate(repo), "dev-gone")
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
    managed = Path(".devkit/managed/authoring/rules/skill_document_size/rule.py")
    assert (repo / managed).is_file() and git(repo, "check-ignore", str(managed))
    result = start(locate(repo), "dev-demo", project=Path("."))
    assert result.synced is True and result.notices == []
    assert (result.path / managed).is_file()
    assert git(result.path, "status", "--porcelain") == ""  # sync wrote ignored files only


def test_sync_uses_the_worktree_environment_with_devkit_and_skips_without_a_receipt(repo: Path, tmp_path: Path) -> None:
    assert start(locate(repo), "dev-plain", project=Path(".")).synced is None
    write(repo, ".gitignore", ".venv/\n")  # as in any Python project
    synchronized(repo)
    marker = tmp_path / "used"
    script = tmp_path / "python"  # stands in for the worktree's .venv interpreter and records that it ran
    script.write_text(f'#!/bin/sh\necho used > {marker}\nexec {sys.executable} "$@"\n')
    script.chmod(0o755)
    setup = f"mkdir -p .venv/bin && cp {script} .venv/bin/python"
    without = start(locate(repo), "dev-without", setup=setup, project=Path("."))
    assert without.synced is True and not marker.exists()  # no devkit in that environment: this interpreter ran
    setup += " && mkdir -p .venv/lib/python3.12/site-packages/devkit_agt-0.0.0.dist-info"
    result = start(locate(repo), "dev-demo", setup=setup, project=Path("."))
    assert result.synced is True and marker.read_text() == "used\n"


def test_a_failed_sync_is_a_warning_and_keeps_the_worktree(repo: Path) -> None:
    write(repo, ".devkit/installation.json", "{")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "broken receipt")
    result = start(locate(repo), "dev-demo", project=Path("."))
    [warning] = result.notices
    assert result.synced is False and result.path.is_dir()
    assert warning.code == "WORKTREE_SYNC_FAILED" and warning.mode is ActionMode.CONTINUE
    # The sync's own error is passed on: its code and message, and its fix (rerunning would fail the same way).
    assert warning.message.startswith(f"devkit sync --locked exited 2 in {result.path}: (RECEIPT_INVALID) ")
    assert warning.fix is not None and warning.fix.startswith(f"In {result.path}: Restore .devkit/installation.json")


def test_a_stale_receipt_names_the_committed_file_and_its_fix(repo: Path) -> None:
    synchronized(repo)
    (repo / "AGENTS.md").unlink()  # committed state the receipt no longer matches
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "drop the guidance block")
    result = start(locate(repo), "dev-demo", project=Path("."))
    [warning] = result.notices
    assert result.synced is False
    assert warning.message.startswith(f"devkit sync --locked exited 1 in {result.path}: (RECEIPT_STALE) ")
    assert warning.target_files == (str(result.path / "AGENTS.md"),)
    # The committed change comes first, ahead of the managed copies --locked would have restored.
    assert warning.details[0] == "would create AGENTS.md" and warning.details[-1].startswith("and ")
    assert warning.fix == f"In {result.path}: devkit sync, then commit the files it changes"
    assert not (result.path / "AGENTS.md").exists()  # --locked wrote nothing


def test_output_that_is_not_an_error_object_keeps_its_headline(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:

    block = "[ERROR]  (SOMETHING_FAILED) the reason\n" + "".join(f"[DETAIL] line {n}\n" for n in range(8))
    failed = subprocess.CompletedProcess(["python"], 3, b"not json", block.encode())
    monkeypatch.setattr(lifecycle, "_execute", lambda *args: failed)
    warning = lifecycle._sync("python", tmp_path)
    assert warning is not None and warning.fix == f"cd {tmp_path} && python -m devkit sync --locked"
    assert warning.message.splitlines()[:2] == [
        "devkit sync --locked exited 3:",
        "[ERROR]  (SOMETHING_FAILED) the reason",
    ]
    assert warning.message.splitlines()[-1] == "[DETAIL] line 7"
