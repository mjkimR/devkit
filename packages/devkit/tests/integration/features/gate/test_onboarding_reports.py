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
    else:
        raise AssertionError("an empty message passed")


def test_status_shows_whether_verify_commands_has_commands(repo: Path) -> None:
    result = CliRunner().invoke(cli, ["status", "-w", str(repo)])
    line = next(line for line in result.stdout.splitlines() if line.startswith("[GATE: verify-commands "))
    assert line.endswith("commands=0 (skipped: no commands configured)]")
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
