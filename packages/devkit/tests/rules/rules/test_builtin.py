from __future__ import annotations

from pathlib import Path

from devkit.rules import RuleContext, WorkspaceCache
from devkit.rules.rules import FileLengthRule, MarkdownLinkRule
from testsupport.rules import write


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


def _messages(root: Path) -> list[tuple[int, str]]:
    return [(v.line, v.message) for v in MarkdownLinkRule().check(RuleContext(workspace_root=root))]


def test_valid_commonmark_destinations_are_not_broken(tmp_path: Path) -> None:
    write(tmp_path, "t.md", "x\n")
    write(tmp_path, "my file.md", "x\n")
    write(tmp_path, "foo(1).md", "x\n")
    write(
        tmp_path,
        "a.md",
        '[t](t.md "Title")\n[s](my%20file.md)\n[n](<my file.md>)\n[q](t.md?plain=1)\n'
        "[u](HTTPS://example.com/x)\n[p](foo(1).md)\n[m](mailto:a@b.c)\n"
        "````md\n```\n[in fence](missing.md)\n```\n````\n",
    )
    assert _messages(tmp_path) == []


def test_findings_in_document_order_with_columns(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "[one](x.md)\n\n- see [two](y.md)\n")
    violations = MarkdownLinkRule().check(RuleContext(workspace_root=tmp_path))
    assert [(v.line, v.column) for v in violations] == [(1, 1), (3, 7)]


def test_fix_rewrites_only_the_destination(tmp_path: Path) -> None:
    write(tmp_path, "docs/guides/setup guide.md", "# Setup\n")
    write(tmp_path, "docs/api.md", "# API\n")
    source = write(
        tmp_path,
        "docs/index.md",
        '[a](wrong/api.md "API reference") and [b](old/api.md#auth)\r\n[c](<old/setup guide.md>) [d](x/setup%20guide.md?v=1)\r\n',
    )
    ctx = RuleContext(workspace_root=tmp_path)
    assert sorted(MarkdownLinkRule().fix(ctx)) == ["docs/index.md"]
    assert source.read_bytes() == (
        b'[a](api.md "API reference") and [b](api.md#auth)\r\n'
        b"[c](<guides/setup guide.md>) [d](<guides/setup guide.md?v=1>)\r\n"
    )


def test_fix_skips_files_that_are_not_utf8(tmp_path: Path) -> None:
    write(tmp_path, "docs/setup.md", "x\n")
    original = b"caf\xe9 [s](wrong/setup.md)\n"
    source = write(tmp_path, "a.md", original)
    ctx = RuleContext(workspace_root=tmp_path)
    assert MarkdownLinkRule().fix(ctx) == []
    assert source.read_bytes() == original


def test_links_leaving_the_workspace_are_not_repaired(tmp_path: Path) -> None:
    root = tmp_path / "ws"
    write(root, "CHANGELOG.md", "x\n")
    write(root, "docs/a.md", "[upstream](../../vendor/CHANGELOG.md)\n")
    violations = MarkdownLinkRule().check(RuleContext(workspace_root=root))
    assert [v.fixable for v in violations] == [False]
    assert MarkdownLinkRule().fix(RuleContext(workspace_root=root)) == []


def test_link_to_symlink_and_percent_encoded_nul_are_handled(tmp_path: Path) -> None:
    write(tmp_path, "docs/v2.md", "x\n")
    (tmp_path / "docs/latest.md").symlink_to("v2.md")
    write(tmp_path, "a.md", "[latest](docs/latest.md) [nul](bad%00.md)\n")
    assert [m for _, m in _messages(tmp_path)] == ["Broken relative markdown link 'bad%00.md'"]


def test_guide_path_for_classes_without_a_source_file() -> None:
    from devkit.rules.rules import guide_path

    floating = type("Floating", (FileLengthRule,), {"__module__": "not_loaded_anywhere"})
    assert guide_path(FileLengthRule()) is not None
    assert guide_path(floating()) is None


def test_fix_encodes_candidate_names_that_link_syntax_would_alter(tmp_path: Path) -> None:
    encoded = {
        "c#sharp.md": "c%23sharp.md",
        "50%off.md": "50%25off.md",
        "why?.md": "why%3F.md",
        "back\\slash.md": "back%5Cslash.md",
        "a<b>.md": "a%3Cb%3E.md",
    }
    for name in encoded:
        write(tmp_path, f"docs/{name}", "x\n")
    source = write(tmp_path, "a.md", "".join(f"[x](old/{link})\n" for link in encoded.values()))
    assert MarkdownLinkRule().fix(RuleContext(workspace_root=tmp_path)) == ["a.md"]
    assert source.read_text() == "".join(f"[x](docs/{link})\n" for link in encoded.values())
    assert MarkdownLinkRule().check(RuleContext(workspace_root=tmp_path)) == []
