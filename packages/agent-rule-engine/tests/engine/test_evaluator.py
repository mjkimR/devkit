from __future__ import annotations

from pathlib import Path

from agent_rule_engine import Phase, RuleContext, WorkspaceCache, default_registry, evaluate


def test_evaluator_autofix_convergence(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    # Setup a story without frontmatter
    stories_dir = temp_workspace / "docs" / "stories"
    stories_dir.mkdir(parents=True)
    doc_path = stories_dir / "US-agent-workflow.md"
    doc_path.write_text("# Agent Workflow\n\nAgent workflow documentation.", encoding="utf-8")

    ctx = RuleContext(
        workspace_root=temp_workspace,
        cache=workspace_cache,
        phase=Phase.LINTER,
        fix=True,
    )
    registry = default_registry()

    result = evaluate(ctx, registry.get_all())
    # The violation should be marked as fixed!
    assert any(v.rule_id == "RULE-spec-format" and v.fixed for v in result.violations)
    assert not result.has_errors

    # Now verify the file on disk has valid frontmatter
    content = doc_path.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "id: US-agent-workflow" in content


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
    from agent_rule_engine import Violation
    from agent_rule_engine.rules import BaseRule

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
    from agent_rule_engine.rules import BaseRule

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
