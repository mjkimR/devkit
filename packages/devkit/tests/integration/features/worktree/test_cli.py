"""``devkit worktree start|finish|status`` and the ``[worktree]`` configuration."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import ActionMode
from devkit_agt.features.worktree import WorktreeConfig, WorktreeConfigError, read_worktree_config
from testsupport.cli import cli
from testsupport.rules import git, init_repo, write


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return init_repo(tmp_path / "repo").resolve()


def invoke(*args: str):
    return CliRunner().invoke(cli, ["worktree", *args])


def configure(root: Path, table: str) -> None:
    write(root, ".devkit/config.toml", f"schema = 1\n\n[worktree]\n{table}")


def work(repo: Path) -> Path:
    """Start ``dev-demo`` and commit one change in its worktree; return the worktree."""
    assert invoke("start", "dev-demo", "-w", str(repo)).exit_code == 0
    path = repo.parent / "repo-wt-dev-demo"
    write(path, "work.txt", "x\n")
    git(path, "add", ".")
    git(path, "commit", "-q", "-m", "work")
    return path


def land(repo: Path, branch: str = "dev-demo") -> None:
    """Land ``branch`` on the base as local integration does (a merge commit), so ``finish`` only cleans up."""
    git(repo, "merge", "-q", "--no-ff", "-m", f"chore(merge): integrate {branch} into main", branch)


def test_start_prints_the_worktree_and_the_cd_hint(repo: Path) -> None:
    result = invoke("start", "dev-demo", "-w", str(repo))
    path = repo.parent / "repo-wt-dev-demo"
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        f"[WORKTREE_STARTED: dev-demo path={path} base={repo} created=yes existing=no unit=- setup=- synced=-]",
        f"[NEXT_CMD: cd {path}]",
    ]
    again = json.loads(invoke("start", "dev-demo", "-w", str(repo), "--format", "json").stdout)
    assert again["error"]["code"] == "WORKTREE_BRANCH_EXISTS"  # an existing branch is continued only by attaching it
    assert "--existing-branch dev-demo --unit" in again["error"]["advisory"]["what_to_report"]
    assert "fix" not in again["error"]["advisory"]  # its unit is not recorded: no runnable command to offer


def test_start_runs_the_configured_setup_and_warns_when_it_fails(repo: Path) -> None:
    configure(repo, 'setup = "exit 4"\n')
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "config")
    result = invoke("start", "dev-demo", "-w", str(repo))
    assert result.exit_code == 0 and 'created=yes existing=no unit=- setup="exit 4"' in result.stdout
    assert "[WARN]   (WORKTREE_SETUP_FAILED) setup 'exit 4' exited 4" in result.stderr
    assert invoke("start", "dev-demo", "-w", str(repo), "--strict").exit_code == 2  # existing: refused, no setup


def test_a_dirty_worktree_refuses_finish_before_any_change(repo: Path) -> None:
    configure(repo, 'pull_request = "auto"\n')
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "config")
    path = work(repo)
    land(repo)
    write(path, "wip.txt", "x\n")
    refused = invoke("finish", "dev-demo", "-w", str(repo))
    assert refused.exit_code == 2 and refused.stdout == ""  # no result sentinel for a refused run
    assert "(WORKTREE_DIRTY)" in refused.stderr and f"[TARGET] {path}\n" in refused.stderr
    assert "--force" not in refused.stderr  # git's own hint is not relayed
    assert path.is_dir() and "refs/heads/dev-demo" in git(repo, "show-ref")  # nothing was removed
    (path / "wip.txt").unlink()
    done = invoke("finish", "dev-demo", "-w", str(repo), "--format", "json")
    assert done.exit_code == 0, done.output
    assert json.loads(done.stdout) == {
        "branch": "dev-demo",
        "slug": "demo",
        "path": str(path),
        "merged": False,
        "removed": True,
        "branch_deleted": True,
        "discarded": False,
        "notices": [],
    }


def test_a_refused_finish_in_json_carries_the_partial_result_and_the_error(repo: Path) -> None:
    configure(repo, 'pull_request = "auto"\n')
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "config")
    invoke("start", "dev-demo", "-w", str(repo))
    path = repo.parent / "repo-wt-dev-demo"
    write(path, "wip.txt", "x\n")
    refused = invoke("finish", "dev-demo", "-w", str(repo), "--format", "json")
    document = json.loads(refused.stdout)
    assert refused.exit_code == 2 and refused.stderr == ""
    assert document["error"]["code"] == "WORKTREE_DIRTY"
    assert document["error"]["advisory"]["target_files"] == [str(path)]


def test_a_git_failure_during_cleanup_reports_progress_then_resumes(
    repo: Path, refuse_deleting: Callable[[Path, str], Path]
) -> None:
    path = work(repo)
    land(repo)
    hook = refuse_deleting(repo, "dev-demo")
    refused = invoke("finish", "dev-demo", "-w", str(repo))
    assert refused.exit_code == 2
    assert refused.stdout == (
        f"[WORKTREE_FINISH_PARTIAL: dev-demo path={path} merged=no removed=yes branch_deleted=no discarded=no]\n"
    )
    assert "(WORKTREE_BRANCH_DELETE_FAILED)" in refused.stderr
    hook.unlink()
    done = invoke("finish", "dev-demo", "-w", str(repo))
    assert done.exit_code == 0, done.output
    assert (
        done.stdout
        == f"[WORKTREE_FINISHED: dev-demo path={path} merged=no removed=yes branch_deleted=yes discarded=no]\n"
    )


def test_finish_of_a_landed_branch_makes_no_network_call(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-03: cleanup after a landing (local integration or a merged pull request) stays local."""
    import devkit_agt.features.worktree.usecases.lifecycle as lifecycle

    git(repo, "remote", "add", "origin", str(tmp_path / "gone.git"))
    git(repo, "config", "branch.main.remote", "origin")
    git(repo, "config", "branch.main.merge", "refs/heads/main")
    path = work(repo)
    land(repo)
    called: list[str] = []
    for name in ("run_git", "run_git_text"):
        original = getattr(lifecycle, name)

        def record(root: Path, *args: str, _original: Callable[..., object] = original, **kw: object) -> object:
            called.append(args[0])
            return _original(root, *args, **kw)

        monkeypatch.setattr(lifecycle, name, record)
    done = invoke("finish", "dev-demo", "-w", str(repo))
    assert done.exit_code == 0, done.output
    assert (
        done.stdout
        == f"[WORKTREE_FINISHED: dev-demo path={path} merged=no removed=yes branch_deleted=yes discarded=no]\n"
    )
    assert called and not set(called) & {"fetch", "push", "ls-remote"}


def test_finish_local_only_is_an_unknown_option(repo: Path) -> None:
    """SPEC-remove-unused-cli-options AC-01: the retired no-op flag is a usage error and nothing is removed."""
    path = work(repo)
    land(repo)
    refused = invoke("finish", "dev-demo", "--local-only", "-w", str(repo))
    assert refused.exit_code == 2 and "No such option '--local-only'" in refused.stderr
    assert path.is_dir() and git(repo, "branch", "--list", "dev-demo")


def test_an_unmerged_branch_is_refused_with_the_integration_route(repo: Path) -> None:
    path = work(repo)
    refused = json.loads(invoke("finish", "dev-demo", "-w", str(repo), "--format", "json").stdout)["error"]
    assert refused["code"] == "WORKTREE_UNMERGED"
    fix = refused["advisory"]["fix"]
    assert "uv run devkit integration prepare dev-demo --route local" in fix and "--merge" not in fix
    assert path.is_dir()


@pytest.mark.parametrize("extra", [(), ("--discard",)], ids=["merge", "merge-discard"])
def test_finish_merge_is_retired_and_changes_nothing(
    repo: Path, monkeypatch: pytest.MonkeyPatch, extra: tuple[str, ...]
) -> None:
    """AC-01: ``--merge`` refuses with ``WORKTREE_MERGE_RETIRED`` naming the integration commands; nothing changes."""
    from devkit_core.core import extensions as core_extensions

    listed: list[str] = []
    monkeypatch.setattr(core_extensions.metadata, "entry_points", lambda group: listed.append(group) or [])
    path = work(repo)
    before = (git(repo, "rev-parse", "HEAD"), git(repo, "show-ref"), git(repo, "config", "--get-regexp", "devkit"))
    refused = invoke("finish", "dev-demo", "--merge", *extra, "-w", str(repo))
    assert refused.exit_code == 2 and refused.stdout == ""
    assert "[ERROR]  (WORKTREE_MERGE_RETIRED)" in refused.stderr
    fix = next(line for line in refused.stderr.splitlines() if line.startswith("[FIX]"))
    assert "uv run devkit integration prepare dev-demo --route local" in fix
    assert "uv run devkit integration integrate dev-demo --route local --expected-digest <digest>" in fix
    after = (git(repo, "rev-parse", "HEAD"), git(repo, "show-ref"), git(repo, "config", "--get-regexp", "devkit"))
    assert after == before and path.is_dir() and listed == []  # no post-finish extension was even listed
    advisory = json.loads(invoke("finish", "dev-demo", "--merge", "-w", str(repo), "--format", "json").stdout)["error"]
    assert (advisory["code"], advisory["advisory"]["mode"], advisory["advisory"]["level"]) == (
        "WORKTREE_MERGE_RETIRED",
        "INPUT_ERROR",
        "ERROR",
    )
    assert "--merge" not in invoke("finish", "--help").stdout


def test_status_lists_worktrees_branches_and_a_summary(repo: Path) -> None:
    invoke("start", "dev-demo", "-w", str(repo))
    git(repo, "branch", "-q", "side")
    git(repo, "checkout", "-q", "side")
    write(repo, "side.txt", "x\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "side")
    git(repo, "checkout", "-q", "main")
    result = invoke("status", "-w", str(repo))
    head = git(repo, "rev-parse", "--short=7", "HEAD")
    side = git(repo, "rev-parse", "--short=7", "side")
    path = repo.parent / "repo-wt-dev-demo"
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        f"[WORKTREE: {repo} branch=main head={head} role=base merged=- dirty=no prunable=no]",
        f"[WORKTREE: {path} branch=dev-demo head={head} role=linked merged=yes dirty=no prunable=no]",
        f"[BRANCH: side head={side} merged=no]",
        f"[SUMMARY: base={repo} base_branch=main worktrees=1 unmerged=0 dirty=0 branches=1]",
    ]
    document = json.loads(invoke("status", "-w", str(path), "--format", "json").stdout)
    assert [item["role"] for item in document["worktrees"]] == ["base", "linked"]


def test_outside_a_repository_every_command_fails_cleanly(tmp_path: Path) -> None:
    for args in (["start", "dev-demo"], ["finish", "dev-demo"], ["status"]):
        result = invoke(*args, "-w", str(tmp_path), "--format", "json")
        assert result.exit_code == 2 and json.loads(result.stdout)["error"]["code"] == "GIT_FAILED"


def test_worktree_config_defaults_and_validation(repo: Path) -> None:
    assert read_worktree_config(repo) == WorktreeConfig(
        pull_request="auto", delete_branch=True, setup=None, stale_after="14d"
    )
    configure(repo, 'pull_request = "required"\ndelete_branch = false\nsetup = "uv sync"\nstale_after = "2w"\n')
    config = read_worktree_config(repo)
    assert config == WorktreeConfig("required", False, "uv sync", "2w")
    for table, message in [
        ("bogus = 1\n", "unknown fields"),
        ('pull_request = "no"\n', 'pull_request must be "auto" or "required"'),
        ("pull_request = true\n", 'pull_request must be "auto" or "required"'),
        ('delete_branch = "no"\n', "delete_branch must be true or false"),
        ('setup = " "\n', "setup must be a non-empty shell command"),
        ("setup = 3\n", "setup must be a non-empty shell command"),
        ('stale_after = "14"\n', "stale_after must be"),
        ('stale_after = "0d"\n', "stale_after must be"),
        ('stale_after = "3m"\n', "stale_after must be"),
        ("stale_after = 14\n", "stale_after must be"),
    ]:
        configure(repo, table)
        with pytest.raises(WorktreeConfigError, match=message) as raised:
            read_worktree_config(repo)
        assert raised.value.code == "WORKTREE_CONFIG_INVALID" and raised.value.mode is ActionMode.INPUT_ERROR
    write(repo, ".devkit/config.toml", "schema = 1\nworktree = 1\n")
    with pytest.raises(WorktreeConfigError, match="expected a table"):
        read_worktree_config(repo)


def test_post_finish_extensions_run_after_a_successful_finish_only(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace

    import devkit_agt.features.worktree.services.extensions as extensions
    from devkit_core.core import extensions as core_extensions

    seen: list[tuple[Path, dict]] = []

    def cleanup(base: Path, result: dict) -> list[str]:
        seen.append((base, result))
        return [f"cleaned {result['slug']}"]

    def broken(base: Path, result: dict) -> None:
        raise RuntimeError("boom")

    entries = [
        SimpleNamespace(name="b-broken", value="fake:b", load=lambda: broken),
        SimpleNamespace(name="a-cleanup", value="fake:a", load=lambda: cleanup),
    ]
    monkeypatch.setattr(
        core_extensions.metadata, "entry_points", lambda group: entries if group == extensions.GROUP else []
    )
    assert invoke("start", "dev-demo", "-w", str(repo)).exit_code == 0
    path = repo.parent / "repo-wt-dev-demo"
    write(path, "work.txt", "x\n")
    git(path, "add", ".")
    git(path, "commit", "-q", "-m", "work")
    land(repo)
    write(path, "wip.txt", "x\n")
    refused = invoke("finish", "dev-demo", "-w", str(repo))
    assert refused.exit_code == 2 and seen == []  # a refusal runs no extension

    (path / "wip.txt").unlink()
    done = invoke("finish", "dev-demo", "-w", str(repo))
    assert done.exit_code == 0, done.output
    assert [(base, result["slug"], result["branch"], result["removed"]) for base, result in seen] == [
        (repo, "demo", "dev-demo", True)
    ]
    assert "(POST_FINISH_NOTICE) cleaned demo" in done.stderr
    assert "(POST_FINISH_EXTENSION_FAILED) post-finish extension b-broken failed: boom" in done.stderr
    assert invoke("finish", "dev-demo", "-w", str(repo), "--format", "json").exit_code == 2  # nothing left to finish


def test_a_mistyped_branch_is_an_input_error_listing_the_branches(repo: Path) -> None:
    result = invoke("finish", "dev-nope", "-w", str(repo), "--format", "json")
    advisory = json.loads(result.stdout)["error"]["advisory"]
    assert (advisory["code"], advisory["mode"]) == ("WORKTREE_NOT_FOUND", "INPUT_ERROR")
    assert advisory["fix"] == f"uv run devkit worktree status -w {repo}" and advisory["target_files"] == ["BRANCH"]


def test_an_attached_branch_exists_error_names_its_recorded_unit(repo: Path) -> None:
    git(repo, "branch", "dev-demo")
    git(repo, "config", "branch.dev-demo.devkitUnit", "units/a")  # what an earlier --existing-branch attach records
    again = json.loads(invoke("start", "dev-demo", "-w", str(repo), "--format", "json").stdout)
    assert again["error"]["advisory"]["fix"] == (
        "uv run devkit worktree start dev-demo --existing-branch dev-demo --unit units/a"
    )


def test_commands_run_inside_a_linked_worktree_fix_with_the_same_command_on_the_base(repo: Path) -> None:
    assert invoke("start", "dev-demo", "-w", str(repo)).exit_code == 0
    path = repo.parent / "repo-wt-dev-demo"
    nested = json.loads(invoke("start", "dev-other", "-w", str(path), "--format", "json").stdout)["error"]
    assert nested["code"] == "WORKTREE_NESTED"
    assert nested["advisory"]["fix"] == f"uv run devkit worktree start dev-other --format json -w {repo}"
    assert any(f"keep working in {path}" in line for line in nested["advisory"]["details"])
    refused = invoke("finish", "dev-demo", "-w", str(path))
    assert refused.exit_code == 2 and "(WORKTREE_RUN_FROM_BASE)" in refused.stderr
    assert f"[FIX]    uv run devkit worktree finish dev-demo -w {repo}\n" in refused.stderr
