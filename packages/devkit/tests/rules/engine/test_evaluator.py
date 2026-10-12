from __future__ import annotations

from pathlib import Path

from devkit.advisory import ActionMode
from devkit.rules import Phase, RuleContext, WorkspaceCache, default_registry, evaluate


def test_evaluator_autofix_convergence(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    # A broken relative link whose target basename exists exactly once elsewhere
    (temp_workspace / "docs" / "guides").mkdir(parents=True)
    (temp_workspace / "docs" / "guides" / "setup.md").write_text("# Setup\n", encoding="utf-8")
    doc_path = temp_workspace / "docs" / "index.md"
    doc_path.write_text("See [setup](wrong/setup.md).\n", encoding="utf-8")

    ctx = RuleContext(
        workspace_root=temp_workspace,
        cache=workspace_cache,
        phase=Phase.LINTER,
        fix=True,
    )
    registry = default_registry()

    result = evaluate(ctx, registry.get_all())
    # The violation should be marked as fixed!
    assert any(v.rule_id == "RULE-markdown-link" and v.fixed for v in result.violations)
    assert not result.has_errors

    # Now verify the file on disk points at the existing target
    assert doc_path.read_text(encoding="utf-8") == "See [setup](guides/setup.md).\n"


def test_evaluator_phase_filtering(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    doc_path = temp_workspace / "docs" / "long.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text("\n".join(f"Line {i}" for i in range(500)), encoding="utf-8")

    registry = default_registry()

    # 1. In Linter phase, FileLengthRule (hygiene) should not run
    ctx_linter = RuleContext(
        workspace_root=temp_workspace,
        cache=workspace_cache,
        phase=Phase.LINTER,
    )
    res_linter = evaluate(ctx_linter, registry.get_all())
    assert not any(v.rule_id == "RULE-file-length" for v in res_linter.violations)

    # 2. In Hygiene phase, FileLengthRule should run
    ctx_hygiene = RuleContext(
        workspace_root=temp_workspace,
        cache=workspace_cache,
        phase=Phase.HYGIENE,
    )
    res_hygiene = evaluate(ctx_hygiene, registry.get_all())
    assert any(v.rule_id == "RULE-file-length" for v in res_hygiene.violations)


def test_fix_failure_rechecks_partial_changes(tmp_path: Path) -> None:
    from devkit.rules import Violation
    from devkit.rules.rules import BaseRule

    class FailingFix(BaseRule):
        def __init__(self) -> None:
            super().__init__(id="RULE-failing", name="failing", description="Partial fix failure")

        def check(self, ctx: RuleContext) -> list[Violation]:
            return [Violation(self.id, "doc.md", 1, ctx.cache.read_text("doc.md"), fixable=True)]

        def fix(self, ctx: RuleContext) -> list[str]:
            (ctx.workspace_root / "doc.md").write_text("after")
            raise RuntimeError("Failed after writing")

    (tmp_path / "doc.md").write_text("before")
    ctx = RuleContext(workspace_root=tmp_path, fix=True)
    result = evaluate(ctx, [FailingFix()])
    assert result.has_errors
    assert result.violations[0].message == "after"
    assert not result.violations[0].fixed
    assert ctx.cache.read_text("doc.md") == "after"


def test_each_fix_invalidates_cache_for_next_rule(tmp_path: Path) -> None:
    from devkit.rules.rules import BaseRule

    class DirectWrite(BaseRule):
        def __init__(self) -> None:
            super().__init__(id="RULE-write", name="write", description="Direct writer")

        def check(self, ctx: RuleContext) -> list:
            ctx.cache.read_text("doc.md")
            return []

        def fix(self, ctx: RuleContext) -> list[str]:
            (ctx.workspace_root / "doc.md").write_text("updated")
            return ["doc.md"]

    class Reader(DirectWrite):
        def fix(self, ctx: RuleContext) -> list[str]:
            assert ctx.cache.read_text("doc.md") == "updated"
            return []

    (tmp_path / "doc.md").write_text("original")
    ctx = RuleContext(workspace_root=tmp_path, fix=True)
    assert not evaluate(ctx, [DirectWrite(), Reader()]).has_errors


def test_fixed_status_survives_fixes_that_move_lines(tmp_path: Path) -> None:
    from devkit.rules import Violation
    from devkit.rules.rules import BaseRule

    class Header(BaseRule):
        """Two fixable findings; the fix adds a header line and repairs only one of them."""

        def __init__(self) -> None:
            super().__init__(id="RULE-header", name="header", description="header")

        def check(self, ctx: RuleContext) -> list[Violation]:
            lines = ctx.cache.read_text("doc.md").splitlines()
            return [
                Violation(self.id, "doc.md", i, "bad", fixable=True) for i, line in enumerate(lines, 1) if line == "bad"
            ]

        def fix(self, ctx: RuleContext) -> list[str]:
            ctx.cache.write_text("doc.md", "# header\nok\nbad\n")
            return ["doc.md"]

    (tmp_path / "doc.md").write_text("bad\nbad\n")
    result = evaluate(RuleContext(workspace_root=tmp_path, fix=True), [Header()])
    # One finding was repaired and one moved to line 3; with line-keyed matching both looked fixed.
    assert sum(v.fixed for v in result.violations) == 1
    assert [v.line for v in result.violations if not v.fixed] == [3]


def test_fix_without_changes_returns_the_initial_findings(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("[x](missing.md)\n")
    result = evaluate(RuleContext(workspace_root=tmp_path, fix=True), default_registry().get_all())
    assert [(v.rule_id, v.fixable, v.fixed) for v in result.violations] == [("RULE-markdown-link", False, False)]


def test_recheck_errors_are_reported(tmp_path: Path) -> None:
    from devkit.rules import Violation
    from devkit.rules.rules import BaseRule

    class FlakyRecheck(BaseRule):
        def __init__(self) -> None:
            super().__init__(id="RULE-flaky", name="flaky", description="flaky")
            self.calls = 0

        def check(self, ctx: RuleContext) -> list[Violation]:
            self.calls += 1
            if self.calls > 1:
                raise RuntimeError("boom")
            return [Violation(self.id, "doc.md", 1, "x", fixable=True)]

        def fix(self, ctx: RuleContext) -> list[str]:
            return ["doc.md"]

    (tmp_path / "doc.md").write_text("x")
    result = evaluate(RuleContext(workspace_root=tmp_path, fix=True), [FlakyRecheck()])
    assert [str(e) for e in result.errors] == ["Rule recheck error (RULE-flaky): boom"]
    assert result.errors[0].code == "RULES_EXECUTION_FAILED" and result.errors[0].rule_id == "RULE-flaky"
    assert result.errors[0].mode is ActionMode.MAINTENANCE and result.errors[0].target_files == (__file__,)
    assert result.violations == [] and result.has_errors
