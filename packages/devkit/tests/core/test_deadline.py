from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest
from devkit.advisory import ActionMode, AdvisoryError, Retry
from devkit.core import Deadline, DeadlineExceededError, GitError, run_git


class _CallerTimeout(AdvisoryError):
    code = "CALLER_TIMEOUT"
    retry = Retry.SAFE


def _caller_error(what: str, seconds: float) -> _CallerTimeout:
    return _CallerTimeout(f"{what} exceeded the caller's timeout of {seconds:g}s")


def test_remaining_counts_down_and_check_passes_before_expiry() -> None:
    deadline = Deadline(5)
    first = deadline.remaining()
    assert 0 < first <= 5 and deadline.seconds == 5
    assert deadline.remaining() <= first
    assert not deadline.expired()
    deadline.check("anything")


def test_an_expired_deadline_raises_deadline_exceeded() -> None:
    deadline = Deadline(0)
    assert deadline.expired() and deadline.remaining() <= 0
    with pytest.raises(DeadlineExceededError) as raised:
        deadline.check("the registry operation")
    error = raised.value
    assert (error.code, error.mode, error.what, error.seconds) == (
        "DEADLINE_EXCEEDED",
        ActionMode.DEFER,
        "the registry operation",
        0,
    )
    assert str(error) == "the registry operation exceeded the deadline of 0s"


def test_an_error_factory_chooses_the_raised_error() -> None:
    deadline = Deadline(0.0, error=_caller_error)
    assert isinstance(deadline.exceeded("x"), _CallerTimeout)
    with pytest.raises(_CallerTimeout, match="waiting exceeded the caller's timeout of 0s") as raised:
        deadline.check("waiting")
    assert raised.value.code == "CALLER_TIMEOUT"


def test_run_git_takes_the_time_left(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[float] = []
    real = subprocess.run

    def spy(command: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        seen.append(kwargs["timeout"])  # type: ignore[arg-type]
        return real(command, **kwargs)  # type: ignore[call-overload]

    monkeypatch.setattr(subprocess, "run", spy)
    assert run_git(repo, "rev-parse", "--is-inside-work-tree", timeout=None, deadline=Deadline(30)) == b"true\n"
    assert 0 < seen[0] <= 30


def test_run_git_with_an_expired_deadline_starts_no_git(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def never(*args: object, **kwargs: object) -> None:
        raise AssertionError("git started")

    monkeypatch.setattr(subprocess, "run", never)
    with pytest.raises(DeadlineExceededError) as raised:
        run_git(repo, "status", deadline=Deadline(0))
    assert raised.value.what == "git status"


def test_run_git_raises_the_deadline_error_when_git_outlives_it(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def slow(command: tuple[str, ...], **kwargs: object) -> None:
        raise subprocess.TimeoutExpired(command, 1.0)

    monkeypatch.setattr(subprocess, "run", slow)
    with pytest.raises(DeadlineExceededError) as default:
        run_git(repo, "fetch", deadline=Deadline(1))
    assert default.value.what == "git fetch" and isinstance(default.value.__cause__, subprocess.TimeoutExpired)
    with pytest.raises(_CallerTimeout, match="git fetch exceeded"):
        run_git(repo, "fetch", deadline=Deadline(1, error=_caller_error))


def test_run_git_kills_a_git_that_outlives_the_deadline(repo: Path) -> None:
    start = time.monotonic()
    with pytest.raises(DeadlineExceededError):
        run_git(repo, "hash-object", "--stdin", input=b"x" * 50_000_000, deadline=Deadline(0.05))
    assert time.monotonic() - start < 5


def test_other_git_failures_stay_git_errors_under_a_deadline(repo: Path) -> None:
    with pytest.raises(GitError) as raised:
        run_git(repo, "rev-parse", "--verify", "no-such-ref", deadline=Deadline(30))
    assert raised.value.returncode == 128
