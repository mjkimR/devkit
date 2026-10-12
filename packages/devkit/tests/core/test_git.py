from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from devkit.core import GitError, run_git
from devkit.core.errors import DevkitCoreError


def test_returns_stdout_bytes(repo: Path) -> None:
    assert run_git(repo, "rev-parse", "--is-inside-work-tree") == b"true\n"


def test_input_is_passed_to_stdin(repo: Path) -> None:
    sha = run_git(repo, "hash-object", "--stdin", input=b"hello\n").strip()
    assert sha == b"ce013625030ba8dba906f756967f9e9ca394464a"


def test_paths_are_raw_bytes(repo: Path) -> None:
    (repo / "한글.md").write_text("x")
    run_git(repo, "add", "--", "한글.md")
    listed = run_git(repo, "ls-files", "-z").split(b"\0")
    assert "한글.md".encode() in listed


def test_nonzero_exit_carries_status_and_stderr(repo: Path) -> None:
    with pytest.raises(GitError) as info:
        run_git(repo, "rev-parse", "--verify", "no-such-ref")
    error = info.value
    assert isinstance(error, DevkitCoreError)
    assert error.returncode == 128
    assert "git rev-parse failed" in str(error)
    assert error.command[:3] == ("git", "-C", str(repo))
    assert error.stderr


def test_nonzero_exit_without_stderr_reports_the_status(repo: Path) -> None:
    run_git(repo, "commit", "-q", "--allow-empty", "-m", "one")
    first = run_git(repo, "rev-parse", "HEAD").decode().strip()
    run_git(repo, "commit", "-q", "--allow-empty", "-m", "two")
    with pytest.raises(GitError, match="exit status 1") as info:
        run_git(repo, "merge-base", "--is-ancestor", "HEAD", first)
    assert info.value.returncode == 1 and info.value.stderr == ""


def test_not_a_repository(tmp_path: Path) -> None:
    with pytest.raises(GitError) as info:
        run_git(tmp_path, "rev-parse", "--show-toplevel")
    assert info.value.returncode is not None and info.value.returncode != 0


def test_git_unavailable(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def missing(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", missing)
    with pytest.raises(GitError, match="git is not available") as info:
        run_git(repo, "status")
    assert info.value.returncode is None


def test_timeout(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def slow(command: list[str], **kwargs: object) -> object:
        assert kwargs["timeout"] == 0.5
        raise subprocess.TimeoutExpired(command, 0.5, stderr=b"still working")

    monkeypatch.setattr(subprocess, "run", slow)
    with pytest.raises(GitError, match=r"timed out after 0\.5s") as info:
        run_git(repo, "fetch", timeout=0.5)
    assert info.value.returncode is None and info.value.stderr == "still working"


def test_real_timeout_kills_a_waiting_git(repo: Path) -> None:
    # ``hash-object --stdin`` with no input closed would block; the runner always closes stdin,
    # so exercise a real expiry with a tiny timeout on a command that reads a large input.
    with pytest.raises(GitError, match="timed out"):
        run_git(repo, "hash-object", "--stdin", input=b"x" * 50_000_000, timeout=0.0001)


def test_no_arguments(repo: Path) -> None:
    with pytest.raises(GitError, match="git failed"):
        run_git(repo)
