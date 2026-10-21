"""Typed direct edges, terminal history and changed-path cycle diagnostics."""

from pathlib import Path

import pytest
from devkit.rules.testing import check

from devkit_spec.documents import DocumentIndex, parse_document
from devkit_spec.documents.dependencies import cycle_members, target_problem
from devkit_spec.rules.document_reference import DocumentReferenceRule


def doc(name: str, edges: str = "", status: str = "draft") -> str:
    return f"---\nid: {name}\nstatus: {status}\n{edges}---\n"


@pytest.mark.parametrize(
    "edges,issues",
    [
        ("", False),
        ("depends_on: []\n", False),
        ("depends_on: [PROP-a, SPEC-b]\n", False),
        ("depends_on: PROP-a\n", True),
        ("depends_on: [1]\n", True),
        ("depends_on: null\n", True),
    ],
)
def test_anchor_field_shapes(edges: str, issues: bool) -> None:
    parsed = parse_document("docs/proposals/PROP-x/proposal.md", doc("PROP-x", edges))
    assert parsed is not None
    assert bool(parsed.issues) is issues


@pytest.mark.parametrize(
    "target,path",
    [
        ("MS-a", "docs/roadmap/MS-a.md"),
        ("SPEC-a", "specs/2026-10/a/other.md"),
        ("PROP-a", "docs/proposals/PROP-a/target-docs.md"),
        ("CAP-A-a", "docs/a.md"),
    ],
)
def test_dependency_targets_are_exact_anchors(tmp_path: Path, target: str, path: str) -> None:
    files = {"docs/proposals/PROP-x/proposal.md": doc("PROP-x", f"depends_on: [{target}]\n"), path: doc(target)}
    found = check(DocumentReferenceRule(), tmp_path, files)
    assert any("depends_on" in v.message for v in found)


def test_mixed_cycle_and_completed_terminal(tmp_path: Path) -> None:
    a, b = "docs/proposals/PROP-a/proposal.md", "specs/2026-10/b/spec.md"
    files = {a: doc("PROP-a", "depends_on: [SPEC-b]\n"), b: doc("SPEC-b", "depends_on: [PROP-a]\n", "in-progress")}
    found = check(DocumentReferenceRule(), tmp_path, files, targets=[a])
    assert any(v.file == a and "unit dependency cycle" in v.message for v in found)
    files[b] = doc("SPEC-b", "depends_on: [PROP-a]\n", "completed")
    assert check(DocumentReferenceRule(), tmp_path, files, targets=[a]) == []
    index = DocumentIndex.load(tmp_path)
    assert not cycle_members(index)
    assert target_problem(index, "SPEC-b") is None


def test_missing_ambiguous_self_and_namespaced_edges(tmp_path: Path) -> None:
    a = "docs/proposals/PROP-a/proposal.md"
    files = {
        a: doc("PROP-a", "depends_on: [PROP-a, SPEC-missing, PROP-b]\n"),
        "docs/packages/pkg/proposals/PROP-b/proposal.md": doc("PROP-b"),
        "docs/duplicate.md": doc("PROP-b"),
    }
    messages = [v.message for v in check(DocumentReferenceRule(), tmp_path, files)]
    assert any("cycle" in m for m in messages)
    assert any("SPEC-missing resolves to 0" in m for m in messages)
    assert any("PROP-b resolves to 2" in m for m in messages)


def test_spec_milestone_is_not_membership(workspace: Path, write) -> None:
    write("docs/roadmap/MS-theme.md", doc("MS-theme"))
    write("specs/2026-10/x/spec.md", doc("SPEC-x", "milestone: MS-theme\n"))
    write("docs/proposals/PROP-y/proposal.md", doc("PROP-y", "milestone: MS-theme\n"))
    assert set(DocumentIndex.load(workspace).incoming("MS-theme")) == {"PROP-y"}


def test_handoff_autofix_requires_an_exact_spec_anchor(tmp_path: Path) -> None:
    source = "docs/proposals/PROP-next/proposal.md"
    original = doc("PROP-next", "depends_on: [PROP-old]\n")
    files = {source: original, "specs/2026-10/old/other.md": doc("SPEC-old")}
    check(DocumentReferenceRule(), tmp_path, files, fix=True)
    assert (tmp_path / source).read_text() == original
    files = {source: original, "specs/2026-10/old/spec.md": doc("SPEC-old", status="completed")}
    (tmp_path / "specs/2026-10/old/other.md").unlink()
    check(DocumentReferenceRule(), tmp_path, files, fix=True)
    assert "depends_on: [SPEC-old]" in (tmp_path / source).read_text()
