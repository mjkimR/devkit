from __future__ import annotations

import json
from pathlib import Path

from agent_rule_engine.cli import cli
from click.testing import CliRunner


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Agent-managed rule engine" in result.output


def test_cli_rules_check_clean(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "--workspace-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "All governance checks passed cleanly" in result.output


def test_cli_rules_check_json_output(tmp_path: Path) -> None:
    stories_dir = tmp_path / "docs" / "stories"
    stories_dir.mkdir(parents=True)
    doc = stories_dir / "US-sample.md"
    doc.write_text("# Sample Story\n\nNo frontmatter here.", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["check", "--workspace-root", str(tmp_path), "--format", "json"])
    assert result.exit_code == 1  # Fails due to violation

    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["rule_id"] == "RULE-spec-format"


def test_cli_rules_fix(tmp_path: Path) -> None:
    stories_dir = tmp_path / "docs" / "stories"
    stories_dir.mkdir(parents=True)
    doc = stories_dir / "US-fixable.md"
    doc.write_text("# Fixable Story\n\nContent.", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["fix", "--workspace-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "FIXED" in result.output
