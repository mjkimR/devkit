from __future__ import annotations

from pathlib import Path

from agent_rule_engine import WorkspaceCache


def test_cache_read_text_and_invalidation(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    doc_path = temp_workspace / "sample.md"
    doc_path.write_text("initial content", encoding="utf-8")

    # First read
    assert workspace_cache.read_text("sample.md") == "initial content"

    # Modify underlying file directly
    doc_path.write_text("updated content", encoding="utf-8")
    # Cached value should still be returned
    assert workspace_cache.read_text("sample.md") == "initial content"

    # Invalidate cache
    workspace_cache.invalidate("sample.md")
    assert workspace_cache.read_text("sample.md") == "updated content"


def test_cache_frontmatter_parsing(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    doc_path = temp_workspace / "doc.md"
    content = "---\nid: US-test\ntitle: Test Story\nstatus: active\n---\n\n# Body here"
    doc_path.write_text(content, encoding="utf-8")

    fm, body, line_count = workspace_cache.get_frontmatter("doc.md")
    assert fm is not None
    assert fm["id"] == "US-test"
    assert fm["title"] == "Test Story"
    assert "# Body here" in body
    assert line_count > 0


def test_cache_markdown_links(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    doc_path = temp_workspace / "doc.md"
    content = "Check [Specification](./specs/SPEC-auth.md) and [External](https://example.com)."
    doc_path.write_text(content, encoding="utf-8")

    links = workspace_cache.get_links("doc.md")
    assert len(links) == 2
    assert links[0].text == "Specification"
    assert links[0].target == "./specs/SPEC-auth.md"
    assert links[1].text == "External"
    assert links[1].target == "https://example.com"


def test_frontmatter_delimiters_inside_values(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    (temp_workspace / "doc.md").write_text('---\ntitle: "before---after"\n---\n# Body\n')
    fm, body, offset = workspace_cache.get_frontmatter("doc.md")
    assert fm == {"title": "before---after"}
    assert body == "# Body\n"
    assert offset == 3


def test_file_listing_cached_and_invalidated(temp_workspace: Path, workspace_cache: WorkspaceCache) -> None:
    (temp_workspace / "b.md").touch()
    ignored = temp_workspace / ".venv"
    ignored.mkdir()
    (ignored / "ignored.md").touch()
    assert workspace_cache.find_files(temp_workspace) == [temp_workspace / "b.md"]
    (temp_workspace / "a.md").touch()
    assert workspace_cache.find_files(temp_workspace) == [temp_workspace / "b.md"]
    workspace_cache.invalidate("a.md")
    assert workspace_cache.find_files(temp_workspace) == [temp_workspace / "a.md", temp_workspace / "b.md"]
