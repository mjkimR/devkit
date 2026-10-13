from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import ExitCode
from devkit.gate import load_gate_project, run_hook
from devkit.gate.cli import cli
from devkit.gate.engine.models import Stage
from devkit.gate.hooks import hooks
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
    assert all(s.state is hooks.HookState.MANAGED and s.python_ok for s in states.values())
    script = (repo / ".git/hooks/pre-commit").read_text()
    assert hooks.MARKER in script and "-P -m devkit.gate run pre-commit" in script

    data = _status(repo)
    assert [h["state"] for h in data["hooks"]] == ["managed"] * 3
    assert [g["id"] for g in data["gates"]] == ["rules-staged", "message-nonempty"] and data["config_sources"] == []
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
    data = (repo / ".git/hooks/pre-commit").read_bytes()
    assert b"\r" not in data
    # Absolute, with the venv's interpreter symlink kept rather than resolved.
    assert hooks._read_python(data.decode()) == Path(os.path.abspath(sys.executable)).as_posix()
    assert all(item.python_ok for item in hooks.status(repo))


def test_install_refuses_an_interpreter_without_devkit(repo: Path, tmp_path: Path) -> None:
    code, output = _invoke("install", "-w", str(repo), "--python", str(tmp_path / "gone/python"))
    assert code != 0 and "GATE_PYTHON_INVALID" in output and "not an executable file" in output

    fake = tmp_path / "fake-python"
    fake.write_text("#!/bin/sh\necho 'No module named devkit' >&2\nexit 1\n")
    fake.chmod(0o755)
    code, output = _invoke("install", "-w", str(repo), "--python", str(fake))
    assert code != 0 and "cannot import devkit.gate" in output and "No module named devkit" in output
    assert not (repo / ".git/hooks/pre-commit").exists()


def test_foreign_hooks_need_force_keep_running_and_are_restored(repo: Path) -> None:
    foreign = repo / ".git/hooks/pre-commit"
    foreign.write_text("#!/bin/sh\necho previous-hook-ran\nexit 0\n")
    foreign.chmod(0o755)
    code, output = _invoke("install", "-w", str(repo), "--python", sys.executable)
    assert code != 0 and "GATE_FOREIGN_HOOK" in output
    assert "previous-hook-ran" in foreign.read_text()

    _install(repo, "--force")
    assert "previous-hook-ran" in (repo / ".git/hooks/pre-commit.pre-gate").read_text()
    code, output = _commit(repo, "-m", "feat: chained")
    assert code == 0 and "previous-hook-ran" in output, output

    _invoke("uninstall", "-w", str(repo))
    assert "previous-hook-ran" in foreign.read_text() and not (repo / ".git/hooks/pre-commit.pre-gate").exists()


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
    data = _status(repo)
    assert data["hooks_path"] == ".husky" and [h["state"] for h in data["hooks"]] == ["managed"] * 3
    code, output = _invoke("status", "-w", str(repo))
    assert "core.hooksPath=.husky (wrappers do not run)" in output
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
    assert (repo / ".git/hooks/pre-commit.pre-gate").is_dir()
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


def test_repository_modules_do_not_shadow_the_hook(repo: Path) -> None:
    _install(repo)
    (repo / "json.py").write_text("raise SystemExit('repository json.py was imported')\n")
    code, output = _commit(repo, "-m", "feat: add json.py", name="json.py")
    assert code == 0, output


def test_wrapper_without_interpreter(repo: Path, tmp_path: Path) -> None:
    directory = repo / ".git/hooks"
    for stage in Stage:
        (directory / stage.value).write_text(hooks.wrapper_script(stage, (tmp_path / "gone/python").as_posix()))
        (directory / stage.value).chmod(0o755)
    code, output = _commit(repo, "-m", "feat: x")
    assert code != 0 and "no interpreter with devkit found" in output
    # Blocking stages exit 2 (the gates could not run); post-commit is not blocking and exits 0.
    assert "    exit 2\n" in (directory / "pre-commit").read_text()
    assert "    exit 0\n" in (directory / "post-commit").read_text()


def test_wrapper_probes_only_the_posix_venv_layout() -> None:
    script = hooks.wrapper_script(Stage.PRE_COMMIT, PYTHON)
    assert "Scripts" not in script and ".exe" not in script and "/Lib/" not in script
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

    (venv / "lib/python3.12/site-packages/devkit-0.1.0.dist-info").mkdir(parents=True)
    code, output = _commit(repo, "-m", "feat: venv with devkit")
    assert code == 0 and marker.exists(), output


def test_commit_all_and_partial_commits_check_what_is_committed(repo: Path) -> None:
    (repo / "README.md").write_text("# Repo\n")
    (repo / "a.md").write_text("[ok](README.md)\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "init")
    _install(repo)

    (repo / "a.md").write_text("[bad](missing.md)\n")
    result = git(repo, "commit", "-am", "feat: all", check=False)
    assert result.returncode != 0 and "GATE_RULES_VIOLATION" in result.stderr
    result = git(repo, "commit", "-m", "feat: partial", "a.md", check=False)
    assert result.returncode != 0 and "GATE_RULES_VIOLATION" in result.stderr

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
    assert code == 0 and "[INFO]   gate.engine.runner: gate message-nonempty stage=commit-msg outcome=passed" in output
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


def test_rule_engine_errors_pass_through_the_staged_gate(repo: Path) -> None:
    (repo / ".devkit").mkdir()
    (repo / ".devkit/config.toml").write_text("[rules]\nexclude = 3\n")
    (repo / "a.md").write_text("# a\n")
    git(repo, "add", ".")
    code, output = _invoke("run", "-w", str(repo), "pre-commit")
    assert code == 2 and "[DETAIL] gate=rules-staged stage=pre-commit" in output
    assert "(RULES_CONFIG_INVALID)" in output and "GATE_RULES" not in output


def test_library_entry_points(repo: Path) -> None:
    (repo / "sub").mkdir()
    project = load_gate_project(repo / "sub")
    assert project.root == repo and project.common_git_dir == (repo / ".git").resolve()
    assert project.validation.ok and project.config.sources == ()
    assert [g.id for g in project.registry.get_all()] == ["rules-staged", "message-nonempty"]

    (repo / "MSG").write_text("\n")
    report = run_hook(repo, Stage.COMMIT_MSG, ["MSG"])
    assert not report.ok and report.exit_code is ExitCode.FINDINGS
    assert [e.code for e in report.problems] == ["GATE_MESSAGE_EMPTY"]

    report = run_hook(repo, Stage.COMMIT_MSG)
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
