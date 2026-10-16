"""Activity branches: remote duplicates, ``start_branch`` (``--no-worktree``), ``attach`` (``--existing-branch``) and
the finish guard."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from click.testing import CliRunner
from devkit.advisory import ActionMode
from devkit.cli import cli
from devkit.core.errors import ArgumentError
from devkit.worktree import (
    AttachRefusedError,
    BaseDetachedError,
    BaseOnBranchError,
    BranchExistsError,
    BranchOutOfSyncError,
    ConflictError,
    DirtyError,
    NestedError,
    NotFoundError,
    UnitInvalidError,
    UnmergedError,
    attach,
    discard,
    extensions,
    finish,
    locate,
    start,
    start_branch,
)
from testsupport.rules import git, init_repo, write


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return init_repo(tmp_path / "repo").resolve()


def commit(root: Path, rel: str, text: str = "x\n") -> None:
    write(root, rel, text)
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", f"add {rel}")


def config(repo: Path, branch: str, key: str) -> str:
    return git(repo, "config", "--local", "--default", "", "--get", f"branch.{branch}.{key}")


def with_remote(repo: Path, tmp_path: Path) -> Path:
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "push", "-q", "-u", "origin", "main")
    return remote


def remote_branch(repo: Path, tmp_path: Path, branch: str, unit: str = "docs/specs/demo") -> str:
    """Push ``branch`` with a unit directory to origin from another clone; its tip."""
    other = tmp_path / "other"
    git(tmp_path, "clone", "-q", str(tmp_path / "remote.git"), str(other))
    git(other, "config", "user.email", "t@example.com")
    git(other, "config", "user.name", "t")
    git(other, "switch", "-q", "-c", branch)
    commit(other, f"{unit}/spec.md")
    git(other, "push", "-q", "origin", branch)
    return git(other, "rev-parse", "HEAD")


# -- new branches: duplicates on a remote ------------------------------------------------------------------------


def test_start_refuses_a_branch_a_remote_has(repo: Path, tmp_path: Path) -> None:
    with_remote(repo, tmp_path)
    remote_branch(repo, tmp_path, "dev-demo")  # never fetched: only ls-remote sees it
    for begin in (lambda: start(locate(repo), "dev-demo"), lambda: start_branch(locate(repo), "dev-demo")):
        with pytest.raises(BranchExistsError, match="already exists on origin") as raised:
            begin()
        assert raised.value.fix is not None and "--existing-branch origin/dev-demo" in raised.value.fix
    assert git(repo, "branch", "--list", "dev-demo") == "" and git(repo, "branch", "--show-current") == "main"


def test_an_unreachable_remote_is_judged_by_its_tracking_ref_with_a_warning(repo: Path, tmp_path: Path) -> None:
    with_remote(repo, tmp_path)
    remote_branch(repo, tmp_path, "dev-seen")
    git(repo, "fetch", "-q", "origin")
    git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    with pytest.raises(BranchExistsError, match="exists on origin"):
        start(locate(repo), "dev-seen")
    result = start(locate(repo), "dev-fresh")
    [warning] = result.notices
    assert warning.code == "WORKTREE_REMOTE_UNCHECKED" and warning.mode is ActionMode.CONTINUE
    assert "refs/remotes/origin/dev-fresh" in warning.message and result.created


# -- start_branch -----------------------------------------------------------------------------------------------


def test_start_branch_switches_the_checkout_and_carries_uncommitted_changes(repo: Path) -> None:
    write(repo, "wip.txt", "carried\n")
    result = start_branch(locate(repo), "dev-demo")
    assert (result.branch, result.slug, result.checkout, result.started_from) == ("dev-demo", "demo", repo, "main")
    assert git(repo, "branch", "--show-current") == "dev-demo" and (repo / "wip.txt").read_text() == "carried\n"
    assert config(repo, "dev-demo", "devkitWorktree") == str(repo)
    assert config(repo, "dev-demo", "devkitBase") == "main"
    with pytest.raises(BranchExistsError):
        start_branch(locate(repo), "dev-demo")


def test_start_branch_refusals(repo: Path) -> None:
    created = start(locate(repo), "dev-task")
    with pytest.raises(NestedError):
        start_branch(locate(created.path), "dev-other")
    with pytest.raises(BranchExistsError, match="checked out at"):
        start_branch(locate(repo), "dev-task")
    git(repo, "checkout", "-q", "--detach")
    with pytest.raises(BaseDetachedError):
        start_branch(locate(repo), "dev-other")
    with pytest.raises(ArgumentError):
        start_branch(locate(repo), "other")


def test_a_branch_without_a_worktree_is_integrated_from_the_base(repo: Path) -> None:
    start_branch(locate(repo), "dev-demo")
    commit(repo, "work.txt")
    with pytest.raises(BaseOnBranchError) as raised:  # routine: the agent switches back and reruns
        finish(locate(repo), "dev-demo", merge=True)
    assert raised.value.fix == f"git -C {repo} switch main" and raised.value.mode is ActionMode.AUTO
    git(repo, "switch", "-q", "main")
    with pytest.raises(UnmergedError):
        finish(locate(repo), "dev-demo")
    git(repo, "switch", "-q", "-c", "elsewhere")
    with pytest.raises(ConflictError, match="started from main") as off_base:
        finish(locate(repo), "dev-demo", merge=True)  # it is integrated into the branch it was started from only
    assert off_base.value.fix == f"git -C {repo} switch main, then rerun"
    git(repo, "switch", "-q", "main")
    done = finish(locate(repo), "dev-demo", merge=True)
    assert (done.merged, done.removed, done.branch_deleted) == (True, True, True)
    assert done.path == repo  # the checkout it was started in, where post-finish cleanup finds its records
    assert (repo / "work.txt").is_file() and git(repo, "branch", "--list", "dev-demo") == ""


# -- attach -----------------------------------------------------------------------------------------------------


def local_branch(repo: Path, branch: str, unit: str = "docs/specs/demo") -> str:
    git(repo, "switch", "-q", "-c", branch)
    commit(repo, f"{unit}/spec.md")
    git(repo, "switch", "-q", "main")
    return git(repo, "rev-parse", branch)


def test_attach_gives_an_existing_branch_its_worktree_without_touching_it(repo: Path) -> None:
    tip = local_branch(repo, "dev-demo")
    seen: list[tuple[Any, ...]] = []
    result = attach(
        locate(repo),
        "dev-demo",
        source="dev-demo",
        unit="docs/specs/demo",
        check=lambda *args: seen.append(args),
    )
    path = repo.parent / "repo-wt-dev-demo"
    assert (result.path, result.created, result.existing, result.unit) == (path, True, True, "docs/specs/demo")
    assert seen == [(repo, "dev-demo", "docs/specs/demo", tip)]
    assert git(path, "rev-parse", "HEAD") == tip and (path / "docs/specs/demo/spec.md").is_file()
    assert config(repo, "dev-demo", "devkitWorktree") == str(path)
    assert config(repo, "dev-demo", "devkitUnit") == "docs/specs/demo"
    again = attach(locate(repo), "dev-demo", source="dev-demo", unit="docs/specs/demo")
    assert (again.created, again.path) == (False, path)
    with pytest.raises(BranchExistsError, match="already has its worktree"):  # only attach continues it
        start(locate(repo), "dev-demo")
    git(repo, "worktree", "remove", str(path))
    with pytest.raises(BranchExistsError):
        start(locate(repo), "dev-demo")  # without the worktree, a plain start never takes the branch over


def test_attach_refusals_change_nothing(repo: Path) -> None:
    local_branch(repo, "dev-demo")
    position = locate(repo)
    with pytest.raises(NotFoundError, match="neither locally"):
        attach(position, "dev-none", source="dev-none", unit="docs/specs/demo")
    with pytest.raises(ArgumentError, match="--existing-branch"):
        attach(position, "dev-demo", source="dev-other", unit="docs/specs/demo")
    with pytest.raises(ArgumentError, match="--existing-branch"):
        attach(position, "dev-demo", source="upstream/dev-demo", unit="docs/specs/demo")  # no such remote
    for unit in ("docs/specs/missing", "docs/specs/demo/spec.md", "../x", "/abs", ""):
        with pytest.raises(UnitInvalidError) as raised:
            attach(position, "dev-demo", source="dev-demo", unit=unit)
        assert raised.value.mode is ActionMode.INPUT_ERROR

    def refuse(*args: Any) -> None:
        raise AttachRefusedError("not this unit", "spec: the unit's slug is other")

    with pytest.raises(AttachRefusedError):
        attach(position, "dev-demo", source="dev-demo", unit="docs/specs/demo", check=refuse)
    assert not (repo.parent / "repo-wt-dev-demo").exists() and config(repo, "dev-demo", "devkitUnit") == ""


def test_attach_resolves_a_project_relative_unit(repo: Path) -> None:
    local_branch(repo, "dev-demo", unit="app/docs/specs/demo")
    result = attach(locate(repo), "dev-demo", source="dev-demo", unit="docs/specs/demo", project=Path("app"))
    assert result.unit == "docs/specs/demo" and result.created


def test_attach_tracks_a_remote_only_branch(repo: Path, tmp_path: Path) -> None:
    with_remote(repo, tmp_path)
    tip = remote_branch(repo, tmp_path, "dev-demo")
    git(repo, "fetch", "-q", "origin")
    result = attach(locate(repo), "dev-demo", source="origin/dev-demo", unit="docs/specs/demo")
    assert result.created and git(repo, "rev-parse", "dev-demo") == tip
    assert git(repo, "rev-parse", "--abbrev-ref", "dev-demo@{upstream}") == "origin/dev-demo"


def test_attach_refuses_a_local_branch_behind_its_remote_and_accepts_one_ahead(repo: Path, tmp_path: Path) -> None:
    with_remote(repo, tmp_path)
    local_branch(repo, "dev-demo")
    git(repo, "push", "-q", "-u", "origin", "dev-demo")
    other = tmp_path / "other"
    git(tmp_path, "clone", "-q", "-b", "dev-demo", str(tmp_path / "remote.git"), str(other))
    git(other, "config", "user.email", "t@example.com")
    git(other, "config", "user.name", "t")
    commit(other, "docs/specs/demo/more.md")
    git(other, "push", "-q", "origin", "dev-demo")
    git(repo, "fetch", "-q", "origin")
    before = git(repo, "rev-parse", "dev-demo")
    with pytest.raises(BranchOutOfSyncError, match="is behind origin/dev-demo") as raised:
        attach(locate(repo), "dev-demo", source="dev-demo", unit="docs/specs/demo")
    assert raised.value.fix == f"git -C {repo} fetch . refs/remotes/origin/dev-demo:refs/heads/dev-demo, then rerun"
    assert git(repo, "rev-parse", "dev-demo") == before
    git(repo, "fetch", "-q", ".", "refs/remotes/origin/dev-demo:refs/heads/dev-demo")
    git(repo, "switch", "-q", "dev-demo")
    commit(repo, "docs/specs/demo/local.md")  # ahead of the remote: attached as it is
    git(repo, "switch", "-q", "main")
    attached = attach(locate(repo), "dev-demo", source="dev-demo", unit="docs/specs/demo")
    assert attached.created
    assert [n.code for n in attached.notices] == ["WORKTREE_BRANCH_AHEAD"]
    assert attached.notices[0].fix == f"git -C {repo} push origin dev-demo when the work is to be shared"


def test_attach_moves_the_base_checkout_off_the_branch_to_its_recorded_base(repo: Path) -> None:
    start_branch(locate(repo), "dev-demo")
    commit(repo, "docs/specs/demo/spec.md")
    write(repo, "wip.txt", "x\n")
    with pytest.raises(ConflictError, match="uncommitted changes"):
        attach(locate(repo), "dev-demo", source="dev-demo", unit="docs/specs/demo")
    (repo / "wip.txt").unlink()
    result = attach(locate(repo), "dev-demo", source="dev-demo", unit="docs/specs/demo")
    assert git(repo, "branch", "--show-current") == "main" and result.created
    git(repo, "worktree", "remove", str(result.path))
    git(repo, "switch", "-q", "dev-demo")
    git(repo, "config", "--local", "--unset", "branch.dev-demo.devkitBase")
    with pytest.raises(ConflictError, match="no branch to return to"):
        attach(locate(repo), "dev-demo", source="dev-demo", unit="docs/specs/demo")


def test_attach_refuses_the_branch_checked_out_elsewhere(repo: Path, tmp_path: Path) -> None:
    local_branch(repo, "dev-demo")
    git(repo, "worktree", "add", "-q", str(tmp_path / "elsewhere"), "dev-demo")
    with pytest.raises(BranchExistsError, match="checked out at"):
        attach(locate(repo), "dev-demo", source="dev-demo", unit="docs/specs/demo")


# -- finish guard -----------------------------------------------------------------------------------------------


def test_the_guard_runs_before_the_merge_and_only_with_merge(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    head, tip = git(repo, "rev-parse", "HEAD"), git(created.path, "rev-parse", "HEAD")
    seen: list[tuple[str, str]] = []

    def refuse(merge_base: str, branch_tip: str) -> None:
        seen.append((merge_base, branch_tip))
        raise ConflictError("blocked by the guard")

    with pytest.raises(ConflictError, match="blocked by the guard") as raised:
        finish(locate(repo), "dev-demo", merge=True, guard=refuse)
    assert seen == [(head, tip)] and raised.value.result is None
    assert git(repo, "rev-parse", "HEAD") == head and created.path.is_dir()
    assert finish(locate(repo), "dev-demo", merge=True, guard=lambda *args: None).merged


def entries(monkeypatch: pytest.MonkeyPatch, wanted: str, **callables: Any) -> None:
    """Make ``callables`` the only extensions of the entry-point group ``wanted``."""
    fake = [SimpleNamespace(name=name, value=f"fake:{name}", load=lambda c=c: c) for name, c in callables.items()]
    monkeypatch.setattr(extensions.metadata, "entry_points", lambda group=None: fake if group == wanted else [])


def test_finish_guard_extensions_block_and_fail_closed(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    head = git(repo, "rev-parse", "HEAD")
    seen: list[tuple[Any, ...]] = []

    def blocking(*args: Any) -> list[str]:
        seen.append(args)
        return ["docs/specs/demo: unresolved problem envelopes/worker-02.yaml"]

    entries(monkeypatch, extensions.FINISH_GUARD_GROUP, units=blocking, quiet=lambda *args: None)
    result = CliRunner().invoke(cli, ["worktree", "finish", "dev-demo", "--merge", "-w", str(repo)])
    assert result.exit_code == 2 and "(WORKTREE_BLOCKED)" in result.stderr
    assert "units: docs/specs/demo: unresolved problem envelopes/worker-02.yaml" in result.stderr
    assert seen == [(repo, "dev-demo", head, git(created.path, "rev-parse", "HEAD"))]
    entries(monkeypatch, extensions.FINISH_GUARD_GROUP, broken=lambda *args: 3)
    failed = CliRunner().invoke(cli, ["worktree", "finish", "dev-demo", "--merge", "-w", str(repo), "--format", "json"])
    assert failed.exit_code == 2 and json.loads(failed.stdout)["error"]["code"] == "WORKTREE_GUARD_FAILED"
    assert git(repo, "rev-parse", "HEAD") == head
    entries(monkeypatch, extensions.FINISH_GUARD_GROUP, quiet=lambda *args: [])
    assert CliRunner().invoke(cli, ["worktree", "finish", "dev-demo", "--merge", "-w", str(repo)]).exit_code == 0


def test_attach_check_extensions_refuse_and_fail_closed(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    local_branch(repo, "dev-demo")
    args = ["worktree", "start", "dev-demo", "--existing-branch", "dev-demo", "--unit", "docs/specs/demo", "-w"]
    entries(monkeypatch, extensions.ATTACH_CHECK_GROUP, spec=lambda *a: ["the unit belongs to plan-demo"])
    refused = CliRunner().invoke(cli, [*args, str(repo), "--format", "json"])
    assert refused.exit_code == 2 and json.loads(refused.stdout)["error"]["code"] == "WORKTREE_ATTACH_REFUSED"

    def broken(*a: Any) -> None:
        raise RuntimeError("boom")

    entries(monkeypatch, extensions.ATTACH_CHECK_GROUP, spec=broken)
    failed = CliRunner().invoke(cli, [*args, str(repo)])
    assert failed.exit_code == 2 and "(WORKTREE_ATTACH_CHECK_FAILED)" in failed.stderr and "spec: boom" in failed.stderr
    entries(monkeypatch, extensions.ATTACH_CHECK_GROUP)
    done = CliRunner().invoke(cli, [*args, str(repo)])
    path = repo.parent / "repo-wt-dev-demo"
    assert done.exit_code == 0, done.output
    assert done.stdout.splitlines()[0] == (
        f"[WORKTREE_STARTED: dev-demo path={path} base={repo} created=yes existing=yes unit=docs/specs/demo"
        " setup=- synced=-]"
    )


def test_the_start_flags_go_together(repo: Path) -> None:
    for extra in (["--existing-branch", "dev-demo"], ["--unit", "x"], ["--no-worktree", "--unit", "x"]):
        result = CliRunner().invoke(cli, ["worktree", "start", "dev-demo", *extra, "-w", str(repo), "--format", "json"])
        assert result.exit_code == 2 and json.loads(result.stdout)["error"]["code"] == "ARGUMENT_INVALID"
    started = CliRunner().invoke(cli, ["worktree", "start", "dev-demo", "--no-worktree", "-w", str(repo)])
    assert started.exit_code == 0, started.output
    assert started.stdout == f"[BRANCH_STARTED: dev-demo checkout={repo} from=main]\n"


# -- review fixes: remote comparison without an upstream, the merged commit, discard -------------------------------


def test_attach_compares_a_branch_without_upstream_with_the_remote_that_has_it(repo: Path, tmp_path: Path) -> None:
    with_remote(repo, tmp_path)
    start_branch(locate(repo), "dev-demo")
    commit(repo, "docs/specs/demo/spec.md")
    git(repo, "push", "-q", "origin", "dev-demo")  # no -u: start_branch sets no upstream
    git(repo, "switch", "-q", "main")
    other = tmp_path / "other"
    git(tmp_path, "clone", "-q", "-b", "dev-demo", str(tmp_path / "remote.git"), str(other))
    git(other, "config", "user.email", "t@example.com")
    git(other, "config", "user.name", "t")
    commit(other, "docs/specs/demo/more.md")
    git(other, "push", "-q", "origin", "dev-demo")
    git(repo, "fetch", "-q", "origin")
    with pytest.raises(BranchOutOfSyncError, match="is behind origin/dev-demo"):
        attach(locate(repo), "dev-demo", source="dev-demo", unit="docs/specs/demo")


def test_attach_refuses_a_named_remote_that_was_never_fetched(repo: Path, tmp_path: Path) -> None:
    with_remote(repo, tmp_path)
    local_branch(repo, "dev-demo")
    with pytest.raises(NotFoundError, match="was never fetched") as raised:
        attach(locate(repo), "dev-demo", source="origin/dev-demo", unit="docs/specs/demo")
    assert raised.value.fix == f"git -C {repo} fetch origin, then rerun"


def test_finish_merges_the_commit_the_guard_checked(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    head = git(repo, "rev-parse", "HEAD")

    def moving(merge_base: str, tip: str) -> None:
        commit(created.path, "late.txt")  # a run still committing while finish checks the branch

    with pytest.raises(ConflictError, match="moved while finish checked it"):
        finish(locate(repo), "dev-demo", merge=True, guard=moving)
    assert git(repo, "rev-parse", "HEAD") == head


def test_discard_drops_an_unmerged_branch_and_its_worktree(repo: Path) -> None:
    created = start(locate(repo), "dev-demo")
    commit(created.path, "work.txt")
    write(created.path, "wip.txt", "x\n")
    with pytest.raises(DirtyError):
        discard(locate(repo), "dev-demo")  # never by force
    (created.path / "wip.txt").unlink()
    seen: list[str] = []
    done = discard(locate(repo), "dev-demo", before_remove=lambda result: seen.append(result.branch))
    assert (done.discarded, done.merged, done.removed, done.branch_deleted) == (True, False, True, True)
    assert seen == ["dev-demo"] and not created.path.exists() and git(repo, "branch", "--list", "dev-demo") == ""
    start_branch(locate(repo), "dev-solo")
    commit(repo, "solo.txt")
    with pytest.raises(BaseOnBranchError):
        discard(locate(repo), "dev-solo")  # the base checkout is on it
    git(repo, "switch", "-q", "main")
    solo = discard(locate(repo), "dev-solo")
    assert solo.path == repo and solo.branch_deleted and git(repo, "branch", "--list", "dev-solo") == ""
    git(repo, "branch", "dev-foreign")  # an activity branch devkit did not start (another checkout, by hand)
    assert discard(locate(repo), "dev-foreign").branch_deleted
    assert git(repo, "branch", "--list", "dev-foreign") == ""


def test_finish_discard_runs_post_finish_and_excludes_merge(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    start(locate(repo), "dev-demo")
    seen: list[dict[str, Any]] = []
    entries(monkeypatch, "devkit.post_finish", spec=lambda base, result: seen.append(result))
    both = CliRunner().invoke(cli, ["worktree", "finish", "dev-demo", "--merge", "--discard", "-w", str(repo)])
    assert both.exit_code == 2 and "ARGUMENT_INVALID" in both.stderr
    done = CliRunner().invoke(cli, ["worktree", "finish", "dev-demo", "--discard", "-w", str(repo)])
    assert done.exit_code == 0 and "merged=no" in done.stdout and "discarded=yes" in done.stdout
    assert seen and seen[0]["discarded"] is True and seen[0]["branch"] == "dev-demo"
