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


def test_cli_plugin_failure_preserves_json_and_fails(tmp_path: Path) -> None:
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "broken.py").write_text('raise RuntimeError("broken plugin")\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--rules-dir", str(rules), "--format", "json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout) == []
    assert "broken plugin" in result.stderr
    assert "passed cleanly" not in result.stdout


def test_cli_malformed_frontmatter_is_not_overwritten(tmp_path: Path) -> None:
    docs = tmp_path / "docs/stories"
    docs.mkdir(parents=True)
    doc = docs / "US-invalid.md"
    original = "---\nid: [invalid\n---\n# Keep this content\n"
    doc.write_text(original)
    result = CliRunner().invoke(cli, ["fix", "-w", str(tmp_path)])
    assert result.exit_code == 1
    assert "Invalid YAML frontmatter" in result.stderr
    assert "passed cleanly" not in result.stdout
    assert doc.read_text() == original


def test_cli_dry_run_does_not_modify_file(tmp_path: Path) -> None:
    docs = tmp_path / "specs"
    docs.mkdir()
    doc = docs / "SPEC-example.md"
    original = "# Example\n"
    doc.write_text(original)
    result = CliRunner().invoke(cli, ["fix", "-w", str(tmp_path), "--dry-run"])
    assert result.exit_code == 1
    assert "FIXABLE" in result.stdout
    assert doc.read_text() == original
