from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
from agent_advisory import AdvisoryError
from agent_commit_gate import GateContext, GatesConfig, Outcome, Stage, default_registry, run_stage
from agent_commit_gate.cli import cli
from agent_commit_gate.gates import StagedRulesGate
from click.testing import CliRunner
from conftest import git

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


def _ctx(repo: Path) -> GateContext:
    return GateContext(repo_root=repo, git_dir=repo / ".git", stage=Stage.PRE_COMMIT)


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


def test_staged_broken_link_refuses(repo: Path) -> None:
    _write(repo, "docs/a.md", "[broken](missing.md)\n")
    git(repo, "add", "docs")
    error = _run(repo)
    assert error is not None
    assert error.code == "GATE_RULES_VIOLATION"
    assert "RULE-markdown-link docs/a.md:1" in error.details[0]
    assert error.target_files == ("docs/a.md",)
    assert "agent-rules fix" in (error.fix or "") and "explain RULE-markdown-link" in (error.fix or "")


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


def test_missing_rule_engine_fails_closed(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write(repo, "docs/a.md", "# fine\n")
    git(repo, "add", "docs")
    monkeypatch.setitem(sys.modules, "agent_rule_engine", None)
    error = _run(repo)
    assert error is not None and error.code == "GATE_RULES_UNAVAILABLE"
    assert "agent-rule-engine" in error.message and "uv sync" in (error.fix or "")


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
