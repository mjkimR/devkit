from __future__ import annotations

import hashlib
import json
from pathlib import Path

from click.testing import CliRunner
from devkit.advisory import AdvisoryError
from devkit.gate import GateContext, GatesConfig, Outcome, Stage, default_registry, run_stage
from devkit.gate.cli import cli
from devkit.gate.gates import StagedRulesGate
from testsupport.gate import gate_ctx, git

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


def _ctx(repo: Path) -> GateContext:
    return gate_ctx(repo)


def _write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run(repo: Path) -> AdvisoryError | None:
    try:
        StagedRulesGate().run(_ctx(repo))
    except AdvisoryError as exc:
        return exc
    return None


def test_gate_is_registered_and_enabled_by_default() -> None:
    gate = default_registry().get("rules-staged")
    assert gate is not None
    assert gate.stage is Stage.PRE_COMMIT and gate.enabled_by_default and gate.settings is None


def test_nothing_staged_is_skipped(repo: Path) -> None:
    result = StagedRulesGate().run(_ctx(repo))
    assert result.outcome is Outcome.SKIPPED and "no changed files" in result.note


def test_a_deletion_only_commit_is_evaluated(repo: Path) -> None:
    _write(repo, "docs/a.md", "# a\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "init", "--no-verify")
    git(repo, "rm", "-q", "docs/a.md")
    result = StagedRulesGate().run(_ctx(repo))
    assert result.outcome is Outcome.PASSED and "1 deleted" in result.note


def test_staged_broken_link_refuses(repo: Path) -> None:
    _write(repo, "docs/a.md", "[broken](missing.md)\n")
    git(repo, "add", "docs")
    error = _run(repo)
    assert error is not None
    assert error.code == "GATE_RULES_VIOLATION"
    assert "RULE-markdown-link docs/a.md:1" in error.details[0]
    assert error.target_files == ("docs/a.md",)
    assert "devkit rules fix" in (error.fix or "") and "explain RULE-markdown-link" in (error.fix or "")


def test_clean_index_passes_and_unstaged_breakage_is_invisible(repo: Path) -> None:
    _write(repo, "README.md", "# Repo\n")
    _write(repo, "docs/a.md", "[ok](../README.md)\n")
    git(repo, "add", ".")
    _write(repo, "docs/a.md", "[broken](missing.md)\n")  # unstaged: not part of the commit
    _write(repo, "notes.md", "[broken](nowhere.md)\n")  # untracked: never in the snapshot
    result = StagedRulesGate().run(_ctx(repo))
    assert result.outcome is Outcome.PASSED and "2 changed file(s)" in result.note

    git(repo, "add", "docs/a.md")
    assert _run(repo) is not None


def test_warning_only_passes_and_policy_comes_from_the_snapshot(repo: Path) -> None:
    _write(repo, "docs/a.md", "[broken](missing.md)\n")
    _write(repo, ".devkit/config.toml", '[rules.severity_overrides]\nRULE-markdown-link = "warning"\n')
    git(repo, "add", "docs")
    assert _run(repo) is not None  # the override is not staged yet, so it does not apply

    git(repo, "add", ".devkit")
    result = StagedRulesGate().run(_ctx(repo))
    assert result.outcome is Outcome.PASSED and "1 warning(s)" in result.note


def test_invalid_rules_policy_refuses(repo: Path) -> None:
    _write(repo, "docs/a.md", "# fine\n")
    _write(repo, ".devkit/config.toml", '[rules.phase_overrides]\nRULE-markdown-link = "linter"\n')
    git(repo, "add", ".")
    error = _run(repo)
    assert error is not None and error.code == "GATE_RULES_CONFIG_INVALID"
    assert error.target_files == (".devkit/config.toml",)


def test_synchronized_rule_pinned_by_the_receipt_runs_and_drift_refuses(repo: Path) -> None:
    rule_path = ".devkit/managed/team/rules/no_todo.py"
    _write(repo, ".gitignore", ".devkit/managed/\n")
    _write(repo, rule_path, NO_TODO_RULE)
    receipt = {
        "schema": 1,
        "packages": [],
        "selection": {"agents": [], "presets": {}},
        "assets": [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [rule_path]}],
        "files": {rule_path: {"sha256": hashlib.sha256(NO_TODO_RULE.encode()).hexdigest(), "mode": 420}},
    }
    _write(repo, ".devkit/installation.json", json.dumps(receipt))
    _write(repo, "notes.md", "TODO later\n")
    git(repo, "add", ".")
    assert ".devkit/managed" not in git(repo, "ls-files").stdout

    error = _run(repo)
    assert error is not None and error.code == "GATE_RULES_VIOLATION"
    assert "RULE-no-todo notes.md:1 TODO found" in error.details

    (repo / rule_path).write_text(NO_TODO_RULE + "\n# edited\n")
    error = _run(repo)
    assert error is not None and error.code == "GATE_RULES_LOAD_FAILED"
    assert "devkit sync" in (error.fix or "")


def test_excluded_paths_are_not_checked(repo: Path) -> None:
    # Same policy as `devkit rules check --staged`: [rules] exclude drops staged targets.
    _write(repo, "vendor/a.md", "[broken](missing.md)\n")
    _write(repo, ".devkit/config.toml", '[rules]\nexclude = ["vendor/**"]\n')
    git(repo, "add", ".")
    result = StagedRulesGate().run(_ctx(repo))
    assert result.outcome is Outcome.PASSED

    _write(repo, "docs/b.md", "[broken](missing.md)\n")
    git(repo, "add", "docs")
    error = _run(repo)
    assert error is not None and error.code == "GATE_RULES_VIOLATION"
    assert error.target_files == ("docs/b.md",)


def test_cli_and_gate_agree_on_excluded_paths(repo: Path) -> None:
    from devkit.rules.cli import cli as rules_cli

    _write(repo, "vendor/a.md", "[broken](missing.md)\n")
    _write(repo, ".devkit/config.toml", '[rules]\nexclude = ["vendor/**"]\n')
    git(repo, "add", ".")
    checked = CliRunner().invoke(rules_cli, ["check", "-w", str(repo), "--staged"])
    gated = CliRunner().invoke(cli, ["run", "-w", str(repo), "pre-commit"])
    assert checked.exit_code == 0, checked.output
    assert gated.exit_code == 0, gated.output


def test_malformed_receipt_refuses(repo: Path) -> None:
    _write(repo, ".devkit/installation.json", "{not json")
    _write(repo, "docs/a.md", "# fine\n")
    git(repo, "add", ".")
    error = _run(repo)
    assert error is not None and error.code == "GATE_RULES_LOAD_FAILED"
    assert any("invalid installation receipt" in detail for detail in error.details)


def test_pre_commit_stage_reports_the_refusal(repo: Path) -> None:
    _write(repo, "docs/a.md", "[broken](missing.md)\n")
    git(repo, "add", "docs")
    report = run_stage(_ctx(repo), default_registry(), GatesConfig())
    assert report.failed
    run = next(r for r in report.runs if r.gate_id == "rules-staged")
    assert run.outcome is Outcome.FAILED and run.error is not None and run.error.code == "GATE_RULES_VIOLATION"

    result = CliRunner().invoke(cli, ["run", "-w", str(repo), "pre-commit"])
    assert result.exit_code == 1
    assert "[GATE: rules-staged stage=pre-commit outcome=failed]" in result.output
    assert "GATE_RULES_VIOLATION" in result.output and "RULE-markdown-link docs/a.md:1" in result.output

    (repo / ".git/devkit.config").write_text("[gates.settings.rules-staged]\nenabled = false\n")
    result = CliRunner().invoke(cli, ["run", "-w", str(repo), "-v", "pre-commit"])
    assert (
        result.exit_code == 0 and "[GATE: rules-staged stage=pre-commit outcome=skipped note=disabled]" in result.output
    )
