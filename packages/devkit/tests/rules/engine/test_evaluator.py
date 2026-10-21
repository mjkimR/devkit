from __future__ import annotations

from pathlib import Path

from devkit.advisory import ActionMode, AdvisoryError
from devkit_agt.features.rules import (
    Phase,
    RuleContext,
    Violation,
    WorkspaceCache,
    default_rule_registry,
    evaluate_rules,
)


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
    registry = default_rule_registry()

    result = evaluate_rules(ctx, registry.get_all())
    # The violation should be marked as fixed!
    assert any(v.rule_id == "RULE-markdown-link" and v.fixed for v in result.violations)
    assert result.ok

    # Now verify the file on disk points at the existing target
    assert doc_path.read_text(encoding="utf-8") == "See [setup](guides/setup.md).\n"


def test_evaluator_phase_filtering(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    doc_path = temp_workspace / "docs" / "long.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text("\n".join(f"Line {i}" for i in range(500)), encoding="utf-8")

    registry = default_rule_registry()

    # 1. In Linter phase, FileLengthRule (hygiene) should not run
    ctx_linter = RuleContext(
        workspace_root=temp_workspace,
        cache=workspace_cache,
        phase=Phase.LINTER,
    )
    res_linter = evaluate_rules(ctx_linter, registry.get_all())
    assert not any(v.rule_id == "RULE-file-length" for v in res_linter.violations)

    # 2. In Hygiene phase, FileLengthRule should run
    ctx_hygiene = RuleContext(
        workspace_root=temp_workspace,
        cache=workspace_cache,
        phase=Phase.HYGIENE,
    )
    res_hygiene = evaluate_rules(ctx_hygiene, registry.get_all())
    assert any(v.rule_id == "RULE-file-length" for v in res_hygiene.violations)


def test_fix_failure_rechecks_partial_changes(tmp_path: Path) -> None:
    from devkit_agt.features.rules.services.builtins import BaseRule

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
    result = evaluate_rules(ctx, [FailingFix()])
    assert not result.ok
    assert result.violations[0].message == "after"
    assert not result.violations[0].fixed
    assert ctx.cache.read_text("doc.md") == "after"


def test_each_fix_invalidates_cache_for_next_rule(tmp_path: Path) -> None:
    from devkit_agt.features.rules.services.builtins import BaseRule

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
    assert evaluate_rules(ctx, [DirectWrite(), Reader()]).ok


def test_fixed_status_survives_fixes_that_move_lines(tmp_path: Path) -> None:
    from devkit_agt.features.rules.services.builtins import BaseRule

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
    result = evaluate_rules(RuleContext(workspace_root=tmp_path, fix=True), [Header()])
    # One finding was repaired and one moved to line 3; with line-keyed matching both looked fixed.
    assert sum(v.fixed for v in result.violations) == 1
    assert [v.line for v in result.violations if not v.fixed] == [3]


def test_fix_without_changes_returns_the_initial_findings(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("[x](missing.md)\n")
    result = evaluate_rules(RuleContext(workspace_root=tmp_path, fix=True), default_rule_registry().get_all())
    assert [(v.rule_id, v.fixable, v.fixed) for v in result.violations] == [("RULE-markdown-link", False, False)]


def test_recheck_errors_are_reported(tmp_path: Path) -> None:
    from devkit_agt.features.rules.services.builtins import BaseRule

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
    result = evaluate_rules(RuleContext(workspace_root=tmp_path, fix=True), [FlakyRecheck()])
    assert [str(e) for e in result.errors] == ["Rule recheck error (RULE-flaky): boom"]
    assert result.errors[0].code == "RULES_EXECUTION_FAILED" and result.errors[0].rule_id == "RULE-flaky"
    assert result.errors[0].mode is ActionMode.MAINTENANCE and result.errors[0].target_files == (__file__,)
    assert result.violations == [] and not result.ok


def test_an_advisory_a_rule_raises_keeps_its_code(tmp_path: Path) -> None:
    from devkit_agt.features.rules.services.builtins import BaseRule

    class Refusing(BaseRule):
        def __init__(self) -> None:
            super().__init__(id="RULE-refusing", name="refusing", description="refusing")

        def check(self, ctx: RuleContext) -> list[Violation]:
            return [Violation(self.id, "doc.md", 1, "x", fixable=True)]

        def fix(self, ctx: RuleContext) -> list[str]:
            raise AdvisoryError(
                "pinned", "detail", code="PINNED_WRITE_REFUSED", guardrail=True, fix="Override it", target_files=["a"]
            )

    (tmp_path / "doc.md").write_text("x")
    result = evaluate_rules(RuleContext(workspace_root=tmp_path, fix=True), [Refusing()])
    [error] = result.errors
    assert (error.code, error.rule_id, error.mode, error.fix) == (
        "PINNED_WRITE_REFUSED",
        "RULE-refusing",
        ActionMode.BLOCKED,
        "Override it",
    )
    assert error.target_files == ("a",) and error.details == ("detail",)
    assert str(error) == "Rule fix error (RULE-refusing): pinned"


def _finding(line: int, message: str = "bad", *, fixable: bool = True) -> Violation:
    return Violation("RULE-x", "doc.md", line, message, fixable=fixable)


def test_mark_fixed_counts_findings_by_identity_and_leaves_inputs_alone() -> None:
    from devkit_agt.features.rules.services.evaluator import _mark_fixed

    initial = [_finding(1), _finding(2), _finding(3, "other"), _finding(4, "manual", fixable=False)]
    recheck = [_finding(5), _finding(4, "manual", fixable=False)]
    marked = _mark_fixed(initial, recheck)
    # One of two "bad" findings remains (on a moved line), "other" is gone, the unfixable one stays as rechecked.
    assert [(v.line, v.message, v.fixed) for v in marked] == [
        (2, "bad", True),
        (3, "other", True),
        (5, "bad", False),
        (4, "manual", False),
    ]
    assert not any(v.fixed for v in initial) and marked[2] is recheck[0]


def test_mark_fixed_without_recheck_findings_marks_every_fixable_finding() -> None:
    from devkit_agt.features.rules.services.evaluator import _mark_fixed

    assert [v.fixed for v in _mark_fixed([_finding(1), _finding(2, fixable=False)], [])] == [True]
    assert _mark_fixed([], []) == []


def test_blocking_violations_are_unfixed_errors() -> None:
    from devkit_agt.features.rules import EvaluationResult, RuleExecutionError, Severity

    error = _finding(1)
    fixed = Violation("RULE-x", "a.md", 1, "fixed", fixed=True)
    warning = Violation("RULE-x", "a.md", 2, "warn", severity=Severity.WARNING)
    result = EvaluationResult(violations=[error, fixed, warning])
    assert result.blocking_violations == [error] and not result.ok
    assert EvaluationResult(violations=[fixed, warning]).ok
    assert not EvaluationResult(errors=[RuleExecutionError("boom")]).ok
