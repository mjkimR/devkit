"""The built-in ``verify-commands`` pre-commit gate."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from devkit.advisory import ActionMode, Actor, AdvisoryError, Retry
from devkit.gate import GateRefusedError, Stage
from devkit.gate.errors import VerifyNotRunError
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


def _block_command(
    tmp_path: Path, exit_code: int, actor: Actor = Actor.DEVELOPER, fix: str = "Run `devkit sync`"
) -> str:
    """A command that prints a nested devkit error block on stderr, as `devkit rules check` does, and exits."""
    block = tmp_path / f"block-{actor}-{exit_code}.txt"
    error = AdvisoryError(
        "synchronized rule .devkit/managed/x.py is missing",
        code="RULES_LOAD_FAILED",
        actor=actor,
        retry=Retry.AFTER_FIX,
        fix=fix,
    )
    block.write_text(error.render() + "\n")
    return f"cat {block} >&2; exit {exit_code}"


def test_a_devkit_command_that_could_not_run_is_not_a_refusal(repo: Path, tmp_path: Path) -> None:
    _commit_all(repo)
    with pytest.raises(VerifyNotRunError) as info:
        _run(repo, _block_command(tmp_path, 2), "false")
    error = info.value
    assert error.code == "GATE_VERIFY_NOT_RUN" and error.mode is ActionMode.MAINTENANCE and error.exit_code == 2
    assert "  > [ERROR]  (RULES_LOAD_FAILED) synchronized rule .devkit/managed/x.py is missing" in error.details
    assert "  > [FIX]    Run `devkit sync`" in error.details


def test_a_missing_sync_relayed_as_auto_makes_the_gate_auto(repo: Path, tmp_path: Path) -> None:
    _commit_all(repo)
    auto = _block_command(tmp_path, 2, Actor.TOOL, "devkit sync")
    with pytest.raises(VerifyNotRunError) as info:
        _run(repo, auto, auto)
    assert info.value.mode is ActionMode.AUTO and info.value.fix == "devkit sync"
    with pytest.raises(VerifyNotRunError) as mixed:
        _run(repo, auto, _block_command(tmp_path, 2))
    assert mixed.value.mode is ActionMode.MAINTENANCE


def test_relayed_errors_of_a_command_with_findings_stay_a_refusal(repo: Path, tmp_path: Path) -> None:
    _commit_all(repo)
    with pytest.raises(GateRefusedError) as info:
        _run(repo, _block_command(tmp_path, 1))
    assert info.value.code == "GATE_VERIFY_FAILED" and info.value.mode is ActionMode.BLOCKED
    assert any(line.startswith("  > [ERROR]  (RULES_LOAD_FAILED)") for line in info.value.details)


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


def test_staged_renames_and_copies_are_not_unstaged(repo: Path) -> None:
    src = repo / "src"
    src.mkdir()
    for name in ("old name.py", "moved.py", "original.py"):
        (src / name).write_text("".join(f"{name} {i}\n" for i in range(40)))
    _commit_all(repo)
    git(repo, "add", "src")
    git(repo, "commit", "-q", "-m", "init")
    git(repo, "config", "status.renames", "copies")
    git(repo, "mv", "src/old name.py", "src/new\nname.py")  # "R ": staged only
    git(repo, "mv", "src/moved.py", "src/renamed.py")
    (src / "renamed.py").write_text((src / "renamed.py").read_text() + "edited\n")  # "RM": unstaged edit
    (src / "copy.py").write_text((src / "original.py").read_text())
    (src / "original.py").write_text((src / "original.py").read_text() + "edited\n")
    git(repo, "add", "src/copy.py", "src/original.py")  # "C ": staged only
    (repo / "a.txt").write_text("changed\n")
    (repo / "new file.txt").write_text("new\n")
    status = git(repo, "status", "--porcelain=v1", "-z").stdout.split("\0")
    assert {entry[:2] for entry in status if len(entry) > 3} >= {"R ", "RM", "C ", " M", "??"}

    result = _run(repo, "true")
    assert [notice.code for notice in result.notices] == ["GATE_VERIFY_UNSTAGED"]
    assert sorted(result.notices[0].details) == ["a.txt", "new file.txt", "src/renamed.py"]


def test_hook_git_variables_do_not_reach_the_commands(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _commit_all(repo)
    monkeypatch.setenv("GIT_INDEX_FILE", str(repo / ".git/index"))
    monkeypatch.setenv("GIT_DIR", str(repo / ".git"))
    result = _run(repo, 'test -z "$GIT_INDEX_FILE" && test -z "$GIT_DIR"')
    assert result.note == "1 command(s) passed"
