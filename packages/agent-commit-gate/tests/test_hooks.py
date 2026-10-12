from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from agent_commit_gate import hooks
from agent_commit_gate.cli import cli
from agent_commit_gate.models import Stage
from click.testing import CliRunner
from conftest import deploy_gate, gate_source, git


def _cli(*args: str) -> object:
    return CliRunner().invoke(cli, list(args))


def _install(repo: Path, *extra: str) -> None:
    result = CliRunner().invoke(cli, ["install", "-w", str(repo), "--python", sys.executable, *extra])
    assert result.exit_code == 0, result.output


def test_install_status_uninstall(repo: Path) -> None:
    _install(repo)
    states = {s.stage: s for s in hooks.status(repo)}
    assert all(s.state is hooks.HookState.MANAGED and s.python_ok for s in states.values())
    script = (repo / ".git/hooks/pre-commit").read_text()
    assert hooks.MARKER in script and "-m agent_commit_gate run pre-commit" in script

    result = CliRunner().invoke(cli, ["status", "-w", str(repo), "--format", "json"])
    data = json.loads(result.output)
    assert [h["state"] for h in data["hooks"]] == ["managed"] * 3
    assert [g["id"] for g in data["gates"]] == ["rules-staged", "message-nonempty"] and data["config_sources"] == []

    _install(repo)  # reinstalling over managed wrappers needs no --force
    result = CliRunner().invoke(cli, ["uninstall", "-w", str(repo)])
    assert result.exit_code == 0 and not (repo / ".git/hooks/pre-commit").exists()


def test_foreign_hooks_need_force_and_are_restored(repo: Path) -> None:
    foreign = repo / ".git/hooks/pre-commit"
    foreign.write_text("#!/bin/sh\nexit 0\n")
    result = CliRunner().invoke(cli, ["install", "-w", str(repo), "--python", sys.executable])
    assert result.exit_code != 0 and "GATE_FOREIGN_HOOK" in result.output
    assert foreign.read_text() == "#!/bin/sh\nexit 0\n"

    _install(repo, "--force")
    assert (repo / ".git/hooks/pre-commit.pre-gate").read_text() == "#!/bin/sh\nexit 0\n"
    CliRunner().invoke(cli, ["uninstall", "-w", str(repo)])
    assert foreign.read_text() == "#!/bin/sh\nexit 0\n" and not (repo / ".git/hooks/pre-commit.pre-gate").exists()


def test_core_hooks_path_is_refused(repo: Path) -> None:
    git(repo, "config", "core.hooksPath", ".husky")
    result = CliRunner().invoke(cli, ["install", "-w", str(repo), "--python", sys.executable])
    assert result.exit_code != 0 and "GATE_HOOKS_PATH_SET" in result.output


def _commit(repo: Path, *args: str) -> tuple[int, str]:
    (repo / "file.txt").write_text(str(len(list(repo.iterdir()))) + str(args))
    git(repo, "add", "file.txt")
    result = git(repo, "commit", *args, check=False)
    return result.returncode, result.stdout + result.stderr


def test_commits_run_built_in_and_deployed_gates(repo: Path) -> None:
    _install(repo)
    code, output = _commit(repo, "-m", "feat: first")
    assert code == 0, output

    code, output = _commit(repo, "--allow-empty-message", "-m", "")
    assert code != 0 and "GATE_MESSAGE_EMPTY" in output

    deploy_gate(repo, gate_source())
    code, output = _commit(repo, "-m", "feat: blocked")
    assert code != 0 and "[GATE: team-block stage=pre-commit outcome=failed]" in output and "TEST_REFUSED" in output

    # The tracked project config is overridden by the clone-local one.
    (repo / ".devkit/config.toml").write_text("[gates.settings.team-block]\nallow = true\n")
    code, _ = _commit(repo, "-m", "feat: allowed by project")
    assert code == 0
    (repo / ".git/devkit.config").write_text("[gates.settings.team-block]\nallow = false\n")
    code, output = _commit(repo, "-m", "feat: blocked locally")
    assert code != 0 and "TEST_REFUSED" in output


def test_wrapper_without_interpreter(repo: Path, tmp_path: Path) -> None:
    _install(repo, "--python", str(tmp_path / "gone/python"))
    code, output = _commit(repo, "-m", "feat: x")
    assert code != 0 and "not found; run 'uv sync'" in output
    # post-commit is not blocking: its wrapper exits 0 when the interpreter is gone.
    assert f"exit {int(Stage.POST_COMMIT.blocking)}" in (repo / ".git/hooks/post-commit").read_text()


def test_run_command_verbose_and_post_commit_never_blocks(repo: Path) -> None:
    message = repo / "MSG"
    message.write_text("fix: y\n")
    result = CliRunner().invoke(cli, ["run", "-w", str(repo), "-v", "commit-msg", "MSG"])
    assert result.exit_code == 0 and "[GATE: message-nonempty stage=commit-msg outcome=passed]" in result.output

    (repo / ".git/devkit.config").write_text("[gates.settings.unknown]\nenabled = true\n")
    assert CliRunner().invoke(cli, ["run", "-w", str(repo), "post-commit"]).exit_code == 0
    result = CliRunner().invoke(cli, ["run", "-w", str(repo), "pre-commit"])
    assert result.exit_code == 1 and "not installed: ['unknown']" in result.output


@pytest.mark.parametrize("stage", list(Stage))
def test_wrapper_script_quotes_interpreter(stage: Stage) -> None:
    script = hooks.wrapper_script(stage, "/path with space/python")
    assert "python='/path with space/python'" in script
    assert hooks._read_python(script) == "/path with space/python"
