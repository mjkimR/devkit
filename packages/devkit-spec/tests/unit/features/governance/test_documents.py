from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from devkit_agt.features.rules import RuleContext, WorkspaceCache

from devkit_spec.features.documents import DocumentIndex
from devkit_spec.features.governance.services.documents import document_index, field_line


def test_document_index_is_cached_per_run(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    doc_file = docs_dir / "test.md"
    doc_file.write_text(
        "---\nid: CAP-TEST-sample\ntitle: Sample Capability\nstatus: active\n---\n# Sample\n",
        encoding="utf-8",
    )

    cache = WorkspaceCache(tmp_path)
    ctx = RuleContext(workspace_root=tmp_path, cache=cache)

    with patch.object(DocumentIndex, "load", wraps=DocumentIndex.load) as mock_load:
        # First call loads and caches
        index1 = document_index(ctx)
        assert mock_load.call_count == 1
        assert index1.canonical("CAP-TEST-sample") is not None

        # Subsequent call returns cached instance without re-loading
        index2 = document_index(ctx)
        assert mock_load.call_count == 1
        assert index2 is index1


def test_document_index_invalidates_on_cache_write(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    doc_file = docs_dir / "test.md"
    doc_file.write_text(
        "---\nid: CAP-TEST-initial\ntitle: Initial Capability\nstatus: active\n---\n# Initial\n",
        encoding="utf-8",
    )

    cache = WorkspaceCache(tmp_path)
    ctx = RuleContext(workspace_root=tmp_path, cache=cache)

    index1 = document_index(ctx)
    assert index1.canonical("CAP-TEST-initial") is not None
    assert index1.canonical("CAP-TEST-updated") is None

    # Simulate autofix modifying a file via cache.write_text
    cache.write_text(
        doc_file,
        "---\nid: CAP-TEST-updated\ntitle: Updated Capability\nstatus: active\n---\n# Updated\n",
    )

    # Next call returns a fresh index reflecting the write
    index2 = document_index(ctx)
    assert index2 is not index1
    assert index2.canonical("CAP-TEST-updated") is not None


@pytest.mark.parametrize(
    ("text", "line"),
    [
        ("---\nid: X\nsummary: s\n---\n", 3),
        ("\ufeff---\nid: X\nsummary: s\n---\n", 3),
        ("--- \r\nid: X\r\nsummary : s\r\n---\r\n", 3),
        ("---\nid: X\n...\nsummary: body\n", 1),
        ("---\nnested:\n  summary: s\n---\n", 1),
        ("summary: no frontmatter\n", 1),
        ("---\nsummary: unclosed\n", 1),
    ],
)
def test_field_line_follows_the_core_grammar(text: str, line: int) -> None:
    assert field_line(text, "summary") == line
