from __future__ import annotations

from pathlib import Path

from agent_rule_engine import RuleContext, WorkspaceCache
from agent_rule_engine.rules import (
    DocumentReferenceRule,
    FileLengthRule,
    IdConventionRule,
    MarkdownLinkRule,
    SpecFormatRule,
)


def test_spec_format_rule_check_and_fix(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    stories_dir = temp_workspace / "docs" / "stories"
    stories_dir.mkdir(parents=True)
    doc_path = stories_dir / "US-user-login.md"
    doc_path.write_text("# User Login\n\nAs a user, I want to log in.", encoding="utf-8")

    ctx = RuleContext(workspace_root=temp_workspace, cache=workspace_cache)
    rule = SpecFormatRule()

    # 1. Check should fail with missing frontmatter
    violations = rule.check(ctx)
    assert len(violations) == 1
    assert violations[0].rule_id == "RULE-spec-format"
    assert violations[0].fixable is True

    # 2. Fix should add frontmatter
    modified = rule.fix(ctx)
    assert "docs/stories/US-user-login.md" in modified

    # 3. Check again after fix
    workspace_cache.invalidate_all()
    violations_after = rule.check(ctx)
    assert len(violations_after) == 0

    fm, _, _ = workspace_cache.get_frontmatter(doc_path)
    assert fm is not None
    assert fm["id"] == "US-user-login"
    assert fm["title"] == "User Login"
    assert fm["status"] == "draft"


def test_id_convention_rule(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    stories_dir = temp_workspace / "docs" / "stories"
    stories_dir.mkdir(parents=True)
    doc_path = stories_dir / "invalid-stem.md"
    doc_path.write_text(
        "---\nid: BAD_ID_123\ntitle: Invalid\nstatus: draft\n---\n",
        encoding="utf-8",
    )

    ctx = RuleContext(workspace_root=temp_workspace, cache=workspace_cache)
    rule = IdConventionRule()

    violations = rule.check(ctx)
    assert len(violations) >= 1
    assert any("format" in v.message for v in violations)


def test_document_reference_rule(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    stories_dir = temp_workspace / "docs" / "stories"
    stories_dir.mkdir(parents=True)

    # Document references non-existent SPEC-payment
    doc_path = stories_dir / "US-checkout.md"
    doc_path.write_text(
        "---\nid: US-checkout\ntitle: Checkout\nstatus: active\n---\n\nDepends on SPEC-payment.",
        encoding="utf-8",
    )

    ctx = RuleContext(workspace_root=temp_workspace, cache=workspace_cache)
    rule = DocumentReferenceRule()

    violations = rule.check(ctx)
    assert any("SPEC-payment" in v.message for v in violations)


def test_markdown_link_rule_and_fix(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    docs_dir = temp_workspace / "docs"
    specs_dir = docs_dir / "specs"
    specs_dir.mkdir(parents=True)

    target_file = specs_dir / "SPEC-auth.md"
    target_file.write_text(
        "---\nid: SPEC-auth\ntitle: Auth Spec\nstatus: active\n---\n",
        encoding="utf-8",
    )

    source_dir = docs_dir / "stories"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "US-login.md"
    # Broken link pointing to wrong location
    source_file.write_text(
        "See [Spec](../wrong/SPEC-auth.md) for details.",
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
    assert "../specs/SPEC-auth.md" in text


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


def test_spec_rules_ignore_similarly_named_directory(tmp_path: Path) -> None:
    (tmp_path / "specs-backup").mkdir()
    (tmp_path / "specs-backup/invalid.md").write_text("# Not a specification\n")
    ctx = RuleContext(workspace_root=tmp_path)
    assert SpecFormatRule().check(ctx) == []
    assert SpecFormatRule().fix(ctx) == []
