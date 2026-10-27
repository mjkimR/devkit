"""What a first-time consumer sees: hook changes reported by sync, verify-commands setup, the tracked template."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import devkit_agt.features.gate.usecases.hooks.local_config as local_config
from click.testing import CliRunner
from devkit.advisory import ActionMode, AdvisoryError
from devkit_agt.features.gate import GateRefusedError, Stage, load_gate_project
from devkit_agt.features.gate.cli import cli
from devkit_agt.features.gate.usecases.gates.message import NonEmptyMessageGate
from devkit_dist.features.project.services.config_template import render_table, uncomment
from testsupport.gate import gate_ctx


def _lines(result: list[str | AdvisoryError] | None) -> list[str]:
    return [item for item in result or [] if isinstance(item, str)]


def test_post_sync_reports_the_hook_changes_it_made_once(repo: Path) -> None:
    lines = _lines(local_config.post_sync(repo, {}))
    assert len(lines) == 1 and lines[0].startswith("gate hooks: ")
    assert all(f"{stage}: installed" in lines[0] for stage in Stage)
    assert local_config.post_sync(repo, {}) is None


def test_post_sync_preview_reports_planned_changes_without_writing(repo: Path) -> None:
    hook = repo / ".git/hooks/pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text("#!/bin/sh\nexit 0\n")
    hook.chmod(0o755)
    lines = _lines(local_config.post_sync_preview(repo, {}))
    assert len(lines) == 1 and lines[0].startswith("gate hooks would change: ")
    assert "pre-commit: moved existing hook to pre-commit.devkit-preserved" in lines[0]
    assert hook.read_text() == "#!/bin/sh\nexit 0\n" and not (repo / ".git/hooks/pre-commit.d").exists()
    assert not (repo / ".git/devkit.config").exists()
    local_config.post_sync(repo, {})
    assert local_config.post_sync_preview(repo, {}) is None


def test_an_empty_message_tells_the_committer_to_correct_it(repo: Path) -> None:
    message = repo / "MSG"
    message.write_text("  \n")
    try:
        NonEmptyMessageGate().run(gate_ctx(repo, Stage.COMMIT_MSG, str(message)))
    except GateRefusedError as error:
        assert (error.code, error.mode, int(error.exit_code)) == ("GATE_MESSAGE_EMPTY", ActionMode.INPUT_ERROR, 1)
        assert list(error.target_files) == ["MSG"]
    else:
        raise AssertionError("an empty message passed")


def test_status_shows_whether_verify_commands_has_commands(repo: Path) -> None:
    result = CliRunner().invoke(cli, ["status", "-w", str(repo)])
    line = next(line for line in result.stdout.splitlines() if line.startswith("[GATE: verify-commands "))
    assert line.endswith(' setup="commands=0 (skipped: no commands configured)"]')
    (repo / ".devkit").mkdir()
    (repo / ".devkit/config.toml").write_text(
        '[gates.settings.verify-commands]\ncommands = ["just check", "just test"]\n'
    )
    data = json.loads(CliRunner().invoke(cli, ["status", "-w", str(repo), "--format", "json"]).stdout)
    row = next(row for row in data["gates"] if row["id"] == "verify-commands")
    assert row["setup"] == "commands=2"
    assert next(row for row in data["gates"] if row["id"] == "rules-check")["setup"] is None


def test_the_tracked_template_lists_the_built_in_gates_at_their_defaults(repo: Path) -> None:
    tables = local_config.config_tables()
    assert [table.path for table in tables] == [
        ("settings", "rules-check"),
        ("settings", "verify-commands"),
        ("settings", "message-nonempty"),
    ]
    text = "".join(render_table(("gates",), table) for table in tables)
    assert "# [gates.settings.verify-commands]\n" in text and "#   commands = []" in text
    assert tomllib.loads(text) == {}
    (repo / ".devkit").mkdir()
    (repo / ".devkit/config.toml").write_text(uncomment(text))
    project = load_gate_project(repo)
    assert project.validation.errors == ()
    assert all(project.config.enabled(gate) for gate in project.registry.get_all())
    assert project.validation.settings["verify-commands"].commands == []


def test_install_and_uninstall_report_in_text_and_json(repo: Path) -> None:
    installed = CliRunner().invoke(cli, ["install", "-w", str(repo), "--format", "json"])
    assert installed.exit_code == 0, installed.output
    data = json.loads(installed.stdout)
    assert data["hooks"][0] == {"stage": "pre-commit", "action": "installed", "detail": ""}
    assert data["config"] == {"template": "created", "path": ".git/devkit.config"} and data["notices"] == []
    removed = CliRunner().invoke(cli, ["uninstall", "-w", str(repo), "--format", "json"])
    assert {"stage": "pre-commit", "action": "removed", "detail": ""} in json.loads(removed.stdout)["hooks"]
    empty = CliRunner().invoke(cli, ["uninstall", "-w", str(repo)])
    assert empty.stdout == "[OK: no managed hooks]\n"


def test_status_writes_booleans_as_yes_or_no(repo: Path) -> None:
    CliRunner().invoke(cli, ["install", "-w", str(repo)])
    lines = CliRunner().invoke(cli, ["status", "-w", str(repo)]).stdout.splitlines()
    assert "[HOOK: pre-commit state=managed python=" in lines[1] and " python_ok=yes scripts=20-devkit]" in lines[1]
    assert " enabled=yes source=builtin" in next(line for line in lines if line.startswith("[GATE: rules-check "))
    assert "true" not in "\n".join(lines) and "false" not in "\n".join(lines)


def test_commit_msg_without_its_file_names_the_message_file_git_writes(repo: Path) -> None:
    from devkit_core.base.errors import ArgumentError

    try:
        NonEmptyMessageGate().run(gate_ctx(repo, Stage.COMMIT_MSG))
    except ArgumentError as error:
        assert error.fix == f"uv run devkit gate run commit-msg {repo / '.git/COMMIT_EDITMSG'}"
    else:
        raise AssertionError("a commit-msg run without its file passed")
