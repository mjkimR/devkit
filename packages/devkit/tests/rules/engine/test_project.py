from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from devkit.rules import (
    Phase,
    RulesConfigError,
    RulesDirError,
    RulesRunError,
    TargetError,
    WorkspaceCache,
    build_project_registry,
    expand_targets,
    git_snapshot,
    load_project_rules,
    run_project_rules,
)
from testsupport.rules import digests, init_repo, write_receipt

BROKEN = "[broken](missing.md)\n"

EXTRA_RULE = """from devkit.rules import RuleContext, Violation
from devkit.rules.rules import BaseRule


class ExtraRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-extra", name="extra", description="from rules_dir")

    def check(self, ctx: RuleContext) -> list[Violation]:
        return []
"""


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _files(run_violations: list) -> list[str]:
    return sorted(v.file for v in run_violations)


def _git(root: Path, *args: str) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=env)


def test_whole_workspace_run_applies_exclude(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", BROKEN)
    _write(tmp_path, "vendor/b.md", BROKEN)
    run = run_project_rules(tmp_path)
    assert _files(run.result.violations) == ["docs/a.md", "vendor/b.md"]
    assert not run.ok and run.errors == [] and run.context is not None

    _write(tmp_path, ".devkit/config.toml", '[rules]\nexclude = ["vendor/**"]\n')
    run = run_project_rules(tmp_path)
    assert _files(run.result.violations) == ["docs/a.md"]
    assert run.config.exclude == ("vendor/**",)
    assert run.context is not None and run.context.exclude == ("vendor/**",)
    assert run.workspace_root == tmp_path.resolve() and run.phase is Phase.LINTER


def test_explicit_targets_apply_exclude_and_expand_directories(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", BROKEN)
    _write(tmp_path, "docs/sub/c.md", BROKEN)
    _write(tmp_path, "vendor/b.md", BROKEN)
    _write(tmp_path, ".devkit/config.toml", '[rules]\nexclude = ["vendor/**"]\n')
    run = run_project_rules(tmp_path, targets=["vendor/b.md"])
    assert run.result.violations == [] and run.ok
    run = run_project_rules(tmp_path, targets=["docs", tmp_path / "docs/a.md"])
    assert _files(run.result.violations) == ["docs/a.md", "docs/sub/c.md"]


def test_an_empty_selection_checks_nothing(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", BROKEN)
    (tmp_path / "empty").mkdir()
    for targets in ([], ["empty"]):
        run = run_project_rules(tmp_path, targets=targets)
        assert run.context is None and run.result.violations == [] and run.ok


def test_invalid_targets(tmp_path: Path) -> None:
    with pytest.raises(TargetError, match="outside the workspace"):
        run_project_rules(tmp_path, targets=["../elsewhere.md"])
    with pytest.raises(TargetError, match="not an existing file or directory"):
        run_project_rules(tmp_path, targets=["missing.md"])


def test_expand_targets_deduplicates(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", "x")
    root = tmp_path.resolve()
    assert expand_targets(root, WorkspaceCache(root), ["docs/a.md", "docs", "docs/a.md"]) == ["docs/a.md"]


def test_invalid_policy_raises_config_error(tmp_path: Path) -> None:
    _write(tmp_path, ".devkit/config.toml", '[rules]\nexclude = "vendor"\n')
    with pytest.raises(RulesConfigError):
        run_project_rules(tmp_path)


def test_policy_errors_are_returned_in_the_result(tmp_path: Path) -> None:
    _write(tmp_path, ".devkit/config.toml", '[rules.severity_overrides]\nRULE-nope = "warning"\n')
    run = run_project_rules(tmp_path)
    assert [str(e) for e in run.errors] == ["severity override for unknown rule: RULE-nope"] and not run.ok
    assert run.errors[0].code == "RULES_POLICY_INVALID" and run.errors[0].rule_id == "RULE-nope"


def test_load_errors_skip_evaluation(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", BROKEN)
    _write(tmp_path, ".devkit/installation.json", "{not json")
    run = run_project_rules(tmp_path)
    assert run.result.violations == [] and run.result.errors == []
    assert len(run.load_errors) == 1 and "invalid installation receipt" in str(run.load_errors[0])
    assert run.load_errors[0].code == "RULES_LOAD_FAILED"
    assert run.errors == list(run.load_errors) and not run.ok
    with pytest.raises(RulesRunError) as caught:
        run.raise_for_problems()
    assert caught.value.code == "RULES_RUN_FAILED" and caught.value.problems == tuple(run.load_errors)


def test_blocking_violations_and_raise_for_problems_of_a_completed_run(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", BROKEN)
    run = run_project_rules(tmp_path)
    run.raise_for_problems()  # findings are not problems
    assert [v.file for v in run.blocking_violations] == ["docs/a.md"]
    assert run.blocking_violations == run.result.blocking_violations


def test_load_project_rules_collects_load_and_policy_errors(tmp_path: Path) -> None:
    _write(tmp_path, "extra/extra.py", EXTRA_RULE)
    _write(tmp_path, "extra/broken.py", "raise RuntimeError('broken')\n")
    _write(
        tmp_path,
        ".devkit/config.toml",
        '[rules.severity_overrides]\nRULE-nope = "warning"\n[rules.settings.RULE-file-length]\nmax_lines = 10\n',
    )
    project = load_project_rules(tmp_path, tmp_path / "extra")
    assert project.rules_dir == (tmp_path / "extra").resolve()
    assert "RULE-extra" in [rule.id for rule in project.rules]
    assert [e.code for e in project.load_errors] == ["RULES_LOAD_FAILED"]
    assert [e.rule_id for e in project.policy_errors] == ["RULE-nope"]
    assert project.errors == [*project.load_errors, *project.policy_errors]
    assert project.resolvers["RULE-file-length"].resolve().max_lines == 10


def test_rules_dir_and_receipt_rules_are_loaded_after_builtins(tmp_path: Path) -> None:
    _write(tmp_path, "extra/extra.py", EXTRA_RULE)
    _write(tmp_path, ".devkit/managed/team/rules/managed.py", EXTRA_RULE.replace("RULE-extra", "RULE-managed"))
    write_receipt(
        tmp_path,
        [{"bundle": "team", "id": "rules", "kind": "rule", "paths": [".devkit/managed/team/rules/managed.py"]}],
        digests(tmp_path, ".devkit/managed/team/rules/managed.py"),
    )
    run = run_project_rules(tmp_path, rules_dir=tmp_path / "extra")
    ids = [rule.id for rule in run.rules]
    assert ids[-2:] == ["RULE-managed", "RULE-extra"]
    assert run.rules_dir == (tmp_path / "extra").resolve()
    registry = build_project_registry(tmp_path.resolve())
    assert "RULE-extra" not in [rule.id for rule in registry.get_all()]


def test_hygiene_phase_and_fix_are_passed_through(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", "x\n")
    run = run_project_rules(tmp_path, phase=Phase.HYGIENE, fix=True, dry_run=True)
    assert run.context is not None and run.context.phase is Phase.HYGIENE
    assert run.context.fix and run.context.dry_run


def test_snapshot_run_reads_policy_from_the_index(tmp_path: Path) -> None:
    root = (tmp_path / "repo").resolve()
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _write(root, "vendor/a.md", BROKEN)
    _write(root, "docs/b.md", BROKEN)
    _write(root, ".devkit/config.toml", '[rules]\nexclude = ["vendor/**"]\n')
    _git(root, "add", "vendor", "docs")
    snapshot = git_snapshot(root, staged=True)
    run = run_project_rules(root, snapshot=snapshot)
    # The exclude is not staged yet, so it does not apply.
    assert _files(run.result.violations) == ["docs/b.md", "vendor/a.md"]
    assert run.workspace_root != root and not run.workspace_root.exists()

    _git(root, "add", ".devkit")
    run = run_project_rules(root, snapshot=git_snapshot(root, staged=True))
    assert _files(run.result.violations) == ["docs/b.md"]


def test_snapshot_without_changes_checks_nothing(tmp_path: Path) -> None:
    root = (tmp_path / "repo").resolve()
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    run = run_project_rules(root, snapshot=git_snapshot(root, staged=True))
    assert run.context is None and run.ok


def test_snapshot_argument_validation(tmp_path: Path) -> None:
    root = (tmp_path / "repo").resolve()
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    snapshot = git_snapshot(root, staged=True)
    with pytest.raises(ValueError, match="do not pass targets"):
        run_project_rules(root, snapshot=snapshot, targets=["a.md"])
    with pytest.raises(ValueError, match="cannot apply fixes"):
        run_project_rules(root, snapshot=snapshot, fix=True)
    with pytest.raises(ValueError, match="snapshot was taken from"):
        run_project_rules(tmp_path, snapshot=snapshot)


TODO_RULE = """from devkit.rules import RuleContext, Violation
from devkit.rules.rules import BaseRule


class TodoRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-todo", name="todo", description="todo")

    def check(self, ctx: RuleContext) -> list[Violation]:
        return [Violation(self.id, f, 1, "TODO") for f in ctx.changed_files if f.endswith(".md") and "TODO" in ctx.cache.read_text(f)]
"""


def test_snapshot_rules_dir_is_read_from_the_snapshot(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo").resolve()
    _write(root, "rules/todo.py", TODO_RULE)
    _write(root, "notes.md", "TODO\n")
    _git(root, "add", ".")
    run = run_project_rules(root, snapshot=git_snapshot(root, staged=True), rules_dir=root / "rules")
    assert [v.rule_id for v in run.result.violations] == ["RULE-todo"]

    # An unstaged edit of the rule does not change the gate.
    _write(root, "rules/todo.py", TODO_RULE.replace('if "TODO" in', 'if "never" in'))
    run = run_project_rules(root, snapshot=git_snapshot(root, staged=True), rules_dir=root / "rules")
    assert [v.rule_id for v in run.result.violations] == ["RULE-todo"]


def test_snapshot_rules_dir_outside_the_repository_or_untracked_is_refused(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo").resolve()
    _write(root, "notes.md", "x\n")
    _write(root, "local-rules/todo.py", TODO_RULE)
    _write(tmp_path, "outside/todo.py", TODO_RULE)
    _git(root, "add", "notes.md")
    snapshot = git_snapshot(root, staged=True)
    with pytest.raises(RulesDirError, match="outside the repository"):
        run_project_rules(root, snapshot=snapshot, rules_dir=tmp_path / "outside")
    with pytest.raises(RulesDirError, match="not in the staged snapshot"):
        run_project_rules(root, snapshot=snapshot, rules_dir=root / "local-rules")


def test_directory_targets_skip_symlinks_that_leave_the_workspace(tmp_path: Path) -> None:
    root = (tmp_path / "ws").resolve()
    _write(root, "docs/a.md", BROKEN)
    _write(tmp_path, "outside.md", BROKEN)
    (root / "docs/out.md").symlink_to(tmp_path / "outside.md")
    run = run_project_rules(root, targets=["docs"])
    assert _files(run.result.violations) == ["docs/a.md"]
    with pytest.raises(TargetError, match="symlink that resolves outside"):
        run_project_rules(root, targets=["docs/out.md"])


def test_directory_symlink_targets_resolving_outside_are_refused(tmp_path: Path) -> None:
    root = (tmp_path / "ws").resolve()
    _write(root, "README.md", "x\n")
    _write(tmp_path, "out/a.md", BROKEN)
    (root / "linkdir").symlink_to("../out")
    for target in ["linkdir", str(root / "linkdir")]:
        with pytest.raises(TargetError, match="symlink that resolves outside") as refused:
            run_project_rules(root, targets=[target])
        assert refused.value.code == "RULES_TARGET_INVALID"


def test_whole_workspace_runs_skip_git_ignored_and_devkit_files(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo").resolve()
    _write(root, ".gitignore", "venv/\n")
    _write(root, "venv/lib/doc.md", BROKEN)
    _write(root, ".devkit/managed/team/guide.md", "[s](wrong/setup.md)\n")
    _write(root, "docs/setup.md", "x\n")
    run = run_project_rules(root, fix=True)
    assert run.result.violations == [] and run.ok
    assert (root / ".devkit/managed/team/guide.md").read_text() == "[s](wrong/setup.md)\n"


def test_snapshot_deletions_recheck_files_linking_to_them(tmp_path: Path) -> None:
    root = init_repo(tmp_path / "repo").resolve()
    _write(root, "docs/target.md", "# Target\n")
    _write(root, "docs/index.md", "[t](target.md)\n")
    _write(root, "docs/other.md", "[readme](../README.md)\n")
    _write(root, "guide.md", "[folder](docs/)\n")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "docs")
    _git(root, "rm", "-q", "docs/target.md")
    snapshot = git_snapshot(root, staged=True)
    assert snapshot.changed == () and snapshot.deleted == ("docs/target.md",)
    run = run_project_rules(root, snapshot=snapshot)
    assert run.context is not None and sorted(run.context.changed_files) == ["docs/index.md", "guide.md"]
    assert [(v.rule_id, v.file) for v in run.result.violations] == [("RULE-markdown-link", "docs/index.md")]
