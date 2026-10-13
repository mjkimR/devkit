"""``devkit worktree start|finish|status`` and the ``[worktree]`` configuration."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import ActionMode
from devkit.cli import cli
from devkit.worktree import WorktreeConfig, WorktreeConfigError, read_worktree_config
from testsupport.rules import git, init_repo, write


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return init_repo(tmp_path / "repo").resolve()


def invoke(*args: str):
    return CliRunner().invoke(cli, ["worktree", *args])


def configure(root: Path, table: str) -> None:
    write(root, ".devkit/config.toml", f"schema = 1\n\n[worktree]\n{table}")


def test_start_prints_the_worktree_and_the_cd_hint(repo: Path) -> None:
    result = invoke("start", "demo", "-w", str(repo))
    path = repo.parent / "repo-wt-demo"
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        f"[WORKTREE_STARTED: demo path={path} branch=demo base={repo} created=yes setup=- synced=-]",
        f"[NEXT_CMD: cd {path}]",
    ]
    reused = json.loads(invoke("start", "demo", "-w", str(repo), "--format", "json").stdout)
    assert reused == {
        "slug": "demo",
        "path": str(path),
        "branch": "demo",
        "base": str(repo),
        "created": False,
        "setup": None,
        "synced": None,
        "notices": [],
    }


def test_start_runs_the_configured_setup_and_warns_when_it_fails(repo: Path) -> None:
    configure(repo, 'setup = "exit 4"\n')
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "config")
    result = invoke("start", "demo", "-w", str(repo))
    assert result.exit_code == 0 and 'created=yes setup="exit 4"' in result.stdout
    assert "[WARN]   (WORKTREE_SETUP_FAILED) setup 'exit 4' exited 4" in result.stderr
    assert invoke("start", "demo", "-w", str(repo), "--strict").exit_code == 0  # reused: no setup, no warning


def test_finish_reports_progress_before_a_refusal_and_resumes(repo: Path) -> None:
    configure(repo, "pull_request = false\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "config")
    assert invoke("start", "demo", "-w", str(repo)).exit_code == 0
    path = repo.parent / "repo-wt-demo"
    write(path, "work.txt", "x\n")
    git(path, "add", ".")
    git(path, "commit", "-q", "-m", "work")
    write(path, "wip.txt", "x\n")
    refused = invoke("finish", "demo", "--merge", "-w", str(repo))
    assert refused.exit_code == 2
    assert refused.stdout == (
        f"[WORKTREE_FINISHED: demo path={path} merged=yes push=no-upstream removed=no branch_deleted=no]\n"
    )
    assert "(WORKTREE_DIRTY)" in refused.stderr
    (path / "wip.txt").unlink()
    done = invoke("finish", "demo", "-w", str(repo), "--format", "json")
    assert done.exit_code == 0, done.output
    assert json.loads(done.stdout) == {
        "slug": "demo",
        "path": str(path),
        "branch": "demo",
        "merged": False,
        "push": None,
        "removed": True,
        "branch_deleted": True,
        "notices": [],
    }


def test_a_refused_finish_in_json_carries_the_partial_result_and_the_error(repo: Path) -> None:
    configure(repo, "pull_request = false\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "config")
    invoke("start", "demo", "-w", str(repo))
    path = repo.parent / "repo-wt-demo"
    write(path, "wip.txt", "x\n")
    refused = invoke("finish", "demo", "--merge", "-w", str(repo), "--format", "json")
    document = json.loads(refused.stdout)
    assert refused.exit_code == 2 and refused.stderr == ""
    assert document["merged"] is True and document["removed"] is False
    assert [error["code"] for error in document["errors"]] == ["WORKTREE_DIRTY"]


def test_a_git_failure_after_the_merge_reports_progress_and_the_push_warning_then_resumes(
    repo: Path, tmp_path: Path, refuse_deleting: Callable[[Path, str], Path]
) -> None:
    configure(repo, "pull_request = false\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "config")
    git(repo, "remote", "add", "origin", str(tmp_path / "gone.git"))  # unreachable: the push fails
    git(repo, "config", "branch.main.remote", "origin")
    git(repo, "config", "branch.main.merge", "refs/heads/main")
    invoke("start", "demo", "-w", str(repo))
    path = repo.parent / "repo-wt-demo"
    write(path, "work.txt", "x\n")
    git(path, "add", ".")
    git(path, "commit", "-q", "-m", "work")
    hook = refuse_deleting(repo, "demo")
    refused = invoke("finish", "demo", "--merge", "-w", str(repo))
    assert refused.exit_code == 2
    assert refused.stdout == (
        f"[WORKTREE_FINISHED: demo path={path} merged=yes push=failed removed=yes branch_deleted=no]\n"
    )
    assert "(WORKTREE_PUSH_FAILED)" in refused.stderr and "(WORKTREE_BRANCH_DELETE_FAILED)" in refused.stderr
    hook.unlink()
    done = invoke("finish", "demo", "-w", str(repo))
    assert done.exit_code == 0, done.output
    assert done.stdout == f"[WORKTREE_FINISHED: demo path={path} merged=no push=- removed=yes branch_deleted=yes]\n"


def test_merge_is_refused_under_the_default_pull_request_policy(repo: Path) -> None:
    invoke("start", "demo", "-w", str(repo))
    refused = invoke("finish", "demo", "--merge", "-w", str(repo), "--format", "json")
    assert refused.exit_code == 2 and json.loads(refused.stdout)["error"]["code"] == "WORKTREE_PR_POLICY"


def test_status_lists_worktrees_branches_and_a_summary(repo: Path) -> None:
    invoke("start", "demo", "-w", str(repo))
    git(repo, "branch", "-q", "side")
    git(repo, "checkout", "-q", "side")
    write(repo, "side.txt", "x\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "side")
    git(repo, "checkout", "-q", "main")
    result = invoke("status", "-w", str(repo))
    head = git(repo, "rev-parse", "--short=7", "HEAD")
    side = git(repo, "rev-parse", "--short=7", "side")
    path = repo.parent / "repo-wt-demo"
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        f"[WORKTREE: {repo} branch=main head={head} role=base merged=- dirty=no prunable=no]",
        f"[WORKTREE: {path} branch=demo head={head} role=linked merged=yes dirty=no prunable=no]",
        f"[BRANCH: side head={side} merged=no]",
        f"[SUMMARY: base={repo} base_branch=main worktrees=1 unmerged=0 dirty=0 branches=1]",
    ]
    document = json.loads(invoke("status", "-w", str(path), "--format", "json").stdout)
    assert [item["role"] for item in document["worktrees"]] == ["base", "linked"]


def test_outside_a_repository_every_command_fails_cleanly(tmp_path: Path) -> None:
    for args in (["start", "demo"], ["finish", "demo"], ["status"]):
        result = invoke(*args, "-w", str(tmp_path), "--format", "json")
        assert result.exit_code == 2 and json.loads(result.stdout)["error"]["code"] == "GIT_FAILED"


def test_worktree_config_defaults_and_validation(repo: Path) -> None:
    assert read_worktree_config(repo) == WorktreeConfig(pull_request=True, delete_branch=True, setup=None)
    configure(repo, 'pull_request = false\ndelete_branch = false\nsetup = "uv sync"\n')
    assert read_worktree_config(repo) == WorktreeConfig(False, False, "uv sync")
    for table, message in [
        ("bogus = 1\n", "unknown fields"),
        ('pull_request = "no"\n', "pull_request must be true or false"),
        ('setup = " "\n', "setup must be a non-empty shell command"),
        ("setup = 3\n", "setup must be a non-empty shell command"),
    ]:
        configure(repo, table)
        with pytest.raises(WorktreeConfigError, match=message) as raised:
            read_worktree_config(repo)
        assert raised.value.code == "WORKTREE_CONFIG_INVALID" and raised.value.mode is ActionMode.INPUT_ERROR
    write(repo, ".devkit/config.toml", "schema = 1\nworktree = 1\n")
    with pytest.raises(WorktreeConfigError, match="expected a table"):
        read_worktree_config(repo)
