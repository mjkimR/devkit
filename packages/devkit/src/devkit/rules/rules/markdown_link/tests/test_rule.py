"""``RULE-markdown-link``: broken relative links are found, and repaired only to a unique candidate."""

from __future__ import annotations

from pathlib import Path

from devkit.rules import RuleContext, WorkspaceCache
from devkit.rules.rules.markdown_link import MarkdownLinkRule
from devkit.rules.testing import check, write_files


def _messages(root: Path) -> list[tuple[int, str]]:
    return [(v.line, v.message) for v in MarkdownLinkRule().check(RuleContext(workspace_root=root))]


def test_a_broken_link_is_reported_and_fixed(tmp_path: Path) -> None:
    write_files(
        tmp_path,
        {"docs/guides/auth.md": "# Auth\n", "docs/stories/login.md": "See [Auth](../wrong/auth.md) for details."},
    )
    cache = WorkspaceCache(tmp_path)
    ctx = RuleContext(workspace_root=tmp_path, cache=cache)
    rule = MarkdownLinkRule()

    violations = rule.check(ctx)
    assert len(violations) == 1
    assert violations[0].fixable is True

    assert len(rule.fix(ctx)) == 1
    cache.invalidate_all()
    assert "../guides/auth.md" in cache.read_text(tmp_path / "docs/stories/login.md")


def test_the_engine_marks_the_repaired_finding_fixed(tmp_path: Path) -> None:
    files = {"docs/guides/auth.md": "# Auth\n", "docs/login.md": "[Auth](wrong/auth.md)\n"}
    found = check(MarkdownLinkRule(), tmp_path, files, fix=True)
    assert [(v.file, v.fixed) for v in found] == [("docs/login.md", True)]
    assert (tmp_path / "docs/login.md").read_text() == "[Auth](guides/auth.md)\n"
    assert check(MarkdownLinkRule(), tmp_path) == []


def test_fix_needs_a_unique_candidate(tmp_path: Path) -> None:
    write_files(tmp_path, {"a/same.md": "# A\n", "b/same.md": "# B\n", "README.md": "[x](missing/same.md)\n"})
    ctx = RuleContext(workspace_root=tmp_path)
    violations = MarkdownLinkRule().check(ctx)
    assert len(violations) == 1
    assert violations[0].fixable is False
    assert MarkdownLinkRule().fix(ctx) == []


def test_link_fix_preserves_identical_link_inside_code(tmp_path: Path) -> None:
    write_files(tmp_path, {"docs/target.md": "# Target\n"})
    source = tmp_path / "README.md"
    source.write_text("`[Target](wrong/target.md)`\n[Target](wrong/target.md)\n")
    ctx = RuleContext(workspace_root=tmp_path)
    rule = MarkdownLinkRule()
    rule.fix(ctx)
    assert source.read_text() == "`[Target](wrong/target.md)`\n[Target](docs/target.md)\n"
    assert rule.check(ctx) == []


def test_valid_commonmark_destinations_are_not_broken(tmp_path: Path) -> None:
    write_files(
        tmp_path,
        {
            "t.md": "x\n",
            "my file.md": "x\n",
            "foo(1).md": "x\n",
            "a.md": '[t](t.md "Title")\n[s](my%20file.md)\n[n](<my file.md>)\n[q](t.md?plain=1)\n'
            "[u](HTTPS://example.com/x)\n[p](foo(1).md)\n[m](mailto:a@b.c)\n"
            "````md\n```\n[in fence](missing.md)\n```\n````\n",
        },
    )
    assert _messages(tmp_path) == []


def test_findings_in_document_order_with_columns(tmp_path: Path) -> None:
    write_files(tmp_path, {"a.md": "[one](x.md)\n\n- see [two](y.md)\n"})
    violations = MarkdownLinkRule().check(RuleContext(workspace_root=tmp_path))
    assert [(v.line, v.column) for v in violations] == [(1, 1), (3, 7)]


def test_fix_rewrites_only_the_destination(tmp_path: Path) -> None:
    write_files(
        tmp_path,
        {
            "docs/guides/setup guide.md": "# Setup\n",
            "docs/api.md": "# API\n",
            "docs/index.md": '[a](wrong/api.md "API reference") and [b](old/api.md#auth)\r\n'
            "[c](<old/setup guide.md>) [d](x/setup%20guide.md?v=1)\r\n",
        },
    )
    ctx = RuleContext(workspace_root=tmp_path)
    assert sorted(MarkdownLinkRule().fix(ctx)) == ["docs/index.md"]
    assert (tmp_path / "docs/index.md").read_bytes() == (
        b'[a](api.md "API reference") and [b](api.md#auth)\r\n'
        b"[c](<guides/setup guide.md>) [d](<guides/setup guide.md?v=1>)\r\n"
    )


def test_fix_skips_files_that_are_not_utf8(tmp_path: Path) -> None:
    original = b"caf\xe9 [s](wrong/setup.md)\n"
    write_files(tmp_path, {"docs/setup.md": "x\n", "a.md": original})
    ctx = RuleContext(workspace_root=tmp_path)
    assert MarkdownLinkRule().fix(ctx) == []
    assert (tmp_path / "a.md").read_bytes() == original


def test_links_leaving_the_workspace_are_not_repaired(tmp_path: Path) -> None:
    root = tmp_path / "ws"
    write_files(root, {"CHANGELOG.md": "x\n", "docs/a.md": "[upstream](../../vendor/CHANGELOG.md)\n"})
    violations = MarkdownLinkRule().check(RuleContext(workspace_root=root))
    assert [v.fixable for v in violations] == [False]
    assert MarkdownLinkRule().fix(RuleContext(workspace_root=root)) == []


def test_link_to_symlink_and_percent_encoded_nul_are_handled(tmp_path: Path) -> None:
    write_files(tmp_path, {"docs/v2.md": "x\n"})
    (tmp_path / "docs/latest.md").symlink_to("v2.md")
    write_files(tmp_path, {"a.md": "[latest](docs/latest.md) [nul](bad%00.md)\n"})
    assert [m for _, m in _messages(tmp_path)] == ["Broken relative markdown link 'bad%00.md'"]


def test_fix_encodes_candidate_names_that_link_syntax_would_alter(tmp_path: Path) -> None:
    encoded = {
        "c#sharp.md": "c%23sharp.md",
        "50%off.md": "50%25off.md",
        "why?.md": "why%3F.md",
        "back\\slash.md": "back%5Cslash.md",
        "a<b>.md": "a%3Cb%3E.md",
    }
    write_files(tmp_path, {f"docs/{name}": "x\n" for name in encoded})
    write_files(tmp_path, {"a.md": "".join(f"[x](old/{link})\n" for link in encoded.values())})
    assert MarkdownLinkRule().fix(RuleContext(workspace_root=tmp_path)) == ["a.md"]
    assert (tmp_path / "a.md").read_text() == "".join(f"[x](docs/{link})\n" for link in encoded.values())
    assert MarkdownLinkRule().check(RuleContext(workspace_root=tmp_path)) == []
