from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.rules.cli import cli
from testsupport.rules import write_receipt


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
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("[missing](nowhere.md)\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli, ["check", "--workspace-root", str(tmp_path), "--format", "json"])
    assert result.exit_code == 1  # Fails due to violation

    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["rule_id"] == "RULE-markdown-link"


def _fixable_link_workspace(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    (docs / "guides").mkdir(parents=True)
    (docs / "guides" / "setup.md").write_text("# Setup\n", encoding="utf-8")
    source = docs / "index.md"
    source.write_text("[setup](wrong/setup.md)\n", encoding="utf-8")
    return source


def test_cli_rules_fix(tmp_path: Path) -> None:
    source = _fixable_link_workspace(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["fix", "--workspace-root", str(tmp_path)])
    assert result.exit_code == 0
    assert "FIXED" in result.output
    assert source.read_text(encoding="utf-8") == "[setup](guides/setup.md)\n"


def test_cli_plugin_failure_preserves_json_and_fails(tmp_path: Path) -> None:
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "broken.py").write_text('raise RuntimeError("broken plugin")\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--rules-dir", str(rules), "--format", "json"])
    assert result.exit_code == 2
    assert json.loads(result.stdout) == []
    assert "broken plugin" in result.stderr
    assert "passed cleanly" not in result.stdout


def test_cli_malformed_frontmatter_elsewhere_neither_blocks_nor_gets_rewritten(tmp_path: Path) -> None:
    # The link rule needs only the basename index; a malformed document is left alone.
    source = _fixable_link_workspace(tmp_path)
    doc = tmp_path / "docs" / "invalid.md"
    original = "---\nid: [invalid\n---\n# Keep this content\n"
    doc.write_text(original)
    result = CliRunner().invoke(cli, ["fix", "-w", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert doc.read_text() == original
    assert source.read_text(encoding="utf-8") == "[setup](guides/setup.md)\n"


def test_cli_dry_run_does_not_modify_file(tmp_path: Path) -> None:
    source = _fixable_link_workspace(tmp_path)
    original = source.read_text(encoding="utf-8")
    result = CliRunner().invoke(cli, ["fix", "-w", str(tmp_path), "--dry-run"])
    assert result.exit_code == 1
    assert "FIXABLE" in result.stdout
    assert source.read_text(encoding="utf-8") == original


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
    assert result.exit_code == 2
    assert "is not 'hygiene'" in result.output


def test_cli_override_for_unknown_rule_fails(tmp_path: Path) -> None:
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-nope = "hygiene"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--format", "json"])
    assert result.exit_code == 2
    assert json.loads(result.stdout) == []
    assert "unknown rule: RULE-nope" in result.stderr


def test_cli_promotion_reported_for_custom_hygiene_rule(tmp_path: Path) -> None:
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "todo.py").write_text("""from devkit.rules import Phase, RuleContext, Severity, Violation
from devkit.rules.rules import BaseRule


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
    assert result.exit_code == 2
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
    assert result.exit_code == 2
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
    assert unknown.exit_code == 2 and "unknown rule: RULE-nope" in unknown.stderr

    plain = runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-markdown-link"])
    assert plain.exit_code == 0 and "Settings: none" in plain.output


# --- synchronized rule assets -----------------------------------------------


def test_cli_loads_rules_recorded_in_installation_receipt(tmp_path: Path) -> None:
    rules_dir = tmp_path / ".devkit/managed/team/rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "no_todo.py").write_text("""from devkit.rules import RuleContext, Violation
from devkit.rules.rules import BaseRule


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
    write_receipt(
        tmp_path,
        [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [".devkit/managed/team/rules/no_todo.py"]}],
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
    both = runner.invoke(cli, ["check", "-w", str(root), "--staged", "--ci"])
    assert both.exit_code == 2 and "mutually exclusive" in both.stderr
    with_file = runner.invoke(cli, ["check", "-w", str(root), "--staged", "README.md"])
    assert with_file.exit_code == 2 and "without file arguments" in with_file.stderr
    hygiene = runner.invoke(cli, ["check", "-w", str(root), "--staged", "--phase", "hygiene"])
    assert hygiene.exit_code == 2 and "without file arguments" in hygiene.stderr
    outside = runner.invoke(cli, ["check", "-w", str(tmp_path), "--staged"])
    assert outside.exit_code == 2 and "not inside a Git work tree" in outside.output
    assert "Usage:" not in outside.output  # an evaluation failure, not a usage error


NO_TODO_RULE = """from devkit.rules import RuleContext, Violation
from devkit.rules.rules import BaseRule


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
    write_receipt(
        root,
        [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [rule_path]}],
        {rule_path: hashlib.sha256(NO_TODO_RULE.encode()).hexdigest()},
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
    assert result.exit_code == 2
    assert "differs from the hash in the receipt" in result.stderr
    (root / ".devkit/managed/team/rules/no_todo.py").unlink()
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged"])
    assert result.exit_code == 2
    assert "missing from the working tree" in result.stderr


def test_cli_missing_managed_rule_fails_in_working_tree_check(tmp_path: Path) -> None:
    write_receipt(tmp_path, [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [".devkit/managed/team/r.py"]}])
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path)])
    assert result.exit_code == 2
    assert "synchronized rule .devkit/managed/team/r.py is missing" in result.stderr


# --- directory targets, exclusions, summary-only, exit codes ---------------


def _two_broken_docs(root: Path) -> None:
    (root / "docs/research").mkdir(parents=True)
    (root / "docs/a.md").write_text("[broken](missing.md)\n", encoding="utf-8")
    (root / "docs/research/b.md").write_text("[broken](missing.md)\n", encoding="utf-8")
    (root / "README.md").write_text("[broken](missing.md)\n", encoding="utf-8")


def test_cli_directory_target_expands_recursively(tmp_path: Path) -> None:
    _two_broken_docs(tmp_path)
    (tmp_path / "docs/node_modules").mkdir()
    (tmp_path / "docs/node_modules/ignored.md").write_text("[broken](missing.md)\n", encoding="utf-8")
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--format", "json", "docs"])
    assert result.exit_code == 1
    assert sorted(v["file"] for v in json.loads(result.stdout)) == ["docs/a.md", "docs/research/b.md"]

    mixed = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--format", "json", "docs/research", "README.md"])
    assert sorted(v["file"] for v in json.loads(mixed.stdout)) == ["README.md", "docs/research/b.md"]


def test_cli_invalid_target_fails_before_evaluation(tmp_path: Path) -> None:
    _two_broken_docs(tmp_path)
    runner = CliRunner()
    missing = runner.invoke(cli, ["check", "-w", str(tmp_path), "docs/nope.md"])
    assert missing.exit_code == 2
    assert "(RULES_TARGET_INVALID)" in missing.stderr and "docs/nope.md" in missing.stderr
    assert "broken" not in missing.stdout

    outside = runner.invoke(cli, ["check", "-w", str(tmp_path), "../elsewhere"])
    assert outside.exit_code == 2 and "(RULES_TARGET_INVALID)" in outside.stderr

    fixed = runner.invoke(cli, ["fix", "-w", str(tmp_path), "--dry-run", "docs/nope"])
    assert fixed.exit_code == 2 and "(RULES_TARGET_INVALID)" in fixed.stderr


def test_cli_target_directory_without_files_checks_nothing(tmp_path: Path) -> None:
    _two_broken_docs(tmp_path)
    (tmp_path / "empty").mkdir()
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--format", "json", "empty"])
    assert result.exit_code == 0 and json.loads(result.stdout) == []


def test_cli_exclude_patterns_drop_files_from_targets_and_scans(tmp_path: Path) -> None:
    _two_broken_docs(tmp_path)
    _write_config(tmp_path, '[rules]\nexclude = ["docs/research/**"]\n')
    runner = CliRunner()

    whole = runner.invoke(cli, ["check", "-w", str(tmp_path), "--format", "json"])
    assert sorted(v["file"] for v in json.loads(whole.stdout)) == ["README.md", "docs/a.md"]

    directory = runner.invoke(cli, ["check", "-w", str(tmp_path), "--format", "json", "docs"])
    assert [v["file"] for v in json.loads(directory.stdout)] == ["docs/a.md"]

    explicit = runner.invoke(cli, ["check", "-w", str(tmp_path), "--format", "json", "docs/research/b.md"])
    assert explicit.exit_code == 0 and json.loads(explicit.stdout) == []


def test_cli_excluded_files_remain_link_repair_candidates(tmp_path: Path) -> None:
    (tmp_path / "docs/research").mkdir(parents=True)
    (tmp_path / "docs/research/target.md").write_text("# Target\n", encoding="utf-8")
    (tmp_path / "docs/a.md").write_text("[t](wrong/target.md)\n", encoding="utf-8")
    _write_config(tmp_path, '[rules]\nexclude = ["docs/research/**"]\n')
    result = CliRunner().invoke(cli, ["fix", "-w", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "docs/a.md").read_text(encoding="utf-8") == "[t](research/target.md)\n"


def test_cli_invalid_exclude_pattern_fails_before_rules(tmp_path: Path) -> None:
    _two_broken_docs(tmp_path)
    _write_config(tmp_path, '[rules]\nexclude = ["/docs/**"]\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--format", "json"])
    assert result.exit_code == 2
    assert "exclude[0]" in result.stderr
    assert "broken" not in result.stdout


def test_cli_summary_only_prints_counts_not_findings(tmp_path: Path) -> None:
    _two_broken_docs(tmp_path)
    _long_doc(tmp_path, "docs/long.md", 500)
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "-w", str(tmp_path), "--phase", "hygiene", "--summary-only"])
    assert result.exit_code == 1
    assert "RULE-markdown-link: 3 error(s), 0 warning(s)" in result.output
    assert "RULE-file-length: 0 error(s), 1 warning(s)" in result.output
    assert "Summary: 3 error(s), 1 warning(s)" in result.output
    assert "Message:" not in result.output and "docs/a.md" not in result.output

    _fixable_link_workspace(tmp_path / "other")
    fixed = runner.invoke(cli, ["fix", "-w", str(tmp_path / "other"), "--summary-only"])
    assert fixed.exit_code == 0, fixed.output
    assert "RULE-markdown-link: 0 error(s), 0 warning(s), 1 fixed" in fixed.output
    assert "[FIXED]" not in fixed.output

    clean = runner.invoke(cli, ["check", "-w", str(tmp_path / "other"), "--summary-only"])
    assert clean.exit_code == 0 and "passed cleanly" in clean.output

    as_json = runner.invoke(cli, ["check", "-w", str(tmp_path), "--summary-only", "--format", "json"])
    assert len(json.loads(as_json.stdout)) == 3  # JSON ignores the flag


def test_cli_summary_only_keeps_sentinel_lines(tmp_path: Path) -> None:
    _broken_link_workspace(tmp_path)
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-markdown-link = "hygiene"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--phase", "hygiene", "--summary-only"])
    assert "[PHASE_OVERRIDE: RULE-markdown-link=hygiene" in result.output
    assert "RULE-markdown-link: 1 error(s), 0 warning(s)" in result.output

    (tmp_path / "repo-dir").mkdir()
    root = _repo(tmp_path / "repo-dir")
    (root / "docs").mkdir()
    (root / "docs/a.md").write_text("[broken](missing.md)\n")
    _git(root, "add", "docs")
    staged = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--summary-only"])
    assert staged.exit_code == 1
    assert "[SNAPSHOT: mode=staged" in staged.output and "Message:" not in staged.output


def test_cli_exit_codes_distinguish_violations_from_failures(tmp_path: Path) -> None:
    _broken_link_workspace(tmp_path)
    runner = CliRunner()
    assert runner.invoke(cli, ["check", "-w", str(tmp_path)]).exit_code == 1  # unresolved violations
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "boom.py").write_text("""from devkit.rules.rules import BaseRule


class Boom(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-boom", name="boom", description="raises")

    def check(self, ctx):
        raise RuntimeError("boom")
""")
    failed = runner.invoke(cli, ["check", "-w", str(tmp_path), "--rules-dir", str(rules)])
    assert failed.exit_code == 2  # execution error, even though violations also exist
    assert "Rule execution error (RULE-boom)" in failed.stderr


# --- project root, snapshot root and rules directories -----------------------


def test_cli_defaults_to_the_project_root_of_the_current_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".devkit").mkdir()
    (tmp_path / "README.md").write_text("[broken](missing.md)\n")
    (tmp_path / "docs/deep").mkdir(parents=True)
    monkeypatch.chdir(tmp_path / "docs/deep")
    result = CliRunner().invoke(cli, ["check", "--format", "json"])
    assert result.exit_code == 1
    assert [v["file"] for v in json.loads(result.stdout)] == ["README.md"]


def test_cli_snapshot_requires_the_repository_top_level(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _repo(tmp_path)
    (root / "pkg").mkdir()
    (root / "pkg/a.md").write_text("[broken](missing.md)\n")
    _git(root, "add", "pkg")
    explicit = CliRunner().invoke(cli, ["check", "-w", str(root / "pkg"), "--staged"])
    assert explicit.exit_code == 2 and "top level" in explicit.output
    # Without -w the project root (here the repository top level) is used, from any subdirectory.
    monkeypatch.chdir(root / "pkg")
    implicit = CliRunner().invoke(cli, ["check", "--staged", "--format", "json"])
    assert implicit.exit_code == 1
    assert [v["file"] for v in json.loads(implicit.stdout)] == ["pkg/a.md"]


def test_cli_base_requires_ci(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--base", "main"])
    assert result.exit_code == 2 and "--base applies to --ci only" in result.stderr


def test_cli_staged_gate_resolves_links_to_tracked_symlinks(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "docs").mkdir()
    (root / "docs/v2.md").write_text("# v2\n")
    (root / "docs/latest.md").symlink_to("v2.md")
    (root / "a.md").write_text("[latest](docs/latest.md)\n")
    _git(root, "add", ".")
    assert CliRunner().invoke(cli, ["check", "-w", str(root), "a.md"]).exit_code == 0
    staged = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged"])
    assert staged.exit_code == 0, staged.output


def test_cli_snapshot_rules_dir_must_be_in_the_repository(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    outside = tmp_path / "outside-rules"
    outside.mkdir()
    (root / "a.md").write_text("x\n")
    _git(root, "add", "a.md")
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--rules-dir", str(outside)])
    assert result.exit_code == 2 and "outside the repository" in result.output


# --- output -------------------------------------------------------------------


def test_cli_info_findings_are_counted(tmp_path: Path) -> None:
    _broken_link_workspace(tmp_path)
    _write_config(tmp_path, '[rules.severity_overrides]\nRULE-markdown-link = "info"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path)])
    assert result.exit_code == 0
    assert "[INFO] RULE-markdown-link" in result.output and "Summary: 1 info(s)" in result.output
    summary = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--summary-only"])
    assert "RULE-markdown-link: 0 error(s), 0 warning(s), 1 info(s)" in summary.output


def test_cli_errors_without_findings_print_no_empty_summary(tmp_path: Path) -> None:
    _write_config(tmp_path, '[rules.severity_overrides]\nRULE-nope = "warning"\n')
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path)])
    assert result.exit_code == 2
    assert "Summary" not in result.output and "passed cleanly" not in result.output
    assert "severity override for unknown rule: RULE-nope" in result.stderr


# --- phases and explain ---------------------------------------------------------


def test_cli_phases_validates_the_whole_policy(tmp_path: Path) -> None:
    _write_config(tmp_path, '[rules.severity_overrides]\nRULE-file-length = "warning"\n')
    result = CliRunner().invoke(cli, ["phases", "-w", str(tmp_path)])
    assert result.exit_code == 2 and "redundant" in result.stderr
    _write_config(tmp_path, "[rules.settings.RULE-file-length]\nmax_lines = 'x'\n")
    assert CliRunner().invoke(cli, ["phases", "-w", str(tmp_path)]).exit_code == 2


def test_cli_explain_reports_only_its_rules_problems_as_errors(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        '[rules.severity_overrides]\nRULE-file-length = "warning"\n[rules.settings.RULE-markdown-link]\nx = 1\n',
    )
    runner = CliRunner()
    other = runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-secret-leak"])
    assert other.exit_code == 0, other.output
    assert "Warning: (RULES_POLICY_INVALID) severity override for RULE-file-length is redundant" in other.stderr
    own = runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-file-length"])
    assert own.exit_code == 2 and "[ERROR]  (RULES_POLICY_INVALID) severity override for RULE-file-length" in own.stderr
    assert "Warning: (RULES_POLICY_INVALID) settings for RULE-markdown-link" in own.stderr
    as_json = runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-file-length", "--format", "json"])
    assert as_json.exit_code == 2
    assert json.loads(as_json.stdout)["error"]["code"] == "RULES_POLICY_INVALID"


def test_cli_deletion_only_commit_rechecks_linking_files(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "docs").mkdir()
    (root / "docs/target.md").write_text("# T\n")
    (root / "docs/index.md").write_text("[t](target.md)\n")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "docs")
    _git(root, "rm", "-q", "docs/target.md")
    result = CliRunner().invoke(cli, ["check", "-w", str(root), "--staged", "--format", "json"])
    assert result.exit_code == 1, result.output
    assert [v["file"] for v in json.loads(result.stdout)] == ["docs/index.md"]


# --- exit-code convention: 0 nothing found, 1 findings, 2 could not run -------


def test_exit_codes_of_check_and_fix(tmp_path: Path) -> None:
    runner = CliRunner()
    assert runner.invoke(cli, ["check", "-w", str(tmp_path)]).exit_code == 0
    _broken_link_workspace(tmp_path)
    assert runner.invoke(cli, ["check", "-w", str(tmp_path)]).exit_code == 1
    assert runner.invoke(cli, ["fix", "-w", str(tmp_path)]).exit_code == 1  # nothing to repair it with
    assert runner.invoke(cli, ["check", "-w", str(tmp_path), "--staged", "--ci"]).exit_code == 2  # usage
    _write_config(tmp_path, "[rules]\nunknown = 1\n")
    for command in ("check", "fix"):
        result = runner.invoke(cli, [command, "-w", str(tmp_path)])
        assert result.exit_code == 2 and "[ERROR]  (RULES_CONFIG_INVALID)" in result.stderr
        assert "[TARGET] .devkit/config.toml" in result.stderr


def test_exit_code_of_fix_that_repairs_everything(tmp_path: Path) -> None:
    _fixable_link_workspace(tmp_path)
    assert CliRunner().invoke(cli, ["fix", "-w", str(tmp_path)]).exit_code == 0


def test_json_check_that_cannot_run_prints_the_error_envelope(tmp_path: Path) -> None:
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path), "--format", "json", "nope.md"])
    assert result.exit_code == 2
    error = json.loads(result.stdout)["error"]
    assert (error["code"], error["advisory"]["mode"]) == ("RULES_TARGET_INVALID", "INPUT_ERROR")


def test_exit_codes_of_phases(tmp_path: Path) -> None:
    runner = CliRunner()
    assert runner.invoke(cli, ["phases", "-w", str(tmp_path)]).exit_code == 0
    _write_config(tmp_path, '[rules.phase_overrides]\nRULE-nope = "hygiene"\n')
    result = runner.invoke(cli, ["phases", "-w", str(tmp_path)])
    assert (
        result.exit_code == 2 and "(RULES_POLICY_INVALID) phase override for unknown rule: RULE-nope" in result.stderr
    )


def test_exit_codes_of_explain(tmp_path: Path) -> None:
    runner = CliRunner()
    assert runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-file-length"]).exit_code == 0
    unknown = runner.invoke(cli, ["explain", "-w", str(tmp_path), "RULE-nope", "--format", "json"])
    assert unknown.exit_code == 2 and "[ACTION] INPUT_ERROR" in unknown.stderr
    assert json.loads(unknown.stdout)["error"]["code"] == "RULES_UNKNOWN_RULE"


def test_unexpected_errors_exit_2_as_advisories(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def explode(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("disk on fire")

    monkeypatch.setattr("devkit.rules.cli.commands.run_project_rules", explode)
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path)])
    assert result.exit_code == 2
    assert "[ERROR]  (UNEXPECTED_ERROR) disk on fire" in result.stderr and "[ACTION] MAINTENANCE" in result.stderr


def test_check_refuses_a_hand_edited_managed_rule(tmp_path: Path) -> None:
    import hashlib

    rel = ".devkit/managed/team/rules/r.py"
    source = (
        "from devkit.rules import RuleContext, Violation\n"
        "from devkit.rules.rules import BaseRule\n\n\n"
        "class R(BaseRule):\n"
        "    def __init__(self) -> None:\n"
        "        super().__init__(id='RULE-team-r', name='r', description='r')\n\n"
        "    def check(self, ctx: RuleContext) -> list[Violation]:\n"
        "        return []\n"
    )
    (tmp_path / ".devkit/managed/team/rules").mkdir(parents=True)
    (tmp_path / rel).write_text(source)
    write_receipt(
        tmp_path,
        [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [rel]}],
        {rel: hashlib.sha256(source.encode()).hexdigest()},
    )
    assert CliRunner().invoke(cli, ["check", "-w", str(tmp_path)]).exit_code == 0
    (tmp_path / rel).write_text(source + "# edited\n")
    result = CliRunner().invoke(cli, ["check", "-w", str(tmp_path)])
    assert result.exit_code == 2
    assert "(RULES_LOAD_FAILED)" in result.output and "differs from the hash in the receipt" in result.output
