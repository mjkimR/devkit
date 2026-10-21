"""Every error the rule engine raises or collects is an ``AdvisoryError`` with a stable code."""

from __future__ import annotations

from pathlib import Path

import pytest
from devkit.advisory import ActionMode, AdvisoryError, ExitCode
from devkit_agt.features.rules import (
    RuleLoadError,
    RulesConfigError,
    RulesDirError,
    RulesRunError,
    SnapshotError,
    TargetError,
    git_snapshot,
    load_rules_config,
    run_project_rules,
)
from testsupport.rules import git, init_repo, write


def test_invalid_rules_table_is_rules_config_invalid(tmp_path: Path) -> None:
    write(tmp_path, ".devkit/config.toml", "[rules]\nexclude = 3\n")
    with pytest.raises(RulesConfigError) as info:
        load_rules_config(tmp_path)
    error = info.value
    assert isinstance(error, AdvisoryError) and not isinstance(error, ValueError)
    assert (error.code, error.mode, error.exit_code) == ("RULES_CONFIG_INVALID", ActionMode.INPUT_ERROR, ExitCode.ERROR)
    assert error.target_files == (".devkit/config.toml",)


def test_bad_target_is_rules_target_invalid(tmp_path: Path) -> None:
    with pytest.raises(TargetError) as info:
        run_project_rules(tmp_path, targets=["missing.md"])
    assert (info.value.code, info.value.target_files) == ("RULES_TARGET_INVALID", ("missing.md",))


def test_snapshot_outside_a_repository_is_an_input_error(tmp_path: Path) -> None:
    with pytest.raises(SnapshotError) as info:
        git_snapshot(tmp_path, staged=True)
    assert info.value.code == "RULES_SNAPSHOT_FAILED" and info.value.mode is ActionMode.INPUT_ERROR


def test_unknown_ci_base_is_an_input_error_naming_the_flag(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    with pytest.raises(SnapshotError) as info:
        git_snapshot(root, staged=False, base="no-such-ref")
    assert info.value.target_files == ("--base",) and info.value.mode is ActionMode.INPUT_ERROR


def test_rules_dir_outside_the_snapshot_repository_is_rules_dir_invalid(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo")
    write(root, "a.md", "# A\n")
    git(root, "add", "a.md")
    outside = tmp_path / "rules"
    outside.mkdir()
    with pytest.raises(RulesDirError) as info:
        run_project_rules(root, snapshot=git_snapshot(root, staged=True), rules_dir=outside)
    assert info.value.code == "RULES_DIR_INVALID" and info.value.target_files == ("--rules-dir",)


def test_lint_binding_raises_rules_run_failed_with_each_problem(tmp_path: Path) -> None:
    from devkit_agt.features.workflow.usecases.lint import lint_with_rules

    write(tmp_path, ".devkit/installation.json", "{")
    write(tmp_path, "a.md", "# A\n")
    with pytest.raises(RulesRunError) as info:
        lint_with_rules(tmp_path, ["a.md"])
    error = info.value
    assert error.code == "RULES_RUN_FAILED" and "invalid installation receipt" in str(error)
    assert [type(problem) for problem in error.problems] == [RuleLoadError]
    assert error.details == tuple(f"({p.code}) {p}" for p in error.problems)
