from __future__ import annotations

from pathlib import Path

from devkit.rules import DocumentCatalog, WorkspaceCache


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_catalog_indexes_every_markdown_file_by_basename(tmp_path: Path) -> None:
    _write(tmp_path, "README.md", "# Root\n")
    _write(tmp_path, "docs/guide.md", "# Guide\n")
    _write(tmp_path, "src/pkg/README.md", "# Package\n")
    _write(tmp_path, "notes.txt", "not markdown\n")

    catalog = DocumentCatalog()
    catalog.build(tmp_path, WorkspaceCache(tmp_path))

    assert catalog.find_paths_by_basename("README.md") == ["README.md", "src/pkg/README.md"]
    assert catalog.find_paths_by_basename("guide.md") == ["docs/guide.md"]
    assert catalog.find_paths_by_basename("notes.txt") == []


def test_catalog_records_frontmatter_identity_verbatim(tmp_path: Path) -> None:
    _write(tmp_path, "docs/a.md", "---\nid: any-shape_42\ntitle: A\nstatus: active\n---\n")
    _write(tmp_path, "docs/b.md", "---\ntitle: No id\n---\n")
    _write(tmp_path, "docs/c.md", "# No frontmatter\n")

    catalog = DocumentCatalog()
    catalog.build(tmp_path, WorkspaceCache(tmp_path))

    doc = catalog.get_doc("any-shape_42")
    assert doc is not None
    assert (doc.path, doc.title, doc.status) == ("docs/a.md", "A", "active")
    assert catalog.has_id("any-shape_42")
    assert set(catalog.documents_by_path) == {"docs/a.md"}
    assert catalog.duplicate_ids == {}


def test_catalog_reports_duplicate_ids_in_path_order(tmp_path: Path) -> None:
    _write(tmp_path, "docs/first.md", "---\nid: dup\n---\n")
    _write(tmp_path, "docs/second.md", "---\nid: dup\n---\n")

    catalog = DocumentCatalog()
    catalog.build(tmp_path, WorkspaceCache(tmp_path))

    doc = catalog.get_doc("dup")
    assert doc is not None and doc.path == "docs/first.md"
    assert catalog.duplicate_ids == {"dup": ["docs/first.md", "docs/second.md"]}


def test_malformed_frontmatter_is_recorded_not_raised(tmp_path: Path) -> None:
    _write(tmp_path, "docs/ok.md", "---\nid: ok\n---\n")
    _write(tmp_path, "docs/broken.md", "---\nIntro text used as a thematic break\n---\nbody\n")
    _write(tmp_path, "docs/unclosed.md", "---\nnever closed\n")

    catalog = DocumentCatalog()
    catalog.build(tmp_path, WorkspaceCache(tmp_path))

    assert catalog.find_paths_by_basename("broken.md") == ["docs/broken.md"]
    assert catalog.has_id("ok")
    assert set(catalog.frontmatter_errors) == {"docs/broken.md", "docs/unclosed.md"}
    assert "mapping" in catalog.frontmatter_errors["docs/broken.md"]
