from __future__ import annotations

from pathlib import Path

from agent_rule_engine import RuleContext, WorkspaceCache
from agent_rule_engine.rules import FileLengthRule, MarkdownLinkRule


def test_markdown_link_rule_and_fix(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    docs_dir = temp_workspace / "docs"
    guides_dir = docs_dir / "guides"
    guides_dir.mkdir(parents=True)

    target_file = guides_dir / "auth.md"
    target_file.write_text("# Auth\n", encoding="utf-8")

    source_dir = docs_dir / "stories"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "login.md"
    # Broken link pointing to wrong location
    source_file.write_text(
        "See [Auth](../wrong/auth.md) for details.",
        encoding="utf-8",
    )

    ctx = RuleContext(workspace_root=temp_workspace, cache=workspace_cache)
    rule = MarkdownLinkRule()

    violations = rule.check(ctx)
    assert len(violations) == 1
    assert violations[0].fixable is True

    # Fix broken link
    modified = rule.fix(ctx)
    assert len(modified) == 1

    workspace_cache.invalidate_all()
    text = workspace_cache.read_text(source_file)
    assert "../guides/auth.md" in text


def test_markdown_link_fix_needs_a_unique_candidate(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    (temp_workspace / "a").mkdir()
    (temp_workspace / "b").mkdir()
    (temp_workspace / "a" / "same.md").write_text("# A\n", encoding="utf-8")
    (temp_workspace / "b" / "same.md").write_text("# B\n", encoding="utf-8")
    source = temp_workspace / "README.md"
    source.write_text("[x](missing/same.md)\n", encoding="utf-8")

    ctx = RuleContext(workspace_root=temp_workspace, cache=workspace_cache)
    violations = MarkdownLinkRule().check(ctx)
    assert len(violations) == 1
    assert violations[0].fixable is False
    assert MarkdownLinkRule().fix(ctx) == []


def test_file_length_rule(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    doc_path = temp_workspace / "docs" / "long.md"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text("\n".join(f"Line {i}" for i in range(50)), encoding="utf-8")

    ctx = RuleContext(workspace_root=temp_workspace, cache=workspace_cache)
    rule = FileLengthRule(max_lines=30)

    violations = rule.check(ctx)
    assert len(violations) == 1
    assert "exceeds line length limit" in violations[0].message


def test_link_fix_preserves_identical_link_inside_code(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/target.md").write_text("# Target\n")
    source = tmp_path / "README.md"
    source.write_text("`[Target](wrong/target.md)`\n[Target](wrong/target.md)\n")
    ctx = RuleContext(workspace_root=tmp_path)
    rule = MarkdownLinkRule()
    rule.fix(ctx)
    assert source.read_text() == "`[Target](wrong/target.md)`\n[Target](docs/target.md)\n"
    assert rule.check(ctx) == []
