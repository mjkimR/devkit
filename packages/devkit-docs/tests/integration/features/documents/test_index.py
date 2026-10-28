from __future__ import annotations

import os
from pathlib import Path

import pytest
from docs_support.types import Write

from devkit_docs.base.errors import DuplicateIdError, UnresolvedIdError
from devkit_docs.features.documents import DocumentIndex


def _doc(document_id: str, body: str = "", status: str = "active") -> str:
    return f"---\nid: {document_id}\nstatus: {status}\n---\n{body}"


def test_only_documents_under_docs_and_specs_are_indexed(workspace: Path, write: Write) -> None:
    write("docs/a.md", _doc("CAP-A-a"))
    write("specs/2026-10/20261001-b/spec.md", _doc("SPEC-b"))
    for skipped in ("README.md", "x-template.md", "x_template.md", ".hidden/c.md", "notes.txt"):
        write(f"docs/{skipped}", _doc("CAP-A-skipped"))
    write("other/d.md", _doc("CAP-A-d"))
    os.symlink(workspace / "docs/a.md", workspace / "docs/link.md")
    # Symlinked directory is skipped
    write("outside/target.md", _doc("CAP-A-target"))
    os.symlink(workspace / "outside", workspace / "docs/sym_dir")
    # Nested hidden directory is skipped
    write("docs/nested/.secret/hidden.md", _doc("CAP-A-nested-hidden"))
    write("docs/nested/visible.md", _doc("CAP-A-nested-visible"))
    index = DocumentIndex.load(workspace)
    assert [document.path for document in index.documents] == [
        "docs/a.md",
        "docs/nested/visible.md",
        "specs/2026-10/20261001-b/spec.md",
    ]


def test_a_malformed_file_is_a_warning_and_the_rest_is_indexed(workspace: Path, write: Write) -> None:
    write("docs/a.md", _doc("CAP-A-a"))
    write("docs/bad.md", "---\nid: CAP-A-bad\nid: again\n---\n")
    index = DocumentIndex.load(workspace)
    assert [document.id for document in index.documents] == ["CAP-A-a"]
    (problem,) = index.problems
    assert problem.code == "DOCS_DOCUMENT_INVALID" and problem.target_files == ("docs/bad.md",)


def test_resolve(workspace: Path, write: Write) -> None:
    write("docs/a.md", _doc("CAP-A-a"))
    write("docs/b.md", _doc("UC-dup"))
    write("docs/c.md", _doc("UC-dup"))
    index = DocumentIndex.load(workspace)
    assert index.resolve("CAP-A-a").path == "docs/a.md"
    with pytest.raises(UnresolvedIdError):
        index.resolve("CAP-A-none")
    with pytest.raises(DuplicateIdError) as caught:
        index.resolve("UC-dup")
    assert caught.value.target_files == ("docs/b.md", "docs/c.md")


def test_references_in_both_directions(workspace: Path, write: Write) -> None:
    write("docs/a.md", _doc("CAP-A-a", "`UC-b` `UC-c` [UC-b]\n"))
    write("docs/b.md", _doc("UC-b", "`CAP-A-a`\n"))
    index = DocumentIndex.load(workspace)
    outgoing = index.outgoing(index.resolve("CAP-A-a"))
    assert {key: len(refs) for key, refs in outgoing.items()} == {"UC-b": 2, "UC-c": 1}
    assert list(index.incoming("UC-b")) == ["CAP-A-a"]
    assert list(index.incoming("CAP-A-a")) == ["UC-b"]


def test_files_of_completed_spec_bundles_are_historical(workspace: Path, write: Write) -> None:
    write("specs/2026-10/20261001-done/spec.md", _doc("SPEC-done", status="completed"))
    write("specs/2026-10/20261001-done/plan.md", _doc("PLAN-done"))
    write("specs/2026-10/20261002-open/spec.md", _doc("SPEC-open", status="draft"))
    write("specs/2026-10/feedback/20261003-x.md", _doc("FB-x"))
    write("specs/2026-10/20261001-done/feedback/y.md", _doc("FB-y", status="open"))
    index = DocumentIndex.load(workspace)
    # Feedback has its own lifecycle: a completed bundle's feedback stays current.
    assert {document.id: index.is_historical(document) for document in index.documents} == {
        "SPEC-done": True,
        "PLAN-done": True,
        "SPEC-open": False,
        "FB-x": False,
        "FB-y": False,
    }


def test_a_completed_status_is_read_case_insensitively(workspace: Path, write: Write) -> None:
    write("specs/2026-10/20261001-done/spec.md", _doc("SPEC-done", status="Completed"))
    write("specs/2026-10/20261001-done/plan.md", _doc("PLAN-done"))
    index = DocumentIndex.load(workspace)
    assert all(index.is_historical(document) for document in index.documents)


def test_symlinked_source_directory_is_skipped(workspace: Path, write: Write) -> None:
    write("external_docs/doc.md", _doc("CAP-A-ext"))
    os.symlink(workspace / "external_docs", workspace / "docs")
    write("specs/2026-10/20261001-b/spec.md", _doc("SPEC-b"))
    index = DocumentIndex.load(workspace)
    assert [document.path for document in index.documents] == ["specs/2026-10/20261001-b/spec.md"]


def test_walk_traversal_deterministic_order(workspace: Path, write: Write) -> None:
    write("docs/z_dir/b.md", _doc("CAP-B"))
    write("docs/z_dir/a.md", _doc("CAP-A"))
    write("docs/a_dir/b.md", _doc("CAP-C"))
    write("docs/a_dir/a.md", _doc("CAP-D"))
    from devkit_docs.features.documents.repositories.index import _files

    paths = [rel for _, rel in _files(workspace)]
    assert paths == [
        "docs/a_dir/a.md",
        "docs/a_dir/b.md",
        "docs/z_dir/a.md",
        "docs/z_dir/b.md",
    ]
