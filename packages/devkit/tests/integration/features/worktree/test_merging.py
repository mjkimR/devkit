"""``devkit_agt.features.worktree.services.merging`` and ``finish --merge``: the result commit built outside the base checkout."""

from __future__ import annotations

import ast
import inspect
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import devkit_agt.features.worktree.services.merging as merging
import pytest
from click.testing import CliRunner
from devkit_agt.features.worktree import (
    CommitFailedError,
    GitUnsupportedError,
    MergeConflictError,
    MergeFailedError,
    MergeNotFastForwardError,
    WorktreeConfigError,
    build_result,
    finish,
    locate,
    merge_method,
    plan_finish,
    read_worktree_config,
    start,
)
from devkit_core.base.errors import GitError
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
    fix = raised.value.fix or ""
    assert raised.value.code == "WORKTREE_MERGE_CONFLICT" and "Merge the target branch into the task branch" in fix
    assert "devkit generated resolve" in fix
    assert refs(repo) == before and git(repo, "status", "--porcelain") == ""


def _conflicting(repo: Path, edits: Mapping[str, tuple[str | None, str | None]]) -> tuple[str, str]:
    """A task tip and a moved target that changed each path of ``edits`` (source text, target text; ``None`` deletes)."""
    for rel in edits:
        write(repo, rel, "base\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base files")
    path, _ = task(repo)
    for rel, (ours, _) in edits.items():
        if ours is None:
            git(path, "rm", "-q", rel)
        else:
            write(path, rel, ours)
    git(path, "add", ".")
    git(path, "commit", "-q", "-m", "source edits")
    for rel, (_, theirs) in edits.items():
        if theirs is None:
            git(repo, "rm", "-q", rel)
        else:
            write(repo, rel, theirs)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "target edits")
    return git(path, "rev-parse", "HEAD"), git(repo, "rev-parse", "HEAD")


def _advance(repo: Path, tip: str, moved: str, settle=None, *, prospective: bool = False) -> str:
    return build_result(
        repo,
        branch="dev-demo",
        target_branch="main",
        target=moved,
        source=tip,
        method="no-ff",
        advance=True,
        prospective=prospective,
        settle=settle,
    )


def test_settler_keeps_the_side_it_names_for_each_conflict(repo: Path) -> None:
    """``ADR-generated-conflicts-in-prepared-merge``: ``ours`` is the target, ``theirs`` the source."""
    edits = {"gen/a.json": ("source a\n", "target a\n"), "gen/b.json": ("source b\n", "target b\n")}
    tip, moved = _conflicting(repo, edits)
    asked: list[tuple[str, ...]] = []

    def settle(paths: tuple[str, ...]) -> dict[str, str]:
        asked.append(paths)
        return {"gen/a.json": "ours", "gen/b.json": "theirs"}

    before = refs(repo)
    result = _advance(repo, tip, moved, settle)
    assert asked == [("gen/a.json", "gen/b.json")]
    assert git(repo, "show", f"{result}:gen/a.json") == "target a"
    assert git(repo, "show", f"{result}:gen/b.json") == "source b"
    assert git(repo, "rev-parse", f"{result}^1", f"{result}^2").split() == [moved, tip]
    assert refs(repo) == before and git(repo, "status", "--porcelain") == ""


def test_seeded_path_is_removed_where_the_seed_side_deleted_it(repo: Path) -> None:
    tip, moved = _conflicting(repo, {"gen/a.json": ("source a\n", None), "gen/b.json": (None, "target b\n")})
    result = _advance(repo, tip, moved, lambda paths: dict.fromkeys(paths, "ours"))
    names = git(repo, "ls-tree", "-r", "--name-only", result).split()
    assert "gen/a.json" not in names and git(repo, "show", f"{result}:gen/b.json") == "target b"


def test_prospective_and_real_seeded_builds_share_one_tree(repo: Path) -> None:
    tip, moved = _conflicting(repo, {"gen/a.json": ("source a\n", "target a\n")})
    prospective = _advance(repo, tip, moved, lambda paths: dict.fromkeys(paths, "ours"), prospective=True)
    real = _advance(repo, tip, moved, lambda paths: dict.fromkeys(paths, "ours"))
    assert git(repo, "rev-parse", f"{prospective}^{{tree}}") == git(repo, "rev-parse", f"{real}^{{tree}}")


def test_unsettled_conflicts_refuse_without_changing_anything(repo: Path) -> None:
    tip, moved = _conflicting(repo, {"gen/a.json": ("source a\n", "target a\n"), "README.md": ("ours\n", "theirs\n")})
    before = refs(repo)
    with pytest.raises(MergeConflictError) as raised:
        _advance(repo, tip, moved, lambda paths: {"gen/a.json": "ours"})
    assert raised.value.details == ("README.md",) and "Merge the target branch" in (raised.value.fix or "")
    for settle in (None, lambda paths: dict.fromkeys(paths, "both")):
        with pytest.raises(MergeConflictError):
            _advance(repo, tip, moved, settle)
    refused = MergeConflictError("cannot settle", "gen/a.json: owned by nothing")

    def refuse(paths: tuple[str, ...]) -> dict[str, str]:
        raise refused

    with pytest.raises(MergeConflictError) as raised:
        _advance(repo, tip, moved, refuse)
    assert raised.value is refused
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


def test_plan_finish_plans_a_moved_target_only_with_advance_under_no_ff(repo: Path) -> None:
    """``ADR-moved-target-merge``: only local integration opts in; other callers keep the containment refusal."""
    _, tip = task(repo)
    moved = commit(repo, "theirs.txt")
    with pytest.raises(MergeNotFastForwardError) as raised:
        plan_finish(locate(repo), "dev-demo")  # the pull-request route and library callers
    assert 'merge = "no-ff"' in (raised.value.fix or "") and "never rebase" in (raised.value.fix or "")
    with pytest.raises(MergeNotFastForwardError):
        plan_finish(locate(repo), "dev-demo", merge_method="ff-only", advance=True)
    plan = plan_finish(locate(repo), "dev-demo", advance=True)
    assert (plan.source_sha, plan.target_sha, plan.already_merged) == (tip, moved, False)
    git(repo, "config", "user.name", "")
    with pytest.raises(CommitFailedError):
        plan_finish(locate(repo), "dev-demo", advance=True)


def test_prospective_build_is_deterministic_unsigned_and_unreferenced(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tip = task(repo)
    moved = commit(repo, "theirs.txt")
    before = refs(repo)
    args: dict[str, Any] = {
        "branch": "dev-demo",
        "target_branch": "main",
        "target": moved,
        "source": tip,
        "method": "no-ff",
    }
    first = build_result(repo, **args, advance=True, prospective=True)
    git(repo, "config", "commit.gpgSign", "true")
    git(repo, "config", "gpg.program", "false")  # a signing build would fail
    git(repo, "config", "i18n.commitEncoding", "ISO-8859-1")
    monkeypatch.setenv("TZ", "Pacific/Kiritimati")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Someone Else")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "else@example.invalid")
    assert build_result(repo, **args, advance=True, prospective=True) == first
    assert refs(repo) == before
    raw = git(repo, "cat-file", "commit", first)
    later = git(repo, "show", "-s", "--format=%cn <%ce> %ct", moved)
    assert "gpgsig" not in raw and "\nencoding " not in raw
    assert git(repo, "show", "-s", "--format=%an <%ae> %at|%cn <%ce> %ct", first) == f"{later}|{later}"
    assert git(repo, "rev-parse", f"{first}^1", f"{first}^2").split() == [moved, tip]
    assert git(repo, "log", "-1", "--format=%s", first) == "chore(merge): integrate dev-demo into main"


# AC-03 (SPEC-generated-conflicts-follow-ups)
def test_merge_tree_runs_on_the_shared_git_runner(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    imported = {
        alias.name
        for node in ast.walk(ast.parse(inspect.getsource(merging)))
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert "subprocess" not in imported

    calls: list[tuple[tuple[str, ...], dict[str, object]]] = []

    def failing(cwd: Path, *args: str, **kwargs: object) -> object:
        calls.append((args, kwargs))
        raise GitError("git merge-tree failed", returncode=128, stderr="fatal: bad revision")

    monkeypatch.setattr(merging, "run_git_result", failing)
    with pytest.raises(MergeFailedError, match="nothing was changed on the target: fatal: bad revision"):
        merging._merge_tree_output(repo, "main", "topic")
    assert calls == [
        (
            ("merge-tree", "--write-tree", "-z", "--no-messages", "main", "topic"),
            {"ok_returncodes": (0, 1), "timeout": merging.MERGE_TREE_TIMEOUT},
        )
    ]
