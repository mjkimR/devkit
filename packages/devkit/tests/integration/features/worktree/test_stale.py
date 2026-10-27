"""Stale activity branches: ``stale_branches``, ``devkit worktree status --stale`` and the hygiene report."""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

import devkit_agt.features.worktree.usecases.stale as stale_module
import pytest
from click.testing import CliRunner
from devkit.advisory import ActionMode
from devkit_agt.features.worktree import locate, stale_branches
from devkit_agt.features.worktree.repositories.pull_request import CommandResult
from testsupport.cli import cli
from testsupport.rules import git, init_repo, write

DAY = 86400


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return init_repo(tmp_path / "repo").resolve()


def aged_branch(repo: Path, branch: str, days: int, start: str = "main", unit: str | None = None) -> None:
    """Create ``branch`` from ``start`` with one commit dated ``days`` ago (holding ``unit``/spec.md when given),
    leaving the checkout on ``start``."""
    git(repo, "switch", "-q", "-c", branch, start)
    write(repo, f"{branch}.txt", "x\n")
    if unit is not None:
        write(repo, f"{unit}/spec.md", "x\n")
    git(repo, "add", ".")
    when = f"@{int(datetime.now(UTC).timestamp()) - days * DAY} +0000"
    env = {**os.environ, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when}
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", branch], check=True, env=env)
    git(repo, "switch", "-q", start)


def fake_gh(pulls: list[dict] | None = None, *, auth: int = 0, pr_list: int = 0) -> Callable[..., CommandResult]:
    def run(cwd: Path, args: list[str], **_: object) -> CommandResult:
        if args[:2] == ["auth", "status"]:
            return CommandResult(auth)
        assert args[:2] == ["pr", "list"] and "--state" in args and "all" in args
        return CommandResult(pr_list, json.dumps(pulls or []))

    return run


def recent(days: int) -> str:
    return (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_stale_is_skipped_with_a_notice_without_gh(repo: Path) -> None:
    aged_branch(repo, "dev-old", 30)
    for code in (1, 127):
        result = stale_branches(locate(repo), gh=fake_gh(auth=code))
        assert (result.checked, result.stale, result.branches) == (False, [], 0)
        [notice] = result.notices
        assert notice.code == "WORKTREE_STALE_SKIPPED" and notice.mode is ActionMode.NOTE


def test_stale_judges_commits_and_pull_requests_of_activity_branches_only(repo: Path, tmp_path: Path) -> None:
    aged_branch(repo, "dev-old", 30, unit="docs/specs/old")
    aged_branch(repo, "plan-busy", 30)  # an old commit, but its pull request moved yesterday
    aged_branch(repo, "dev-new", 1)
    aged_branch(repo, "side", 90)  # not an activity branch
    git(repo, "config", "--local", "branch.dev-old.devkitUnit", "docs/specs/old")
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    git(repo, "remote", "add", "origin", str(remote))
    aged_branch(repo, "dev-gone", 20)
    git(repo, "push", "-q", "origin", "dev-gone", "dev-old")
    git(repo, "fetch", "-q", "origin")
    git(repo, "branch", "-q", "-D", "dev-gone")  # only its remote-tracking copy is left
    pulls = [
        {"headRefName": "dev-old", "state": "OPEN", "isDraft": True, "updatedAt": recent(20), "url": "https://pr/1"},
        {"headRefName": "dev-old", "state": "CLOSED", "isDraft": False, "updatedAt": recent(40), "url": "https://pr/0"},
        {"headRefName": "plan-busy", "state": "OPEN", "isDraft": False, "updatedAt": recent(1), "url": "https://pr/2"},
        {"headRefName": "dev-gone", "state": "OPEN", "mergeStateStatus": "BLOCKED", "updatedAt": recent(19)},
    ]
    result = stale_branches(locate(repo), "14d", gh=fake_gh(pulls))
    assert result.checked and result.branches == 4 and result.notices == []
    rows = {item.branch: item for item in result.stale}
    assert list(rows) == ["dev-old", "dev-gone"]  # most idle first
    old, gone = rows["dev-old"], rows["dev-gone"]
    assert (old.unit, old.pr, old.pr_url, old.refs) == ("docs/specs/old", "draft", "https://pr/1", ("local", "origin"))
    assert (gone.unit, gone.pr, gone.refs) == (None, "blocked", ("origin",))
    assert old.last_activity.date() == (datetime.now(UTC) - timedelta(days=20)).date()  # the PR is later
    warning = gone.warning(repo, "14d")
    assert warning.code == "WORKTREE_STALE_BRANCH" and warning.mode is ActionMode.CONTINUE
    assert warning.fix is None  # no recorded unit: no runnable resume command
    assert list(warning.details)[-2:] == [
        "to resume it: uv run devkit worktree start dev-gone --existing-branch origin/dev-gone --unit followed by its"
        " unit directory",
        f"to discard it, only once the user decides: close its pull request, git -C {repo} push origin --delete"
        " dev-gone",
    ]
    assert warning.what_to_report == "Activity branch dev-gone is idle; ask whether to resume or discard it"
    assert stale_branches(locate(repo), "3w", gh=fake_gh(pulls)).stale == []


def test_a_failed_pull_request_lookup_judges_by_commits_alone(repo: Path) -> None:
    aged_branch(repo, "dev-old", 30)
    result = stale_branches(locate(repo), gh=fake_gh(pr_list=1))
    [item] = result.stale
    assert item.pr == "unknown"
    assert result.notices == []  # no GitHub remote: nothing to report on every run
    git(repo, "remote", "add", "origin", "https://github.com/example/repo.git")
    [notice] = stale_branches(locate(repo), gh=fake_gh(pr_list=1)).notices
    assert notice.code == "WORKTREE_STALE_PR_UNKNOWN" and notice.fix is None


def test_the_stale_command_lists_and_warns(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    aged_branch(repo, "dev-old", 30)
    monkeypatch.setattr(stale_module, "run_gh", fake_gh())
    result = CliRunner().invoke(cli, ["worktree", "status", "--stale", "-w", str(repo)])
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert lines[0].startswith("[STALE_BRANCH: dev-old unit=- last_activity=") and lines[0].endswith(
        " pr=none refs=local]"
    )
    assert lines[1] == "[SUMMARY: checked=yes branches=1 stale=1 stale_after=14d]"
    assert "(WORKTREE_STALE_BRANCH)" in result.stderr
    document = json.loads(
        CliRunner().invoke(cli, ["worktree", "status", "--stale", "-w", str(repo), "--format", "json"]).stdout
    )
    assert document["checked"] is True and [item["branch"] for item in document["stale"]] == ["dev-old"]
    monkeypatch.setattr(stale_module, "run_gh", fake_gh(auth=1))
    skipped = CliRunner().invoke(cli, ["worktree", "status", "--stale", "-w", str(repo)])
    assert skipped.exit_code == 0 and skipped.stdout == "[SUMMARY: checked=no branches=0 stale=0 stale_after=14d]\n"
    assert "(WORKTREE_STALE_SKIPPED)" in skipped.stderr


def test_hygiene_runs_show_stale_branches_and_linter_runs_never_do(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    aged_branch(repo, "dev-old", 30)
    calls: list[Path] = []
    gh = fake_gh()
    monkeypatch.setattr(stale_module, "run_gh", lambda cwd, args, **_: (calls.append(cwd), gh(cwd, args))[1])
    hygiene = CliRunner().invoke(cli, ["rules", "check", "-p", "hygiene", "-w", str(repo)])
    assert hygiene.exit_code == 0, hygiene.output
    assert "(WORKTREE_STALE_BRANCH) activity branch dev-old" in hygiene.stderr
    strict = CliRunner().invoke(cli, ["rules", "check", "-p", "hygiene", "-w", str(repo), "--strict"])
    assert strict.exit_code == 1  # a warning, as every hygiene warning under --strict
    calls.clear()
    for args in (["rules", "check"], ["rules", "check", "-p", "hygiene", str(repo / "README.md")]):
        write(repo, "README.md", "# x\n")
        result = CliRunner().invoke(cli, [*args, "-w", str(repo)])
        assert "STALE" not in result.stderr
    assert calls == []


def test_a_recorded_unit_the_branch_no_longer_holds_is_not_reported(repo: Path) -> None:
    aged_branch(repo, "dev-gone", 30, unit="docs/specs/gone")
    git(repo, "config", "--local", "branch.dev-gone.devkitUnit", "docs/proposals/PROP-gone")  # handed off since
    [item] = stale_branches(locate(repo), gh=fake_gh()).stale
    assert item.unit is None  # the caller maps the slug instead of resuming a unit that is gone


def test_default_status_never_queries_github(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_gh(cwd: Path, args: list[str], **_: object) -> None:
        pytest.fail("default worktree status must not query GitHub")

    monkeypatch.setattr(stale_module, "run_gh", unexpected_gh)
    result = CliRunner().invoke(cli, ["worktree", "status", "-w", str(repo), "--format", "json"])
    assert result.exit_code == 0, result.output
    assert "worktrees" in json.loads(result.stdout)
    assert CliRunner().invoke(cli, ["worktree", "stale", "--help"]).exit_code == 2
