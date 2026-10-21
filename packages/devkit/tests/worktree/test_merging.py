"""``devkit.worktree.merging`` and ``finish --merge``: the result commit built outside the base checkout."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.worktree import (
    CommitFailedError,
    GitUnsupportedError,
    MergeConflictError,
    MergeNotFastForwardError,
    WorktreeConfigError,
    build_result,
    finish,
    locate,
    merge_method,
    merging,
    plan_finish,
    read_worktree_config,
    start,
)
from devkit_core.core.locks import file_lock
from testsupport.cli import cli
from testsupport.rules import git, init_repo, write


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return init_repo(tmp_path / "repo").resolve()


def commit(root: Path, rel: str, text: str = "x\n") -> str:
    write(root, rel, text)
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", f"add {rel}")
    return git(root, "rev-parse", "HEAD")


def task(repo: Path) -> tuple[Path, str]:
    created = start(locate(repo), "dev-demo")
    return created.path, commit(created.path, "work.txt")


def refs(repo: Path) -> str:
    return git(repo, "show-ref")


def test_merge_key_defaults_to_no_ff_and_rejects_other_values(repo: Path) -> None:
    assert read_worktree_config(repo).merge == "no-ff"
    write(repo, ".devkit/config.toml", '[worktree]\nmerge = "ff-only"\n')
    assert read_worktree_config(repo).merge == "ff-only"
    for value in ('"ff"', '"squash"', "true"):
        write(repo, ".devkit/config.toml", f"[worktree]\nmerge = {value}\n")
        with pytest.raises(WorktreeConfigError):
            read_worktree_config(repo)


def test_no_ff_build_commits_the_source_tree_onto_the_target(repo: Path) -> None:
    _, tip = task(repo)
    head = git(repo, "rev-parse", "HEAD")
    before = refs(repo)
    result = build_result(repo, branch="dev-demo", target_branch="main", target=head, source=tip, method="no-ff")
    assert refs(repo) == before  # no ref moves
    assert git(repo, "rev-parse", f"{result}^1", f"{result}^2").split() == [head, tip]
    assert git(repo, "rev-parse", f"{result}^{{tree}}") == git(repo, "rev-parse", f"{tip}^{{tree}}")
    assert git(repo, "log", "-1", "--format=%s", result) == "chore(merge): integrate dev-demo into main"


def test_ff_only_build_is_the_source_and_refuses_an_advanced_target(repo: Path) -> None:
    _, tip = task(repo)
    head = git(repo, "rev-parse", "HEAD")
    assert build_result(repo, branch="dev-demo", target_branch="main", target=head, source=tip, method="ff-only") == tip
    moved = commit(repo, "theirs.txt")
    with pytest.raises(MergeNotFastForwardError) as raised:
        build_result(repo, branch="dev-demo", target_branch="main", target=moved, source=tip, method="ff-only")
    assert "rebase" not in (raised.value.fix or "").replace("never rebase", "")


def test_advanced_target_needs_the_advance_flag_and_merges_cleanly_with_it(repo: Path) -> None:
    _, tip = task(repo)
    moved = commit(repo, "theirs.txt")
    with pytest.raises(MergeNotFastForwardError):
        build_result(repo, branch="dev-demo", target_branch="main", target=moved, source=tip, method="no-ff")
    result = build_result(
        repo, branch="dev-demo", target_branch="main", target=moved, source=tip, method="no-ff", advance=True
    )
    assert git(repo, "rev-parse", f"{result}^1", f"{result}^2").split() == [moved, tip]
    assert set(git(repo, "ls-tree", "--name-only", result).split()) == {"README.md", "theirs.txt", "work.txt"}


def test_conflicting_advance_is_refused_without_changing_anything(repo: Path) -> None:
    path, _ = task(repo)
    tip = commit(path, "README.md", "ours\n")
    moved = commit(repo, "README.md", "theirs\n")
    before = refs(repo)
    with pytest.raises(MergeConflictError) as raised:
        build_result(
            repo, branch="dev-demo", target_branch="main", target=moved, source=tip, method="no-ff", advance=True
        )
    assert raised.value.code == "WORKTREE_MERGE_CONFLICT" and "Merge the target branch into the task branch" in (
        raised.value.fix or ""
    )
    assert refs(repo) == before and git(repo, "status", "--porcelain") == ""


def test_old_git_is_refused_only_when_the_target_advanced(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, tip = task(repo)
    head = git(repo, "rev-parse", "HEAD")
    monkeypatch.setattr(merging, "git_version", lambda _base: (2, 37))
    assert build_result(repo, branch="dev-demo", target_branch="main", target=head, source=tip, method="no-ff")
    moved = commit(repo, "theirs.txt")
    with pytest.raises(GitUnsupportedError):
        build_result(
            repo, branch="dev-demo", target_branch="main", target=moved, source=tip, method="no-ff", advance=True
        )


def test_failed_signature_is_commit_failed(repo: Path) -> None:
    _, tip = task(repo)
    head = git(repo, "rev-parse", "HEAD")
    git(repo, "config", "commit.gpgSign", "true")
    git(repo, "config", "gpg.program", "false")
    with pytest.raises(CommitFailedError):
        build_result(repo, branch="dev-demo", target_branch="main", target=head, source=tip, method="no-ff")


def test_missing_identity_is_refused_before_any_change(repo: Path) -> None:
    _, tip = task(repo)
    head = git(repo, "rev-parse", "HEAD")
    git(repo, "config", "user.name", "")
    with pytest.raises(CommitFailedError):
        plan_finish(locate(repo), "dev-demo")
    with pytest.raises(CommitFailedError):
        finish(locate(repo), "dev-demo", merge=True, network="forbid")
    assert git(repo, "rev-parse", "HEAD") == head and git(repo, "rev-parse", "dev-demo") == tip
    assert plan_finish(locate(repo), "dev-demo", merge_method="ff-only").merge_method == "ff-only"


def test_finish_merge_lands_a_merge_commit_and_a_rerun_builds_nothing(repo: Path) -> None:
    path, tip = task(repo)
    head = git(repo, "rev-parse", "HEAD")
    result = finish(locate(repo), "dev-demo", merge=True, network="forbid", delete_branch=False)
    landed = git(repo, "rev-parse", "HEAD")
    assert result.merged and git(repo, "rev-parse", "HEAD^1", "HEAD^2").split() == [head, tip]
    assert git(repo, "rev-parse", "HEAD^{tree}") == git(repo, "rev-parse", f"{tip}^{{tree}}")
    assert not path.exists()
    # What a run stopped after the merge leaves: the marked branch, already contained in the base.
    git(repo, "config", "branch.dev-demo.devkitWorktree", str(path))
    again = finish(locate(repo), "dev-demo", merge=True, network="forbid", delete_branch=False)
    assert again.merged and git(repo, "rev-parse", "HEAD") == landed


def test_finish_merge_ff_only_fast_forwards_and_refuses_an_advanced_base(repo: Path) -> None:
    _, tip = task(repo)
    moved = commit(repo, "theirs.txt")
    with pytest.raises(MergeNotFastForwardError):
        finish(locate(repo), "dev-demo", merge=True, network="forbid", merge_method="no-ff")
    assert git(repo, "rev-parse", "HEAD") == moved
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    finish(locate(repo), "dev-demo", merge=True, network="forbid", merge_method="ff-only")
    assert git(repo, "rev-parse", "HEAD") == tip


def test_source_policy_ff_only_wins(repo: Path) -> None:
    path, _ = task(repo)
    assert merge_method(repo, "no-ff", "refs/heads/dev-demo") == "no-ff"
    assert merge_method(repo, "ff-only", "refs/heads/dev-demo") == "ff-only"
    commit(path, ".devkit/config.toml", '[worktree]\nmerge = "ff-only"\n')
    assert merge_method(repo, "no-ff", "refs/heads/dev-demo") == "ff-only"


def test_cli_finish_merge_takes_the_integration_lock(repo: Path) -> None:
    path, tip = task(repo)
    with file_lock(repo / ".git" / merging.LOCK_NAME):
        held = CliRunner().invoke(cli, ["worktree", "finish", "dev-demo", "--merge", "--local-only", "-w", str(repo)])
        assert held.exit_code == 2 and "LOCK_HELD" in held.stderr and path.exists()
    done = CliRunner().invoke(
        cli, ["worktree", "finish", "dev-demo", "--merge", "--local-only", "-w", str(repo), "--format", "json"]
    )
    assert done.exit_code == 0, done.output
    assert json.loads(done.stdout)["merged"] is True and git(repo, "rev-parse", "HEAD^2") == tip
