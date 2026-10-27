from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

import devkit_agt.features.gate.usecases.hooks.hooks as hooks
import pytest
from click.testing import CliRunner
from devkit.advisory import ExitCode
from devkit_agt.features.gate import RunHookUseCase, load_gate_project
from devkit_agt.features.gate.cli import cli
from devkit_agt.features.gate.models.contracts import Stage
from testsupport.gate import deploy_gate, gate_source, git

PYTHON = Path(sys.executable).as_posix()


def _invoke(*args: str) -> tuple[int, str]:
    result = CliRunner().invoke(cli, list(args))
    return result.exit_code, result.output


def _install(repo: Path, *extra: str) -> str:
    code, output = _invoke("install", "-w", str(repo), "--python", sys.executable, *extra)
    assert code == 0, output
    return output


def _status(repo: Path, expected: int = 0) -> dict:
    code, output = _invoke("status", "-w", str(repo), "--format", "json")
    assert code == expected, output
    return json.loads(output)


def _commit(repo: Path, *args: str, name: str = "file.txt") -> tuple[int, str]:
    (repo / name).write_text(str(len(list(repo.iterdir()))) + str(args))
    git(repo, "add", name)
    result = git(repo, "commit", *args, check=False)
    return result.returncode, result.stdout + result.stderr


def test_install_status_uninstall(repo: Path) -> None:
    _install(repo)
    states = {s.stage: s for s in hooks.status(repo)}
    assert all(s.state is hooks.HookState.MANAGED for s in states.values())
    assert states[Stage.PRE_COMMIT].python_ok and states[Stage.COMMIT_MSG].python_ok
    assert states[Stage.POST_COMMIT].python is None
    script = (repo / ".git/hooks/pre-commit").read_text()
    assert hooks.MARKER in script
    assert '-P -c "$bootstrap" pre-commit' in (repo / ".git/hooks/pre-commit.d/20-devkit").read_text()

    data = _status(repo)
    assert [h["state"] for h in data["hooks"]] == ["managed"] * 3
    assert [g["id"] for g in data["gates"]] == ["rules-check", "verify-commands", "message-nonempty"]
    assert data["config_sources"] == []
    assert data["hooks_dir"] == str((repo / ".git/hooks").resolve()) and data["hooks_path"] is None
    assert data["errors"] == []

    _install(repo)  # reinstalling over managed wrappers needs no --force
    code, _ = _invoke("uninstall", "-w", str(repo))
    assert code == 0 and not (repo / ".git/hooks/pre-commit").exists()


def test_wrappers_are_lf_only_and_record_an_absolute_interpreter(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    relative = os.path.relpath(sys.executable, tmp_path)
    code, output = _invoke("install", "-w", str(repo), "--python", relative)
    assert code == 0, output
    data = (repo / ".git/hooks/pre-commit.d/20-devkit").read_bytes()
    assert b"\r" not in data
    # Absolute, with the venv's interpreter symlink kept rather than resolved.
    assert hooks._read_python(data.decode()) == Path(os.path.abspath(sys.executable)).as_posix()
    assert all(item.python_ok for item in hooks.status(repo) if item.stage.blocking)


def test_install_refuses_an_interpreter_without_devkit(repo: Path, tmp_path: Path) -> None:
    code, output = _invoke("install", "-w", str(repo), "--python", str(tmp_path / "gone/python"))
    assert code != 0 and "GATE_PYTHON_INVALID" in output and "not an executable file" in output

    fake = tmp_path / "fake-python"
    fake.write_text("#!/bin/sh\necho 'No module named devkit' >&2\nexit 1\n")
    fake.chmod(0o755)
    code, output = _invoke("install", "-w", str(repo), "--python", str(fake))
    assert code != 0 and "cannot import devkit_agt.features.gate" in output and "No module named devkit" in output
    assert not (repo / ".git/hooks/pre-commit").exists()


def test_foreign_hooks_are_preserved_automatically_and_restored(repo: Path) -> None:
    foreign = repo / ".git/hooks/pre-commit"
    foreign.write_text("#!/bin/sh\necho previous-hook-ran\nexit 0\n")
    foreign.chmod(0o755)
    code, output = _invoke("install", "-w", str(repo), "--python", sys.executable)
    assert code == 0 and "GATE_HOOK_PRESERVED" in output
    assert "previous-hook-ran" in (repo / ".git/hooks/pre-commit.devkit-preserved").read_text()
    code, output = _commit(repo, "-m", "feat: chained")
    assert code == 0 and "previous-hook-ran" in output, output

    _invoke("uninstall", "-w", str(repo))
    assert "previous-hook-ran" in foreign.read_text() and not (repo / ".git/hooks/pre-commit.devkit-preserved").exists()


def test_a_failing_moved_aside_hook_still_blocks_the_commit(repo: Path) -> None:
    foreign = repo / ".git/hooks/pre-commit"
    foreign.write_text("#!/bin/sh\necho previous-hook-refused >&2\nexit 3\n")
    foreign.chmod(0o755)
    _install(repo, "--force")
    code, output = _commit(repo, "-m", "feat: x")
    assert code != 0 and "previous-hook-refused" in output


def test_inert_hooks_are_moved_aside_without_force(repo: Path) -> None:
    inert = repo / ".git/hooks/pre-commit"
    inert.write_text("#!/bin/sh\nexit 1\n")
    inert.chmod(0o644)
    assert hooks.status(repo)[0].state is hooks.HookState.INERT
    output = _install(repo)
    assert "moved inert (non-executable) hook" in output
    code, _ = _commit(repo, "-m", "feat: inert hook is still ignored")
    assert code == 0


@pytest.mark.parametrize("target", ["../../.githooks/pre-commit", "/nonexistent/hook"])
def test_symlinked_hooks_are_foreign_and_never_written_through(repo: Path, target: str) -> None:
    (repo / ".githooks").mkdir()
    link = repo / ".git/hooks/pre-commit"
    link.symlink_to(target)
    assert hooks.status(repo)[0].state is hooks.HookState.FOREIGN
    code, output = _invoke("install", "-w", str(repo), "--python", sys.executable)
    assert code != 0 and "GATE_FOREIGN_HOOK" in output

    _install(repo, "--force")
    assert not link.is_symlink() and hooks.MARKER in link.read_text()
    assert list((repo / ".githooks").iterdir()) == []
    _invoke("uninstall", "-w", str(repo))
    assert link.is_symlink() and os.readlink(link) == target


def test_core_hooks_path_is_refused_and_reported(repo: Path) -> None:
    git(repo, "config", "core.hooksPath", ".husky")
    code, output = _invoke("install", "-w", str(repo), "--python", sys.executable)
    assert code != 0 and "GATE_HOOKS_PATH_SET" in output

    git(repo, "config", "--unset", "core.hooksPath")
    _install(repo)
    git(repo, "config", "core.hooksPath", ".husky")
    data = _status(repo)  # a warning: the report still exits 0
    assert data["hooks_path"] == ".husky" and [h["state"] for h in data["hooks"]] == ["managed"] * 3
    assert [(n["code"], n["level"]) for n in data["notices"]] == [("GATE_HOOKS_PATH_SET", "WARNING")]
    notice = data["notices"][0]
    assert notice["message"].startswith("enabled gates do not run: core.hooksPath is set to '.husky'")
    assert notice["advisory"]["details"] == ["gates=rules-check,verify-commands,message-nonempty"]
    assert (
        notice["advisory"]["fix"]
        == "Once the user agrees, run `git config --unset core.hooksPath`, then `uv run devkit gate install`"
    )
    code, output = _invoke("status", "-w", str(repo))
    assert code == 0 and "core.hooksPath=.husky (wrappers do not run)" in output
    assert "GATE_HOOK_ENTRY_MISSING" not in output
    assert _invoke("status", "-w", str(repo), "--strict")[0] == 1
    code, output = _invoke("uninstall", "-w", str(repo))
    assert code == 0 and "pre-commit: removed" in output and not (repo / ".git/hooks/pre-commit").exists()


def _fix_command(output: str) -> list[str]:
    fix = next(line for line in output.splitlines() if line.startswith("[FIX] "))
    return shlex.split(fix.split("`")[1])


def test_hooks_path_fix_names_the_scope_that_sets_it(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git(repo, "config", "core.hooksPath", ".husky")
    code, output = _invoke("install", "-w", str(repo), "--python", sys.executable)
    assert code != 0 and "(local config)" in output
    assert _fix_command(output) == ["git", "config", "--unset", "core.hooksPath"]
    git(repo, "config", "--unset", "core.hooksPath")

    # A global value cannot be unset with a local `--unset`; the fix overrides it for this repository only.
    global_config = tmp_path / "global.gitconfig"
    global_config.write_text("[core]\n\thooksPath = /shared/hooks\n")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(global_config))
    code, output = _invoke("install", "-w", str(repo), "--python", sys.executable)
    assert code != 0 and "GATE_HOOKS_PATH_SET" in output and "(global config)" in output
    command = _fix_command(output)
    assert command == ["git", "config", "core.hooksPath", (repo / ".git/hooks").as_posix()]
    git(repo, *command[1:])
    _install(repo)
    assert "/shared/hooks" in global_config.read_text()

    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.hooksPath")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", ".husky")
    code, output = _invoke("install", "-w", str(repo), "--python", sys.executable)
    assert code != 0 and "(command config)" in output and "GIT_CONFIG_* environment variables" in output


def test_a_directory_moved_aside_does_not_break_commits(repo: Path) -> None:
    (repo / ".git/hooks/pre-commit").mkdir()
    assert hooks.status(repo)[0].state is hooks.HookState.FOREIGN
    _install(repo, "--force")
    assert (repo / ".git/hooks/pre-commit.devkit-preserved").is_dir()
    code, output = _commit(repo, "-m", "feat: x")
    assert code == 0, output
    _invoke("uninstall", "-w", str(repo))
    assert (repo / ".git/hooks/pre-commit").is_dir()


def test_hooks_path_naming_the_default_directory_is_not_a_conflict(repo: Path) -> None:
    git(repo, "config", "core.hooksPath", ".git/hooks")
    _install(repo)
    assert _status(repo)["hooks_path"] is None


def test_commits_run_built_in_gates(repo: Path) -> None:
    _install(repo)
    code, output = _commit(repo, "-m", "feat: first")
    assert code == 0, output

    code, output = _commit(repo, "--allow-empty-message", "-m", "")
    assert code != 0 and "GATE_MESSAGE_EMPTY" in output

    code, output = _commit(repo, "-m", "#123 fix the parser")  # `git commit -m` hands the hook the '#' line
    assert code == 0, output


def test_deployed_gates_read_the_project_and_clone_config(repo: Path) -> None:
    # Gate logic runs in-process; the commits above and the worktree test cover the wrappers.
    deploy_gate(repo, gate_source())
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 1 and "[DETAIL] gate=team-block stage=pre-commit" in output and "TEST_REFUSED" in output

    # The tracked project config is overridden by the clone-local one.
    (repo / ".devkit/config.toml").write_text("[gates.settings.team-block]\nallow = true\n")
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 0, output
    (repo / ".git/devkit.config").write_text("[gates.settings.team-block]\nallow = false\n")
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 1 and "TEST_REFUSED" in output


def test_ctrl_c_during_verify_commands_aborts_with_130(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tempfile, "tempdir", str(repo.parent))  # where the command's log goes
    (repo / ".devkit").mkdir()
    (repo / ".devkit/config.toml").write_text(
        '[gates.settings.verify-commands]\ncommands = ["kill -INT $PPID; sleep 30", "true"]\n'
    )
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 128 + signal.SIGINT, output  # as `devkit run` exits, not UNEXPECTED_ERROR (2)
    assert "UNEXPECTED_ERROR" not in output


def test_repository_modules_do_not_shadow_the_hook(repo: Path) -> None:
    _install(repo)
    (repo / "json.py").write_text("raise SystemExit('repository json.py was imported')\n")
    code, output = _commit(repo, "-m", "feat: add json.py", name="json.py")
    assert code == 0, output


def _run_entry(repo: Path, stage: Stage, python: str) -> subprocess.CompletedProcess[str]:
    entry = repo / ".git/hooks" / f"{stage.value}.d" / hooks.DEVKIT_ENTRY
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text(hooks.wrapper_script(stage, python))
    entry.chmod(0o755)
    return subprocess.run([str(entry)], cwd=repo, capture_output=True, text=True, check=False)


def _venv_without_devkit(tmp_path: Path) -> Path:
    venv = tmp_path / "bare-venv"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(venv)], check=True)
    return venv


def _assert_unavailable(result: subprocess.CompletedProcess[str], stage: Stage, reason: str) -> None:
    # Exit 2 (could not run) in a blocking stage, never 1 (gates refused); post-commit only warns.
    blocking = stage.blocking
    assert result.returncode == (2 if blocking else 0), result.stderr
    assert "Traceback" not in result.stderr
    lines = result.stderr.splitlines()
    headline = "[ERROR]  " if blocking else "[WARN]   "
    assert (
        lines[0]
        == f"{headline}(GATE_INTERPRETER_UNAVAILABLE) {stage.value}: no interpreter can import devkit_agt.features.gate; the gates did not run"
    )
    assert lines[1].startswith("[ACTION] MAINTENANCE" if blocking else "[ACTION] CONTINUE")
    assert any(line.startswith("[FIX]    Run `uv sync`") for line in lines)
    assert lines[-2].startswith("[DETAIL] python=") and lines[-1].startswith(f"[DETAIL] {reason}")


@pytest.mark.parametrize("stage", list(Stage))
def test_wrapper_without_interpreter(repo: Path, tmp_path: Path, stage: Stage) -> None:
    result = _run_entry(repo, stage, (tmp_path / "gone/python").as_posix())
    _assert_unavailable(result, stage, "not an executable file")
    assert f"[DETAIL] python={(tmp_path / 'gone/python').as_posix()}" in result.stderr


@pytest.mark.parametrize("stage", list(Stage))
def test_wrapper_with_interpreter_without_devkit(repo: Path, tmp_path: Path, stage: Stage) -> None:
    python = _venv_without_devkit(tmp_path) / "bin/python"
    _assert_unavailable(_run_entry(repo, stage, python.as_posix()), stage, "ModuleNotFoundError: ")


def test_wrapper_with_interpreter_whose_devkit_is_broken(repo: Path, tmp_path: Path) -> None:
    venv = _venv_without_devkit(tmp_path)
    site = next((venv / "lib").glob("python*/site-packages"))
    (site / "devkit_agt/features/gate").mkdir(parents=True)
    (site / "devkit_agt/features/gate/__init__.py").write_text(
        "raise RuntimeError('incompatible devkit\\nsecond line')\n"
    )
    result = _run_entry(repo, Stage.PRE_COMMIT, (venv / "bin/python").as_posix())
    _assert_unavailable(result, Stage.PRE_COMMIT, "RuntimeError: incompatible devkit")
    assert "second line" not in result.stderr


def test_commit_aborts_without_interpreter(repo: Path, tmp_path: Path) -> None:
    directory = repo / ".git/hooks"
    for stage in Stage:
        (directory / stage.value).write_text(hooks.wrapper_script(stage, (tmp_path / "gone/python").as_posix()))
        (directory / stage.value).chmod(0o755)
    code, output = _commit(repo, "-m", "feat: x")
    assert code != 0 and "(GATE_INTERPRETER_UNAVAILABLE) pre-commit" in output


def test_wrapper_probes_only_the_posix_venv_layout() -> None:
    script = hooks.wrapper_script(Stage.PRE_COMMIT, PYTHON)
    shell = script.replace("sys.executable", "")
    assert "Scripts" not in shell and ".exe" not in shell and "/Lib/" not in shell
    assert '"$top/.venv/bin/python"' in script


def test_wrapper_prefers_the_work_tree_venv_when_it_has_devkit(repo: Path, tmp_path: Path) -> None:
    _install(repo)
    marker = tmp_path / "venv-python-used"
    venv = repo / ".venv"
    (venv / "bin").mkdir(parents=True)
    shim = venv / "bin/python"
    shim.write_text(f'#!/bin/sh\ntouch "{marker}"\nexec "{PYTHON}" "$@"\n')
    shim.chmod(0o755)
    (repo / ".gitignore").write_text(".venv/\n")

    code, output = _commit(repo, "-m", "feat: venv without devkit")
    assert code == 0 and not marker.exists(), output

    (venv / "lib/python3.12/site-packages/devkit_agt-0.1.0.dist-info").mkdir(parents=True)
    code, output = _commit(repo, "-m", "feat: venv with devkit")
    assert code == 0 and marker.exists(), output


def test_staged_rules_in_verify_commands_check_what_is_committed(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TMPDIR", str(tmp_path))  # the commands' logs
    (repo / "README.md").write_text("# Repo\n")
    (repo / "a.md").write_text("[ok](README.md)\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "init")
    _install(repo)
    command = f"{shlex.quote(PYTHON)} -m devkit_dist rules check --staged"
    (repo / ".git/devkit.config").write_text(
        f"[gates.settings.verify-commands]\ncommands = [{json.dumps(command)}]\n"
        "[gates.settings.rules-check]\nenabled = false\n"  # the nested command alone, as a project may configure it
    )

    # `commit -a` and `commit <paths>` commit a temporary index, which the staged check reads.
    (repo / "a.md").write_text("[bad](missing.md)\n")
    result = git(repo, "commit", "-am", "feat: all", check=False)
    assert result.returncode != 0 and "GATE_VERIFY_FAILED" in result.stderr and "missing.md" in result.stderr
    result = git(repo, "commit", "-m", "feat: partial", "a.md", check=False)
    assert result.returncode != 0 and "GATE_VERIFY_FAILED" in result.stderr

    # A broken file that is staged but left out of a partial commit is not checked.
    git(repo, "checkout", "a.md")
    (repo / "b.md").write_text("[bad](missing.md)\n")
    git(repo, "add", "b.md")
    (repo / "README.md").write_text("# Repo 2\n")
    result = git(repo, "commit", "-m", "docs: readme only", "README.md", check=False)
    assert result.returncode == 0, result.stderr


def test_linked_worktree_shares_hooks_and_clone_config(repo: Path, tmp_path: Path) -> None:
    (repo / "README.md").write_text("# Repo\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "init")
    worktree = tmp_path / "wt"
    git(repo, "worktree", "add", "-q", str(worktree), "-b", "wt")

    _install(worktree)  # installs into the common hooks directory
    assert (repo / ".git/hooks/pre-commit").is_file()

    source = gate_source("where").replace(
        'raise GateRefusedError("where refused", code="TEST_REFUSED")',
        'raise GateRefusedError(f"git_dir={ctx.git_dir} common={ctx.common_git_dir}", code="TEST_REFUSED")',
    )
    deploy_gate(worktree, source)
    code, output = _commit(worktree, "-m", "feat: in worktree")
    common = (repo / ".git").resolve()
    assert code != 0 and f"git_dir={common / 'worktrees/wt'} common={common}" in output, output

    # The clone-local config lives in the common git dir, so every worktree reads it.
    (repo / ".git/devkit.config").write_text("[gates.settings.where]\nenabled = false\n")
    code, output = _invoke("run", "-w", str(worktree), "pre-commit")
    assert code == 0, output


def test_run_command_verbose_and_post_commit_never_blocks(repo: Path) -> None:
    message = repo / "MSG"
    message.write_text("fix: y\n")
    code, output = _invoke("run", "-w", str(repo), "-v", "commit-msg", "MSG")
    assert (
        code == 0
        and "[INFO]   devkit_agt.features.gate.usecases.runner: gate message-nonempty stage=commit-msg outcome=passed"
        in output
    )
    code, output = _invoke("run", "-w", str(repo), "commit-msg", "MSG")
    assert code == 0 and output == ""  # silent when every gate passes

    (repo / ".git/devkit.config").write_text("[gates.settings.unknown]\nenabled = true\n")
    code, output = _invoke("run", "-w", str(repo), "post-commit")
    # The commit exists: the same problem is a warning, never an [ERROR] telling the agent to stop.
    assert code == 0 and output.startswith("[WARN]   (GATE_CONFIG_INVALID) configured gates are not installed")
    assert "[ACTION] CONTINUE — " in output and "[ERROR]" not in output
    assert _invoke("run", "-w", str(repo), "--strict", "post-commit")[0] == 0  # post-commit always exits 0
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 2 and output.startswith("[ERROR]  (GATE_CONFIG_INVALID)")  # a configuration problem
    assert "not installed: ['unknown']" in output

    (repo / ".git/devkit.config").write_text("[gates\n")
    code, output = _invoke("run", "-w", str(repo), "post-commit")
    assert code == 0 and "invalid config" in output
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 2 and "invalid config" in output


def test_status_reports_every_problem_that_fails_a_commit(repo: Path) -> None:
    (repo / ".git/devkit.config").write_text("[gates.settings.typo-gate]\nenabled = true\n")
    data = _status(repo, 1)  # a report listing problems exits 1
    assert [e["code"] for e in data["errors"]] == ["GATE_CONFIG_INVALID"]
    assert "not installed: ['typo-gate']" in data["errors"][0]["message"]

    (repo / ".git/devkit.config").write_text("[gates.settings.message-nonempty]\nenabled = false\nbogus = 1\n")
    assert "gate has no settings" in _status(repo, 1)["errors"][0]["message"]

    (repo / ".git/devkit.config").write_text("[gates\n")
    data = _status(repo, 1)
    assert "invalid config" in data["errors"][0]["message"] and data["gates"]
    assert data["errors"][0]["code"] == "CONFIG_INVALID"  # the core error, not re-wrapped
    code, output = _invoke("status", "-w", str(repo))
    assert code == 1 and "(CONFIG_INVALID)" in output

    (repo / ".git/devkit.config").unlink()
    assert _status(repo)["errors"] == []


def test_outside_a_repository_is_an_input_error(tmp_path: Path) -> None:
    code, output = _invoke("status", "-w", str(tmp_path))
    assert code == 2 and "(GIT_FAILED)" in output and "INPUT_ERROR" in output

    result = CliRunner().invoke(cli, ["status", "-w", str(tmp_path), "--format", "json"])
    assert result.exit_code == 2
    assert json.loads(result.stdout)["error"]["code"] == "GIT_FAILED"

    missing = CliRunner().invoke(cli, ["status", "-w", str(tmp_path / "missing"), "--format", "JSON"])
    assert missing.exit_code == 2
    assert (
        json.loads(missing.stdout)["error"]["code"] == "ARGUMENT_INVALID"
    )  # one JSON document, not click's usage text


def test_every_command_uses_the_git_top_level(repo: Path) -> None:
    (repo / "sub").mkdir()
    _install(repo / "sub")
    data = _status(repo / "sub")
    assert data["hooks_dir"] == str((repo / ".git/hooks").resolve())
    assert {h["state"] for h in data["hooks"]} == {"managed"}


def test_run_exit_codes(repo: Path, tmp_path: Path) -> None:
    assert _invoke("run", "-w", str(repo), "pre-commit")[0] == 0
    deploy_gate(repo, gate_source())
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 1 and "(TEST_REFUSED)" in output  # a gate refused the commit
    outside = tmp_path / "outside"
    outside.mkdir()
    code, output = _invoke("run", "-w", str(outside), "pre-commit")
    assert code == 2 and "(GIT_FAILED)" in output  # the stage could not run, and still blocks
    code, output = _invoke("run", "-w", str(outside), "post-commit")
    assert code == 0 and output.startswith("[WARN]   (GIT_FAILED)")  # post-commit reports only
    assert _invoke("run", "-w", str(repo), "pre-commit-typo")[0] == 2  # usage error


def test_run_exits_with_the_highest_problem_exit_code(repo: Path) -> None:
    deploy_gate(repo, gate_source())
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 1 and "(TEST_REFUSED)" in output  # a refusal alone
    (repo / ".git/devkit.config").write_text("[gates.settings.typo]\nenabled = true\n")
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 2 and "(TEST_REFUSED)" in output and "(GATE_CONFIG_INVALID)" in output


def test_library_entry_points(repo: Path) -> None:
    (repo / "sub").mkdir()
    project = load_gate_project(repo / "sub")
    assert project.root == repo and project.common_git_dir == (repo / ".git").resolve()
    assert project.validation.ok and project.config.sources == ()
    assert [g.id for g in project.registry.get_all()] == ["rules-check", "verify-commands", "message-nonempty"]

    (repo / "MSG").write_text("\n")
    report = RunHookUseCase().execute(repo, Stage.COMMIT_MSG, ["MSG"])
    assert not report.ok and report.exit_code is ExitCode.FINDINGS
    assert [e.code for e in report.problems] == ["GATE_MESSAGE_EMPTY"]

    report = RunHookUseCase().execute(repo, Stage.COMMIT_MSG)
    assert [e.code for e in report.problems] == ["ARGUMENT_INVALID"] and report.exit_code is ExitCode.ERROR


def test_install_refusals_exit_2(repo: Path, tmp_path: Path) -> None:
    code, _ = _invoke("install", "-w", str(repo), "--python", str(tmp_path / "gone/python"))
    assert code == 2
    git(repo, "config", "core.hooksPath", ".husky")
    code, output = _invoke("install", "-w", str(repo), "--python", sys.executable)
    assert code == 2 and "GATE_HOOKS_PATH_SET" in output


@pytest.mark.parametrize("stage", list(Stage))
def test_wrapper_script_quotes_interpreter(stage: Stage) -> None:
    script = hooks.wrapper_script(stage, "/path with space/python")
    assert "python='/path with space/python'" in script
    assert hooks._read_python(script) == "/path with space/python"


def _script(path: Path, body: str) -> None:
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(0o755)


def test_dispatcher_order_arguments_environment_and_direct_children(repo: Path) -> None:
    _install(repo)
    entries = repo / ".git/hooks/commit-msg.d"
    # Put a non-shell executable between checks, with spaces in its filename and arguments.
    before = entries / "10 before"
    _script(before, 'printf "before:%s:%s:%s\\n" "$1" "$LC_ALL" "$GIT_INDEX_FILE" >> order\n')
    python = entries / "30-python"
    python.write_text(f"#!{PYTHON}\nfrom pathlib import Path\nPath('order').open('a').write('after\\n')\n")
    python.chmod(0o755)
    _script(entries / "40-inert", "exit 9\n")
    (entries / "40-inert").chmod(0o644)
    (entries / "50-directory").mkdir()
    _script(entries / "50-directory/nested", "exit 9\n")
    (repo / "message with spaces").write_text("subject\n")
    env = {**os.environ, "LC_ALL": "C.UTF-8", "GIT_INDEX_FILE": str(repo / ".git/index")}
    result = subprocess.run(
        [str(repo / ".git/hooks/commit-msg"), "message with spaces"],
        cwd=repo,
        env=env,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert (repo / "order").read_text().splitlines() == [
        f"before:message with spaces:C.UTF-8:{repo / '.git/index'}",
        "after",
    ]


def test_custom_script_failure_blocks_with_original_code_and_post_commit_continues(repo: Path) -> None:
    _install(repo)
    for stage in (Stage.PRE_COMMIT, Stage.POST_COMMIT):
        entries = repo / f".git/hooks/{stage}.d"
        _script(entries / "10-fail", "exit 7\n")
        _script(entries / "30-after", f"touch {stage}-after\n")
        result = subprocess.run([str(repo / f".git/hooks/{stage}")], cwd=repo, capture_output=True, text=True)
        assert result.returncode == (7 if stage.blocking else 0)
        assert (repo / f"{stage}-after").exists() is not stage.blocking
        if not stage.blocking:
            assert "GATE_HOOK_SCRIPT_FAILED" in result.stderr and "[ACTION] CONTINUE" in result.stderr


def test_uninstall_keeps_user_scripts_and_the_legacy_hook(repo: Path) -> None:
    _script(repo / ".git/hooks/pre-commit", "echo legacy >> ran\n")
    _install(repo)
    custom = repo / ".git/hooks/pre-commit.d/30-custom"
    _script(custom, "echo custom >> ran\n")
    assert _invoke("uninstall", "-w", str(repo))[0] == 0
    assert custom.exists() and not (custom.parent / "20-devkit").exists()
    result = subprocess.run([str(repo / ".git/hooks/pre-commit")], cwd=repo, capture_output=True)
    assert result.returncode == 0 and (repo / "ran").read_text() == "legacy\ncustom\n"
    custom.unlink()
    assert _invoke("uninstall", "-w", str(repo))[0] == 0
    assert not custom.parent.exists()
    assert (repo / ".git/hooks/pre-commit").read_text().endswith("echo legacy >> ran\n")


def test_install_is_idempotent_and_retains_custom_scripts(repo: Path) -> None:
    _script(repo / ".git/hooks/pre-commit", "exit 0\n")
    assert "GATE_HOOK_PRESERVED" in _install(repo)
    custom = repo / ".git/hooks/pre-commit.d/30-custom"
    _script(custom, "exit 0\n")
    paths = [custom, custom.parent / "20-devkit", custom.parent / "00-legacy", repo / ".git/hooks/pre-commit"]
    before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}
    assert "GATE_HOOK_PRESERVED" not in _install(repo)
    assert before == {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}


@pytest.mark.parametrize(
    "conflict", ["pre-commit.devkit-preserved", "commit-msg.d/20-devkit", "commit-msg.d/00-legacy", "commit-msg.d"]
)
def test_conflicting_paths_are_not_overwritten_and_preflight_all_stages(repo: Path, conflict: str) -> None:
    original = repo / ".git/hooks/pre-commit"
    _script(original, "exit 0\n")
    path = repo / ".git/hooks" / conflict
    path.parent.mkdir(exist_ok=True)
    path.write_text("keep me\n")
    code, output = _invoke("install", "-w", str(repo))
    assert code == 2 and ("GATE_BACKUP_EXISTS" in output or "GATE_HOOK_LAYOUT_INVALID" in output)
    assert original.read_text() == "#!/bin/sh\nexit 0\n" and path.read_text() == "keep me\n"
    assert not (repo / ".git/hooks/post-commit.d").exists()


def test_empty_stages_only_get_dispatchers_and_directories(repo: Path) -> None:
    (repo / ".devkit").mkdir()
    (repo / ".devkit/config.toml").write_text(
        "[gates.settings.rules-check]\nenabled = false\n[gates.settings.verify-commands]\nenabled = false\n"
        "[gates.settings.message-nonempty]\nenabled = false\n"
    )
    _install(repo)
    assert all(item.state is hooks.HookState.MANAGED and item.python is None for item in hooks.status(repo))
    for stage in Stage:
        assert list((repo / f".git/hooks/{stage}.d").iterdir()) == []
    (repo / ".devkit/config.toml").write_text("")
    _install(repo)
    assert (repo / ".git/hooks/pre-commit.d/20-devkit").exists()
    # Do not remove an entry installed for another worktree when this worktree disables it.
    (repo / ".devkit/config.toml").write_text("[gates.settings.verify-commands]\nenabled = false\n")
    _install(repo)
    assert (repo / ".git/hooks/pre-commit.d/20-devkit").exists()


def test_failed_dispatcher_write_restores_the_existing_hook(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hook = repo / ".git/hooks/pre-commit"
    _script(hook, "exit 0\n")
    original = hook.read_bytes()
    write = hooks._write

    def fail_dispatcher(path: Path, text: str, *, dry_run: bool = False) -> bool:
        if path == hook:
            raise OSError("write failed")
        return write(path, text, dry_run=dry_run)

    monkeypatch.setattr(hooks, "_write", fail_dispatcher)
    with pytest.raises(OSError, match="write failed"):
        hooks.install(repo, sys.executable)
    assert hook.read_bytes() == original and not (repo / ".git/hooks/pre-commit.devkit-preserved").exists()


def test_symlinked_script_directory_is_not_written_through(repo: Path, tmp_path: Path) -> None:
    target = tmp_path / "user-hooks"
    target.mkdir()
    (repo / ".git/hooks/pre-commit.d").symlink_to(target, target_is_directory=True)
    code, output = _invoke("install", "-w", str(repo), "--force")
    assert code == 2 and "GATE_HOOK_LAYOUT_INVALID" in output
    assert list(target.iterdir()) == [] and not (repo / ".git/hooks/pre-commit").exists()


def test_preserved_hook_keeps_directory_relative_resources(repo: Path) -> None:
    hook = repo / ".git/hooks/pre-commit"
    (hook.parent / "resource").write_text("kept\n")
    _script(hook, 'cat "$(dirname "$0")/resource" > legacy-result\n')
    _install(repo)
    code, output = _commit(repo, "-m", "feat: preserve hook resources")
    assert code == 0 and (repo / "legacy-result").read_text() == "kept\n", output


_POST_COMMIT_GATE = gate_source("after-commit", enabled=False, cls="AfterGate").replace(
    "stage=Stage.PRE_COMMIT", "stage=Stage.POST_COMMIT"
)


def test_status_warns_when_an_enabled_gate_has_no_hook_entry(repo: Path) -> None:
    deploy_gate(repo, _POST_COMMIT_GATE, ".devkit/managed/team/gates/after/gate.py")
    _install(repo)  # off by default: post-commit gets no 20-devkit entry
    assert _status(repo)["notices"] == []

    (repo / ".git/devkit.config").write_text("[gates.settings.after-commit]\nenabled = true\n")
    data = _status(repo)  # a warning: the report still exits 0
    assert [g["enabled"] for g in data["gates"] if g["id"] == "after-commit"] == [True]
    assert [(n["code"], n["level"]) for n in data["notices"]] == [("GATE_HOOK_ENTRY_MISSING", "WARNING")]
    assert "post-commit: enabled gates do not run" in data["notices"][0]["message"]
    assert data["notices"][0]["advisory"]["details"] == ["gates=after-commit"]
    result = CliRunner().invoke(cli, ["status", "-w", str(repo)])
    assert result.exit_code == 0 and "[WARN]   (GATE_HOOK_ENTRY_MISSING)" in result.stderr
    assert "devkit gate install" in result.stderr
    assert _invoke("status", "-w", str(repo), "--strict")[0] == 1

    _install(repo)
    assert (repo / ".git/hooks/post-commit.d/20-devkit").is_file() and _status(repo)["notices"] == []


def test_status_warns_for_every_stage_with_gates_before_install(repo: Path) -> None:
    notices = _status(repo)["notices"]
    assert [n["code"] for n in notices] == ["GATE_HOOK_ENTRY_MISSING"] * 2
    assert ["is not a devkit dispatcher (missing)" in n["message"] for n in notices] == [True, True]


def test_status_with_core_hooks_path_warns_with_its_fix_instead_of_install(repo: Path) -> None:
    git(repo, "config", "core.hooksPath", ".husky")  # nothing installed: install would refuse
    notices = _status(repo)["notices"]
    assert [n["code"] for n in notices] == ["GATE_HOOKS_PATH_SET"]
    assert "git config --unset core.hooksPath" in notices[0]["advisory"]["fix"]
    assert _invoke("install", "-w", str(repo), "--python", sys.executable)[0] != 0


def test_post_commit_script_failure_is_rendered_by_the_advisory_library(repo: Path) -> None:
    from devkit_agt.features.gate.models.errors import HookScriptFailedNotice

    _install(repo)
    script = repo / ".git/hooks/post-commit.d/10 fail"
    _script(script, "exit 3\n")
    result = subprocess.run([str(repo / ".git/hooks/post-commit")], cwd=repo, capture_output=True, text=True)
    assert result.returncode == 0
    expected = HookScriptFailedNotice("hook script failed").render()
    assert result.stderr == f"{expected}\n[DETAIL] stage=post-commit script={script} exit=3\n"
