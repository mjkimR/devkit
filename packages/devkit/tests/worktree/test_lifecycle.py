"""``devkit.worktree``: locate, start, finish and status against real repositories."""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from devkit.advisory import ActionMode
from devkit.core.errors import ArgumentError
from devkit.worktree import (
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


def test_start_refuses_a_registered_worktree_whose_directory_is_missing(repo: Path) -> None:
    gone = start(locate(repo), "gone")
    shutil.rmtree(gone.path)
    with pytest.raises(ConflictError, match="directory is missing") as raised:
        start(locate(repo), "gone")
    assert raised.value.mode is ActionMode.INTERACTION
    assert raised.value.fix == f"git -C {repo} worktree prune"


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


def test_finish_refuses_a_worktree_that_is_not_on_the_slugs_branch(repo: Path) -> None:
    detached = start(locate(repo), "detached")
    git(detached.path, "checkout", "-q", "--detach")
    commit(detached.path, "lost.txt")  # on no branch: the branch "detached" is still merged
    moved = start(locate(repo), "moved")
    git(moved.path, "switch", "-q", "-c", "elsewhere")
    commit(moved.path, "work.txt")
    head = git(repo, "rev-parse", "HEAD")
    rows = {item.path: item for item in status(locate(repo)).worktrees}
    for slug, path in (("detached", detached.path), ("moved", moved.path)):
        assert rows[path].merged is False  # status and finish judge the same commits
        for merge in (False, True):
            with pytest.raises(ConflictError, match=f"not {slug};") as raised:
                finish(locate(repo), slug, merge=merge, pull_request=False)
            assert raised.value.result is None and raised.value.mode is ActionMode.INTERACTION
        assert path.is_dir() and git(repo, "branch", "--list", slug)
    for merge in (False, True):
        with pytest.raises(ConflictError, match="the base checkout's branch"):
            finish(locate(repo), "main", merge=merge, pull_request=False)
    assert git(repo, "rev-parse", "HEAD") == head and git(repo, "branch", "--list", "main")


def test_finish_refuses_a_locked_worktree_before_the_merge(repo: Path) -> None:
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    git(repo, "worktree", "lock", "--reason", "in use", str(created.path))
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(LockedError) as raised:
        finish(locate(repo), "demo", merge=True, pull_request=False)
    assert raised.value.code == "WORKTREE_LOCKED" and raised.value.result is None
    assert raised.value.fix == f"git -C {repo} worktree unlock {created.path}"
    assert git(repo, "rev-parse", "HEAD") == head and created.path.is_dir()
    git(repo, "worktree", "unlock", str(created.path))
    assert finish(locate(repo), "demo", merge=True, pull_request=False).branch_deleted


def test_finish_merge_refuses_a_detached_base(repo: Path) -> None:
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    git(repo, "checkout", "-q", "--detach")
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(BaseDetachedError) as raised:
        finish(locate(repo), "demo", merge=True, pull_request=False)
    assert raised.value.code == "WORKTREE_BASE_DETACHED" and raised.value.mode is ActionMode.INTERACTION
    assert raised.value.result is None and git(repo, "rev-parse", "HEAD") == head
    assert created.path.is_dir() and git(repo, "branch", "--list", "demo")


def test_a_failed_branch_deletion_carries_the_result_and_a_rerun_deletes_the_branch(
    repo: Path, refuse_deleting: Callable[[Path, str], Path]
) -> None:
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    hook = refuse_deleting(repo, "demo")
    with pytest.raises(BranchDeleteFailedError) as raised:
        finish(locate(repo), "demo", merge=True, pull_request=False)
    partial = raised.value.result
    assert isinstance(partial, FinishResult) and raised.value.mode is ActionMode.INTERACTION
    assert (partial.merged, partial.removed, partial.branch_deleted) == (True, True, False)
    assert not created.path.exists() and git(repo, "branch", "--list", "demo")
    hook.unlink()
    done = finish(locate(repo), "demo")  # no worktree left, the merged branch remains: only the deletion runs
    assert (done.merged, done.removed, done.branch_deleted) == (False, True, True)
    assert git(repo, "branch", "--list", "demo") == ""
    with pytest.raises(NotFoundError):
        finish(locate(repo), "demo")
    git(repo, "checkout", "-q", "-b", "spike")
    commit(repo, "spike.txt")
    git(repo, "checkout", "-q", "main")
    with pytest.raises(NotFoundError, match="not merged"):
        finish(locate(repo), "spike")
    assert git(repo, "branch", "--list", "spike")


def test_a_failed_removal_carries_the_result_and_a_rerun_resumes(repo: Path) -> None:
    created = start(locate(repo), "demo")
    commit(created.path, "sub/work.txt")
    (created.path / "sub").chmod(0o555)  # Git cannot delete the file inside it
    try:
        with pytest.raises(RemoveFailedError) as raised:
            finish(locate(repo), "demo", merge=True, pull_request=False)
    finally:
        (created.path / "sub").chmod(0o755)
    partial = raised.value.result
    assert isinstance(partial, FinishResult) and raised.value.code == "WORKTREE_REMOVE_FAILED"
    assert (partial.merged, partial.removed, partial.branch_deleted) == (True, False, False)
    done = finish(locate(repo), "demo")
    assert done.removed and done.branch_deleted and git(repo, "branch", "--list", "demo") == ""


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
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(BaseBehindError) as raised:
        finish(locate(repo), "demo", merge=True, pull_request=False)
    assert raised.value.code == "WORKTREE_BASE_BEHIND" and raised.value.result is None
    assert raised.value.fix == f"git -C {repo} pull --ff-only origin refs/heads/main"
    assert git(repo, "rev-parse", "HEAD") == head and created.path.is_dir()


def test_a_push_rejected_by_a_moved_upstream_has_its_own_code(repo: Path, tmp_path: Path) -> None:
    remote = _with_remote(repo, tmp_path)
    moved_on(remote, tmp_path)
    git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))  # the fetch fails: the check is skipped
    git(repo, "remote", "set-url", "--push", "origin", str(remote))
    created = start(locate(repo), "demo")
    commit(created.path, "work.txt")
    result = finish(locate(repo), "demo", merge=True, pull_request=False)
    assert (result.merged, result.push, result.removed, result.branch_deleted) == (True, "rejected", True, True)
    [warning] = result.notices
    assert warning.code == "WORKTREE_PUSH_REJECTED" and warning.mode is ActionMode.CONTINUE
    push = f"git -C {repo} push origin refs/heads/main:refs/heads/main"
    assert warning.fix == f"git -C {repo} pull --rebase origin refs/heads/main && {push}"


def test_finish_refuses_before_the_merge_when_the_branch_upstream_lacks_its_commits(repo: Path, tmp_path: Path) -> None:
    _with_remote(repo, tmp_path)
    created = start(locate(repo), "demo")
    commit(created.path, "one.txt")
    git(created.path, "push", "-q", "-u", "origin", "demo")
    commit(created.path, "two.txt")
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(BranchUnpushedError) as raised:
        finish(locate(repo), "demo", merge=True, pull_request=False)
    assert raised.value.code == "WORKTREE_BRANCH_UNPUSHED" and raised.value.result is None
    assert raised.value.fix == f"git -C {repo} push origin refs/heads/demo:refs/heads/demo"
    assert git(repo, "rev-parse", "HEAD") == head and created.path.is_dir()
    git(repo, "push", "-q", "origin", "refs/heads/demo:refs/heads/demo")
    done = finish(locate(repo), "demo", merge=True, pull_request=False)
    assert (done.push, done.removed, done.branch_deleted) == ("pushed", True, True)


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


def test_sync_uses_the_worktree_environment_with_devkit_and_skips_without_a_receipt(repo: Path, tmp_path: Path) -> None:
    assert start(locate(repo), "plain", project=Path(".")).synced is None
    write(repo, ".gitignore", ".venv/\n")  # as in any Python project, so the reused worktree is clean
    synchronized(repo)
    marker = tmp_path / "used"
    script = tmp_path / "python"  # stands in for the worktree's .venv interpreter and records that it ran
    script.write_text(f'#!/bin/sh\necho used > {marker}\nexec {sys.executable} "$@"\n')
    script.chmod(0o755)
    setup = f"mkdir -p .venv/bin && cp {script} .venv/bin/python"
    without = start(locate(repo), "without", setup=setup, project=Path("."))
    assert without.synced is True and not marker.exists()  # no devkit in that environment: this interpreter ran
    setup += " && mkdir -p .venv/lib/python3.12/site-packages/devkit-0.0.0.dist-info"
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
    assert "devkit sync --locked exited 2" in warning.message
    assert warning.fix == f"cd {result.path} && {sys.executable} -m devkit sync --locked"
