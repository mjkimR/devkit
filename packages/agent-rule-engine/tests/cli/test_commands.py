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


# --- settings, severity overrides, guides, explain --------------------------


def _long_doc(root: Path, rel: str, lines: int) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"line {i}" for i in range(lines)) + "\n", encoding="utf-8")


def test_cli_settings_override_by_path_and_guide_line(tmp_path: Path) -> None:
    _long_doc(tmp_path, "docs/a.md", 50)
    _long_doc(tmp_path, "docs/research/b.md", 50)
    _write_config(
        tmp_path,
        "[rules.settings.RULE-file-length]\nmax_lines = 30\n"
        "[[rules.settings.RULE-file-length.overrides]]\npath = 'docs/research/**'\nmax_lines = 100\n",
    )
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--phase", "hygiene"])
    assert result.exit_code == 0, result.output
    assert "docs/a.md:31" in result.output and "docs/research/b.md" not in result.output
    assert "Guide: " in result.output and "file_length.md" in result.output


def test_cli_invalid_settings_fail_before_checks(tmp_path: Path) -> None:
    _write_config(tmp_path, "[rules.settings.RULE-file-length]\nmax_lines = 'many'\n")
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--format", "json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout) == []
    assert "RULE-file-length: settings.max_lines: expected integer" in result.stderr


def test_cli_severity_override_turns_warning_into_error(tmp_path: Path) -> None:
    _long_doc(tmp_path, "docs/a.md", 500)
    _write_config(tmp_path, '[rules.severity_overrides]\nRULE-file-length = "error"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--phase", "hygiene"])
    assert result.exit_code == 1
    assert "[ERROR] RULE-file-length" in result.output


def test_cli_explain_text_and_json(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        '[rules.severity_overrides]\nRULE-file-length = "error"\n'
        "[rules.settings.RULE-file-length]\nmax_lines = 300\n"
        "[[rules.settings.RULE-file-length.overrides]]\npath = 'docs/**'\nmax_lines = 800\n",
    )
    runner = CliRunner()
    text = runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-file-length"])
    assert text.exit_code == 0, text.output
    assert "Severity: warning (effective error)" in text.output
    assert "max_lines = 300 (default 400)" in text.output
    assert "[docs/**] max_lines = 800" in text.output
    assert "# [RULE-file-length]" in text.output

    as_json = runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-file-length", "--format", "json"])
    data = json.loads(as_json.stdout)
    assert data["effective_severity"] == "error" and data["settings"]["settings"]["max_lines"] == 300
    assert data["settings"]["overrides"] == [{"path": "docs/**", "max_lines": 800}]

    unknown = runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-nope"])
    assert unknown.exit_code == 1 and "unknown rule: RULE-nope" in unknown.stderr

    plain = runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-markdown-link"])
    assert plain.exit_code == 0 and "Settings: none" in plain.output


# --- synchronized rule assets -----------------------------------------------


def test_cli_loads_rules_recorded_in_installation_receipt(tmp_path: Path) -> None:
    rules_dir = tmp_path / ".devkit/managed/team/rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "no_todo.py").write_text("""from agent_rule_engine import RuleContext, Violation
from agent_rule_engine.rules import BaseRule


class NoTodoRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-no-todo", name="no-todo", description="no TODO")

    def check(self, ctx: RuleContext) -> list[Violation]:
        out = []
        for p in ctx.cache.find_files(ctx.workspace_root, extensions=(".md",)):
            if "TODO" in ctx.cache.read_text(p):
                out.append(Violation(self.id, p.relative_to(ctx.workspace_root).as_posix(), 1, "TODO found"))
        return out
""")
    (tmp_path / ".devkit/installation.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "assets": [
                    {
                        "bundle": "team",
                        "id": "rules",
                        "kind": "rule",
                        "paths": [".devkit/managed/team/rules/no_todo.py"],
                    }
                ],
            }
        )
    )
    (tmp_path / "notes.md").write_text("TODO\n")
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--format", "json"])
    assert result.exit_code == 1
    assert [v["rule_id"] for v in json.loads(result.stdout)] == ["RULE-no-todo"]
    phases = CliRunner().invoke(cli, ["phases", "-w", str(tmp_path)])
    assert "RULE-no-todo" in phases.output


# --- git snapshot gates -----------------------------------------------------


def _git(root: Path, *args: str) -> str:
    import subprocess

    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    (root / "README.md").write_text("# Repo\n")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "init")
    return root


def test_cli_staged_gate_sees_only_the_index(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "docs").mkdir()
    (root / "docs/a.md").write_text("[ok](../README.md)\n")
    _git(root, "add", "docs")
    (root / "docs/a.md").write_text("[broken](missing.md)\n")  # unstaged breakage is invisible
    (root / ".env").write_text("SECRET=1\n")  # untracked, never in the snapshot

    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged"])
    assert result.exit_code == 0, result.output
    assert "[SNAPSHOT: mode=staged" in result.output and "changed=1" in result.output
    assert "passed cleanly" in result.output

    _git(root, "add", "docs")
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--format", "json"])
    assert result.exit_code == 1
    assert [v["rule_id"] for v in json.loads(result.stdout)] == ["RULE-markdown-link"]


def test_cli_staged_gate_runs_safety_rules_and_reads_snapshot_config(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "secrets.txt").write_text("-----BEGIN RSA PRIVATE KEY-----\n")
    (root / "app.db").write_bytes(b"x")
    _git(root, "add", "-f", "secrets.txt", "app.db")
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--format", "json"])
    assert result.exit_code == 1
    assert sorted(v["rule_id"] for v in json.loads(result.stdout)) == ["RULE-clean-artifacts", "RULE-secret-leak"]

    # Policy comes from the snapshot: an unstaged config edit does not apply.
    _write_config(root, '[rules.severity_overrides]\nRULE-secret-leak = "warning"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--format", "json"])
    assert all(v["severity"] == "error" for v in json.loads(result.stdout))
    _git(root, "add", ".devkit")
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--format", "json"])
    secret = [v for v in json.loads(result.stdout) if v["rule_id"] == "RULE-secret-leak"]
    assert secret and secret[0]["severity"] == "warning"


def test_cli_staged_gate_with_nothing_staged(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged"])
    assert result.exit_code == 0 and "nothing to check" in result.output
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--format", "json"])
    assert result.exit_code == 0 and json.loads(result.stdout) == []


def test_cli_ci_gate_uses_base_ref(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _git(root, "checkout", "-q", "-b", "feature")
    (root / "docs").mkdir()
    (root / "docs/a.md").write_text("[broken](missing.md)\n")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "feature")
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--ci", "--base", "main", "--format", "json"])
    assert result.exit_code == 1
    assert [v["file"] for v in json.loads(result.stdout)] == ["docs/a.md"]


def test_cli_snapshot_flag_validation(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    runner = CliRunner()
    assert runner.invoke(cli, ["check", "-w", str(root), "--staged", "--ci"]).exit_code == 2
    assert runner.invoke(cli, ["check", "-w", str(root), "--staged", "README.md"]).exit_code == 2
    assert runner.invoke(cli, ["check", "-w", str(root), "--staged", "--phase", "hygiene"]).exit_code == 2
    outside = runner.invoke(cli, ["check", "-w", str(tmp_path), "--staged"])
    assert outside.exit_code == 1 and "git write-tree failed" in outside.output


NO_TODO_RULE = """from agent_rule_engine import RuleContext, Violation
from agent_rule_engine.rules import BaseRule


class NoTodoRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-no-todo", name="no-todo", description="no TODO")

    def check(self, ctx: RuleContext) -> list[Violation]:
        out = []
        for p in ctx.cache.find_files(ctx.workspace_root, extensions=(".md",)):
            if "TODO" in ctx.cache.read_text(p):
                out.append(Violation(self.id, p.relative_to(ctx.workspace_root).as_posix(), 1, "TODO found"))
        return out
"""


def _managed_rule_repo(tmp_path: Path) -> Path:
    """A repo whose committed receipt lists a managed rule while ``.devkit/managed/`` is Git-ignored."""
    import hashlib

    root = _repo(tmp_path)
    (root / ".gitignore").write_text(".devkit/managed/\n")
    rule_path = ".devkit/managed/team/rules/no_todo.py"
    (root / rule_path).parent.mkdir(parents=True)
    (root / rule_path).write_text(NO_TODO_RULE)
    (root / ".devkit/installation.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "assets": [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [rule_path]}],
                "files": {rule_path: {"sha256": hashlib.sha256(NO_TODO_RULE.encode()).hexdigest(), "mode": 420}},
            }
        )
    )
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "devkit sync")
    assert ".devkit/managed" not in _git(root, "ls-files")
    return root


def test_cli_staged_gate_loads_ignored_managed_rules_pinned_by_the_receipt(tmp_path: Path) -> None:
    root = _managed_rule_repo(tmp_path)
    (root / "notes.md").write_text("TODO\n")
    _git(root, "add", "notes.md")
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--format", "json"])
    assert result.exit_code == 1, result.output
    assert [v["rule_id"] for v in json.loads(result.stdout)] == ["RULE-no-todo"]


def test_cli_staged_gate_rejects_managed_rule_that_drifted_from_the_receipt(tmp_path: Path) -> None:
    root = _managed_rule_repo(tmp_path)
    (root / "notes.md").write_text("fine\n")
    _git(root, "add", "notes.md")
    (root / ".devkit/managed/team/rules/no_todo.py").write_text(NO_TODO_RULE + "\n# edited\n")
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged"])
    assert result.exit_code == 1
    assert "differs from the hash in the receipt" in result.stderr
    (root / ".devkit/managed/team/rules/no_todo.py").unlink()
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged"])
    assert result.exit_code == 1
    assert "missing from the working tree" in result.stderr


def test_cli_missing_managed_rule_fails_in_working_tree_check(tmp_path: Path) -> None:
    (tmp_path / ".devkit").mkdir()
    (tmp_path / ".devkit/installation.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "assets": [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [".devkit/managed/team/r.py"]}],
            }
        )
    )
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path)])
    assert result.exit_code == 1
    assert "synchronized rule .devkit/managed/team/r.py is missing" in result.stderr
