"""The built-in ``rules-check`` pre-commit gate."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from devkit.advisory import ActionMode, Actor, Level
from devkit.gate import GateRefusedError, Stage
from devkit.gate.cli import cli
from devkit.gate.gates.rules import MAX_LISTED, RulesCheckGate, _not_run
from devkit.rules import RuleLoadError, RulesRunError
from testsupport.gate import gate_ctx, git


def _run(repo: Path):
    return RulesCheckGate().run(gate_ctx(repo, Stage.PRE_COMMIT))


def _stage(repo: Path, name: str, text: str) -> None:
    (repo / name).write_text(text)
    git(repo, "add", name)


def test_nothing_staged_skips(repo: Path) -> None:
    assert _run(repo).note == "nothing staged"


def test_a_clean_staged_tree_passes_without_notices(repo: Path) -> None:
    _stage(repo, "README.md", "# Repo\n")
    _stage(repo, "a.md", "[ok](README.md)\n")
    result = _run(repo)
    assert result.note == "2 staged file(s) checked" and result.notices == ()


def test_an_error_violation_refuses_the_commit(repo: Path) -> None:
    _stage(repo, "a.md", "[bad](missing.md)\n")
    with pytest.raises(GateRefusedError) as info:
        _run(repo)
    error = info.value
    assert (error.code, error.mode, error.exit_code) == ("GATE_RULES_FAILED", ActionMode.BLOCKED, 1)
    assert error.message == "1 rule violation(s) in the staged tree"
    assert list(error.details) == [
        "RULE-markdown-link a.md:1: Broken relative markdown link 'missing.md'",
        "  fix: Verify relative path 'missing.md' exists",
    ]
    assert error.fix is not None and "devkit rules check --staged" in error.fix


def test_a_long_refusal_lists_the_first_violations_and_counts_the_rest(repo: Path) -> None:
    _stage(repo, "a.md", "".join(f"[bad](missing-{n}.md)\n" for n in range(MAX_LISTED + 3)))
    with pytest.raises(GateRefusedError) as info:
        _run(repo)
    assert info.value.details[-1] == "... and 3 more"


def test_the_staged_tree_is_checked_not_the_working_tree(repo: Path) -> None:
    _stage(repo, "a.md", "[bad](missing.md)\n")
    (repo / "a.md").write_text("fixed but not staged\n")
    with pytest.raises(GateRefusedError):
        _run(repo)

    _stage(repo, "a.md", "fixed\n")
    (repo / "b.md").write_text("[bad](missing.md)\n")  # untracked
    assert _run(repo).note == "1 staged file(s) checked"


def test_warning_violations_pass_with_one_notice(repo: Path) -> None:
    (repo / ".devkit").mkdir()
    _stage(repo, ".devkit/config.toml", '[rules.severity_overrides]\nRULE-markdown-link = "warning"\n')
    _stage(repo, "a.md", "[bad](missing.md)\n")
    result = _run(repo)
    [notice] = result.notices
    assert (notice.code, notice.level) == ("GATE_RULES_WARNINGS", Level.WARNING)
    assert notice.details[0] == "RULE-markdown-link a.md:1: Broken relative markdown link 'missing.md'"


def test_a_run_that_cannot_complete_is_not_a_refusal(repo: Path) -> None:
    (repo / ".devkit").mkdir()
    _stage(repo, ".devkit/config.toml", '[rules.severity_overrides]\nRULE-no-such-rule = "warning"\n')
    with pytest.raises(RulesRunError) as info:
        _run(repo)
    assert info.value.code == "RULES_RUN_FAILED" and info.value.mode is ActionMode.MAINTENANCE


def test_problems_sharing_one_automatic_fix_make_the_failure_automatic() -> None:
    missing = [
        RuleLoadError(f"synchronized rule {n}.py is missing", actor=Actor.TOOL, fix="Run `devkit sync`") for n in "ab"
    ]
    error = _not_run(missing)
    assert (error.mode, error.fix) == (ActionMode.AUTO, "Run `devkit sync`")
    mixed = [*missing, RuleLoadError("rule c.py fails to import", fix="Fix the rule")]
    assert _not_run(mixed).mode is ActionMode.MAINTENANCE


def test_the_hook_index_is_checked_and_the_environment_restored(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stage(repo, "a.md", "fine\n")
    index = repo / ".git" / "other-index"
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")} | {"GIT_INDEX_FILE": str(index)}
    (repo / "b.md").write_text("[bad](missing.md)\n")
    subprocess.run(["git", "-C", str(repo), "add", "b.md"], check=True, env=env)
    monkeypatch.setenv("GIT_INDEX_FILE", ".git/other-index")  # Git may pass it relative to the top level
    monkeypatch.setenv("GIT_DIR", str(repo / ".git"))
    monkeypatch.delenv("DEVKIT_GIT_INDEX_FILE", raising=False)
    with pytest.raises(GateRefusedError):
        _run(repo)  # b.md is only in the hook's index
    assert os.environ["GIT_INDEX_FILE"] == ".git/other-index" and os.environ["GIT_DIR"] == str(repo / ".git")
    assert "DEVKIT_GIT_INDEX_FILE" not in os.environ


def test_the_installed_hook_refuses_a_commit_with_a_violation(repo: Path) -> None:
    _stage(repo, "README.md", "# Repo\n")
    git(repo, "commit", "-m", "init")
    result = CliRunner().invoke(cli, ["install", "-w", str(repo), "--python", sys.executable])
    assert result.exit_code == 0, result.output

    (repo / "README.md").write_text("[bad](missing.md)\n")
    refused = git(repo, "commit", "-am", "docs: break a link", check=False)
    assert refused.returncode == 1 and "(GATE_RULES_FAILED)" in refused.stderr and "missing.md" in refused.stderr

    (repo / ".git/devkit.config").write_text("[gates.settings.rules-check]\nenabled = false\n")
    assert git(repo, "commit", "-am", "docs: break a link", check=False).returncode == 0
