from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from devkit_core.base.errors import DevkitCoreError
from devkit_core.core import GitError, is_ancestor, run_git, run_git_text
from devkit_core.core.git import GitResult, repository_facts, run_git_result


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


def test_git_runs_unprompted_in_the_c_locale(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []
    real_run = subprocess.run

    def spy(command: list[str], **kwargs: object) -> object:
        calls.append(kwargs)
        return real_run(command, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setenv("GIT_INDEX_FILE", str(repo / ".git/index"))
    monkeypatch.setenv("LC_ALL", "ko_KR.UTF-8")
    monkeypatch.setattr(subprocess, "run", spy)
    run_git(repo, "status")
    run_git(repo, "hash-object", "--stdin", input=b"x")
    env = calls[0]["env"]
    assert isinstance(env, dict)
    assert (env["LC_ALL"], env["GIT_TERMINAL_PROMPT"], env["GIT_INDEX_FILE"]) == ("C", "0", str(repo / ".git/index"))
    assert calls[0]["stdin"] is subprocess.DEVNULL and calls[1]["stdin"] is None


def test_without_input_git_reads_nothing(repo: Path) -> None:
    empty_blob = b"e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    assert run_git(repo, "hash-object", "--stdin").strip() == empty_blob


def test_git_messages_are_not_localized(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANG", "ko_KR.UTF-8")
    monkeypatch.setenv("LC_ALL", "ko_KR.UTF-8")
    with pytest.raises(GitError) as info:
        run_git(tmp_path, "rev-parse", "--show-toplevel")
    assert "not a git repository" in info.value.stderr


def test_run_git_text_decodes_with_surrogateescape_and_drops_one_newline(repo: Path) -> None:
    blob = run_git_text(repo, "hash-object", "-w", "--stdin", input=b" caf\xe9 \n")  # not UTF-8, padded
    assert blob == run_git(repo, "hash-object", "--stdin", input=b" caf\xe9 \n").decode().strip()
    assert run_git_text(repo, "cat-file", "blob", blob) == b" caf\xe9 ".decode("utf-8", errors="surrogateescape")
    run_git(repo, "commit", "-q", "--allow-empty", "-m", "one")
    assert run_git_text(repo, "log", "-1", "--format=%s%n") == "one\n"  # only one trailing newline is removed


def test_is_ancestor_answers_and_raises_when_git_cannot(repo: Path, tmp_path: Path) -> None:
    run_git(repo, "commit", "-q", "--allow-empty", "-m", "one")
    first = run_git_text(repo, "rev-parse", "HEAD")
    run_git(repo, "commit", "-q", "--allow-empty", "-m", "two")
    second = run_git_text(repo, "rev-parse", "HEAD")
    assert is_ancestor(repo, first, second) is True
    assert is_ancestor(repo, first, first) is True
    assert is_ancestor(repo, second, first) is False
    with pytest.raises(GitError) as info:
        is_ancestor(repo, "0" * 40, first)
    assert info.value.returncode not in (None, 1)
    with pytest.raises(GitError):
        is_ancestor(tmp_path, first, second)


# AC-01 (SPEC-generated-conflicts-follow-ups)
def test_an_accepted_nonzero_exit_returns_its_status_and_output(repo: Path) -> None:
    (repo / "a.txt").write_text("one\n")
    (repo / "b.txt").write_text("two\n")
    result = run_git_result(repo, "diff", "--no-index", "--", "a.txt", "b.txt", ok_returncodes=(0, 1))
    assert isinstance(result, GitResult)
    assert result.returncode == 1
    assert b"-one\n+two\n" in result.stdout
    assert run_git_result(repo, "diff", "--no-index", "--", "a.txt", "a.txt", ok_returncodes=(0, 1)) == (0, b"")


# AC-02 (SPEC-generated-conflicts-follow-ups)
def test_an_exit_outside_the_accepted_statuses_raises_as_run_git_does(repo: Path) -> None:
    with pytest.raises(GitError) as info:
        run_git_result(repo, "rev-parse", "--verify", "no-such-ref", ok_returncodes=(0, 1))
    assert info.value.returncode == 128
    assert "git rev-parse failed" in str(info.value)
    assert info.value.stderr
    (repo / "a.txt").write_text("one\n")
    (repo / "b.txt").write_text("two\n")
    with pytest.raises(GitError, match="exit status 1") as default:
        run_git_result(repo, "diff", "--no-index", "--quiet", "--", "a.txt", "b.txt")
    assert default.value.returncode == 1


def _count_git(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, ...]]:
    calls: list[tuple[str, ...]] = []
    real_run = subprocess.run

    def spy(command: list[str], **kwargs: object) -> object:
        calls.append(tuple(command[3:]))
        return real_run(command, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(subprocess, "run", spy)
    return calls


def test_repository_facts_are_asked_once_per_scope_and_directory(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _count_git(monkeypatch)
    toplevel = ("rev-parse", "--show-toplevel")
    with repository_facts():
        first = run_git(repo, *toplevel)
        with repository_facts():  # a nested scope shares the outer memo
            assert run_git(repo, *toplevel) == first
        (repo / "sub").mkdir()
        assert run_git(repo / "sub", *toplevel) == first  # another directory is asked
        run_git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
        run_git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
        run_git(repo, "status")
        run_git(repo, "status")  # only repository-location queries are memoized
        with pytest.raises(GitError):
            run_git(tmp_path, *toplevel)
        run_git(tmp_path, "init", "-q")
        assert run_git(tmp_path, *toplevel).strip() == str(tmp_path.resolve()).encode()  # a failure is not kept
    run_git(repo, *toplevel)  # outside the scope Git is asked again
    assert calls.count(toplevel) == 5
    assert len(calls) == 9
