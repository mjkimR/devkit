"""``devkit_core.core.git``: the isolated environment and session options, path lists, tracked and ignored probes and
configuration reads."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pytest
from devkit_core.core import GitError, changed_paths, dirty_paths, git_config, run_git, run_git_text
from devkit_core.core.git import ignored_paths, run_git_result, tracked_paths


def git(repo: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, env=env).stdout


def _commit(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return git(repo, "rev-parse", "HEAD").strip()


def test_isolated_env_drops_inherited_git_variables(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    other = tmp_path / "other"
    other.mkdir()
    git(other, "init", "-q", "-b", "other")
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    assert run_git_text(repo, "rev-parse", "--absolute-git-dir") == str((other / ".git").resolve())
    assert run_git_text(repo, "rev-parse", "--absolute-git-dir", isolated_env=True) == str(repo / ".git")


def test_isolated_env_keeps_the_index_option(repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (repo / "a.txt").write_text("a")
    index = str(tmp_path / "index")
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "ignored"))
    run_git(repo, "add", "a.txt", index=index, isolated_env=True)
    assert run_git_text(repo, "ls-files", index=index, isolated_env=True) == "a.txt"
    assert run_git_text(repo, "ls-files", isolated_env=True) == ""


def test_new_session_runs_git_and_raises_as_run_git(repo: Path) -> None:
    assert run_git(repo, "rev-parse", "--is-inside-work-tree", new_session=True) == b"true\n"
    assert run_git(repo, "hash-object", "--stdin", input=b"hello\n", new_session=True).strip() == (
        b"ce013625030ba8dba906f756967f9e9ca394464a"
    )
    with pytest.raises(GitError) as raised:
        run_git(repo, "rev-parse", "--verify", "no-such-ref", new_session=True)
    assert raised.value.returncode == 128
    assert run_git_result(repo, "diff", "--quiet", ok_returncodes=(0, 1), new_session=True).returncode == 0


def test_new_session_timeout_kills_the_process_group(repo: Path, tmp_path: Path) -> None:
    marker = tmp_path / "child.pid"
    git(repo, "config", "alias.sleepy", f"!sh -c 'sleep 30 & echo $! > {marker}; wait'")
    with pytest.raises(GitError) as raised:
        run_git(repo, "sleepy", timeout=1, new_session=True)
    assert isinstance(raised.value.__cause__, subprocess.TimeoutExpired)
    pid = int(marker.read_text())
    for _ in range(100):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.02)
    else:
        pytest.fail("the grandchild outlived the timed-out Git")


def test_dirty_paths_lists_both_sides_of_a_rename_sorted(repo: Path) -> None:
    (repo / "old.txt").write_text("content\n" * 20)
    (repo / "z.txt").write_text("z")
    _commit(repo, "base")
    git(repo, "mv", "old.txt", "new.txt")
    (repo / "z.txt").write_text("changed")
    (repo / "dir").mkdir()
    (repo / "dir" / "u.txt").write_text("u")
    assert dirty_paths(repo) == ["dir/u.txt", "new.txt", "old.txt", "z.txt"]
    assert dirty_paths(repo, untracked="normal", optional_locks=True) == ["dir/", "new.txt", "old.txt", "z.txt"]
    assert dirty_paths(repo, untracked="no") == ["new.txt", "old.txt", "z.txt"]


def test_dirty_paths_of_a_clean_tree(repo: Path) -> None:
    assert dirty_paths(repo) == []


def test_changed_paths_lists_both_names_of_a_rename(repo: Path) -> None:
    (repo / "old.txt").write_text("content\n" * 20)
    (repo / "keep.txt").write_text("k")
    base = _commit(repo, "base")
    git(repo, "mv", "old.txt", "new.txt")
    (repo / "한글.md").write_text("x")
    head = _commit(repo, "head")
    assert changed_paths(repo, base, head) == ["new.txt", "old.txt", "한글.md"]
    assert changed_paths(repo, head, head) == []
    with pytest.raises(GitError):
        changed_paths(repo, base, "no-such-ref")


def test_git_config(repo: Path, tmp_path: Path) -> None:
    git(repo, "config", "devkit.test", "value with space")
    git(repo, "config", "devkit.flag", "yes")
    git(repo, "config", "devkit.empty", "")
    assert git_config(repo, "devkit.test") == "value with space"
    assert git_config(repo, "devkit.test", local=True) == "value with space"
    assert git_config(repo, "devkit.flag", type="bool") == "true"
    assert git_config(repo, "devkit.empty") == ""
    assert git_config(repo, "devkit.unset") is None
    assert git_config(repo, "devkit.unset", local=True) is None
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(GitError) as raised:  # --local outside a repository: exit 128, not "unset"
        git_config(outside, "devkit.test", local=True)
    assert raised.value.returncode == 128


@pytest.fixture
def probed(repo: Path) -> Path:
    (repo / "dir/sub").mkdir(parents=True)
    (repo / "dir/sub/file.txt").write_text("x")
    (repo / "tracked.txt").write_text("x")
    (repo / "kept.log").write_text("x")
    (repo / "a*b").write_text("x")
    (repo / "axb").write_text("x")
    (repo / ":x").write_text("x")  # without literal pathspecs, ":x" is the magic form of "x"
    _commit(repo, "tracked files")
    (repo / ".gitignore").write_text("*.log\n/build/\n")
    (repo / "fresh.log").write_text("x")
    (repo / "build").mkdir()
    return repo


def test_tracked_paths_are_literal_and_cover_directories(probed: Path) -> None:
    asked = ["tracked.txt", "dir", "dir/sub/", "a*b", ":x", "fresh.log", "missing"]
    assert tracked_paths(probed, asked) == {"tracked.txt", "dir", "dir/sub/", "a*b", ":x"}
    assert tracked_paths(probed, ["a?b", "x"]) == set()  # neither a glob nor a stripped magic prefix matches


def test_ignored_paths_follow_the_index_unless_asked_not_to(probed: Path) -> None:
    asked = ["kept.log", "fresh.log", "build/", "tracked.txt"]
    assert ignored_paths(probed, asked) == {"fresh.log", "build/"}
    assert ignored_paths(probed, asked, no_index=True) == {"kept.log", "fresh.log", "build/"}
    assert ignored_paths(probed, ["tracked.txt", "a*b"]) == set()  # Git exit 1: none ignored


def test_probes_without_paths_run_no_git(tmp_path: Path) -> None:
    missing = tmp_path / "missing"  # git -C on a missing directory would fail
    assert tracked_paths(missing, []) == set()
    assert ignored_paths(missing, [], no_index=True) == set()


def test_probes_outside_a_repository_raise(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    for probe in (tracked_paths, ignored_paths):
        with pytest.raises(GitError) as raised:
            probe(tmp_path, ["x"])
        assert raised.value.returncode == 128
