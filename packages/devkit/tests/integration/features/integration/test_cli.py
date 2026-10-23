from __future__ import annotations

import json
import tomllib
from pathlib import Path

from click.testing import CliRunner
from devkit_agt.features.integration.cli import cli


def test_lifecycle_mcp_service_registration_is_removed():
    pyproject = Path(__file__).resolve().parents[4] / "pyproject.toml"
    entries = tomllib.loads(pyproject.read_text("utf-8"))["project"].get("entry-points", {})
    assert "devkit.host.services" not in entries


def test_integrate_cli_executes_after_host_conversation(repo):
    base, worktree = repo
    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--workspace-root",
            str(base),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "completed"
    assert payload["authority"] == "host-conversation"
    assert not worktree.exists()


def test_integrate_cli_reads_automatic_authority_from_base(repo):
    base, worktree = repo
    config = base / ".devkit/config.toml"
    config.write_text(config.read_text() + '\n[workflow.approvals]\ndev-integration = "auto"\n')
    from testsupport.rules import git

    git(base, "add", ".devkit/config.toml")
    git(base, "commit", "-qm", "enable automatic integration")
    # The source worktree follows the configured base before the operation is prepared.
    git(worktree, "merge", "-q", "main")
    result = CliRunner().invoke(
        cli,
        [
            "integrate",
            "dev-demo",
            "--task-kind",
            "session",
            "--task-id",
            "fixture",
            "--workspace-root",
            str(base),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["authority"] == "policy"
    assert not worktree.exists()
