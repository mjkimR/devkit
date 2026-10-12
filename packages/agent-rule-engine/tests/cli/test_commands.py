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


def _write_config(root: Path, body: str) -> None:
    path = root / ".devkit" / "config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _broken_link_workspace(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "a.md").write_text("[broken](missing.md)\n", encoding="utf-8")


def test_cli_phase_override_parks_rule_in_hygiene(tmp_path: Path) -> None:
    _broken_link_workspace(tmp_path)
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-markdown-link = "hygiene"\n')
    runner = CliRunner()

    linter = runner.invoke(cli, ["check", "-w", str(tmp_path)])
    assert linter.exit_code == 0, linter.output
    assert "RULE-markdown-link" not in linter.output.split("passed cleanly")[-1]
    assert "PHASE_OVERRIDE" not in linter.output

    hygiene = runner.invoke(cli, ["check", "-w", str(tmp_path), "--phase", "hygiene"])
    assert hygiene.exit_code == 1
    assert "[PHASE_OVERRIDE: RULE-markdown-link=hygiene default=linter source=.devkit/config.toml remaining=1]" in (
        hygiene.output
    )


def test_cli_phase_override_reports_remaining_zero(tmp_path: Path) -> None:
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-markdown-link = "hygiene"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--phase", "hygiene"])
    assert result.exit_code == 0, result.output
    assert "remaining=0]" in result.output
    assert "drop the override" in result.output


def test_cli_json_output_stays_a_violation_list_with_effective_phase(tmp_path: Path) -> None:
    _broken_link_workspace(tmp_path)
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-markdown-link = "hygiene"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--phase", "hygiene", "--format", "json"])
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    links = [v for v in data if v["rule_id"] == "RULE-markdown-link"]
    assert links and all(v["phase"] == "hygiene" for v in links)


def test_cli_invalid_rules_config_fails(tmp_path: Path) -> None:
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-markdown-link = "linter"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path)])
    assert result.exit_code != 0
    assert "is not 'hygiene'" in result.output


def test_cli_override_for_unknown_rule_fails(tmp_path: Path) -> None:
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-nope = "hygiene"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--format", "json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout) == []
    assert "unknown rule: RULE-nope" in result.stderr


def test_cli_promotion_reported_for_custom_hygiene_rule(tmp_path: Path) -> None:
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "todo.py").write_text("""from agent_rule_engine import Phase, RuleContext, Severity, Violation
from agent_rule_engine.rules import BaseRule


class NoTodoRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-no-todo",
            name="no-todo",
            description="TODO markers are debt",
            phase=Phase.HYGIENE,
            severity=Severity.WARNING,
            promote_to=Phase.LINTER,
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        out = []
        for p in ctx.cache.find_files(ctx.workspace_root, extensions=(".md",)):
            if "TODO" in ctx.cache.read_text(p):
                rel = p.relative_to(ctx.workspace_root).as_posix()
                out.append(Violation(self.id, rel, 1, "TODO found", severity=self.severity, phase=self.phase))
        return out
""")
    (tmp_path / "notes.md").write_text("TODO later\n")
    runner = CliRunner()

    linter = runner.invoke(cli, ["check", "-w", str(tmp_path), "--rules-dir", str(rules)])
    assert linter.exit_code == 0
    assert "PROMOTION" not in linter.output

    hygiene = runner.invoke(cli, ["check", "-w", str(tmp_path), "--rules-dir", str(rules), "--phase", "hygiene"])
    assert hygiene.exit_code == 0  # warnings do not fail
    assert "[PROMOTION: RULE-no-todo=hygiene promote_to=linter remaining=1]" in hygiene.output


def test_cli_phases_command_text_and_json(tmp_path: Path) -> None:
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-markdown-link = "hygiene"\n')
    runner = CliRunner()

    text = runner.invoke(cli, ["phases", "-w", str(tmp_path)])
    assert text.exit_code == 0, text.output
    assert "RULE-markdown-link" in text.output and "override -> linter" in text.output

    as_json = runner.invoke(cli, ["phases", "-w", str(tmp_path), "--format", "json"])
    data = {e["rule_id"]: e for e in json.loads(as_json.stdout)}
    assert data["RULE-markdown-link"] == {
        "rule_id": "RULE-markdown-link",
        "default_phase": "linter",
        "effective_phase": "hygiene",
        "overridden": True,
        "promote_to": None,
    }
    assert data["RULE-file-length"]["effective_phase"] == "hygiene"
    assert data["RULE-file-length"]["overridden"] is False


def test_cli_phases_command_flags_unknown_override(tmp_path: Path) -> None:
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-nope = "hygiene"\n')
    result = CliRunner().invoke(cli, ["phases", "-w", str(tmp_path)])
    assert result.exit_code == 1
    assert "unknown rule: RULE-nope" in result.stderr
