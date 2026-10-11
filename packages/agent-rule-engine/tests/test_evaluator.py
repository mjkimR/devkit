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
