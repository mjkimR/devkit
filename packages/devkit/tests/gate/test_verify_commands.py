"""The built-in ``verify-commands`` pre-commit gate."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from devkit.gate import GateRefusedError, Stage
from devkit.gate.gates.commands import VerifyCommandsGate, VerifyCommandsSettings
from testsupport.gate import gate_ctx, git


@pytest.fixture(autouse=True)
def _logs_in_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    logs = tmp_path / "tmp"
    logs.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(logs))


def _run(repo: Path, *commands: str):
    ctx = gate_ctx(repo, Stage.PRE_COMMIT)
    object.__setattr__(ctx, "settings", VerifyCommandsSettings(list(commands)))
    return VerifyCommandsGate().run(ctx)


def _commit_all(repo: Path) -> None:
    (repo / "a.txt").write_text("a\n")
    git(repo, "add", "a.txt")


def test_no_commands_skips(repo: Path) -> None:
    assert _run(repo).note == "no commands configured"


def test_passing_commands_pass_without_notices_on_a_clean_tree(repo: Path) -> None:
    _commit_all(repo)
    result = _run(repo, "true", "echo ok")
    assert result.note == "2 command(s) passed" and result.notices == ()


def test_every_failed_command_is_reported_with_its_log(repo: Path) -> None:
    _commit_all(repo)
    with pytest.raises(GateRefusedError) as info:
        _run(repo, "echo first broke; exit 3", "true", "echo second broke >&2; exit 1")
    error = info.value
    assert error.code == "GATE_VERIFY_FAILED"
    assert error.message == "verification failed: echo first broke; exit 3, echo second broke >&2; exit 1"
    details = list(error.details)
    assert details[0].startswith("command: echo first broke; exit 3  exit=3  log=")
    assert "  | first broke" in details and "  | second broke" in details
    log = Path(details[0].rsplit("log=", 1)[1])
    assert log.is_file() and "first broke" in log.read_text()


def test_unstaged_and_untracked_files_are_noted(repo: Path) -> None:
    _commit_all(repo)
    git(repo, "commit", "-q", "-m", "init")
    (repo / "a.txt").write_text("changed\n")
    (repo / "new.txt").write_text("new\n")
    result = _run(repo, "true")
    assert [notice.code for notice in result.notices] == ["GATE_VERIFY_UNSTAGED"]
    assert sorted(result.notices[0].details) == ["a.txt", "new.txt"]

    with pytest.raises(GateRefusedError) as info:
        _run(repo, "false")
    assert info.value.details[-1].startswith("note: the commands checked the working tree")


def test_hook_git_variables_do_not_reach_the_commands(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _commit_all(repo)
    monkeypatch.setenv("GIT_INDEX_FILE", str(repo / ".git/index"))
    monkeypatch.setenv("GIT_DIR", str(repo / ".git"))
    result = _run(repo, 'test -z "$GIT_INDEX_FILE" && test -z "$GIT_DIR"')
    assert result.note == "1 command(s) passed"
