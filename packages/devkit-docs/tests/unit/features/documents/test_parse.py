from __future__ import annotations

import pytest
from devkit_core.core import FrontmatterError

from devkit_docs.features.documents import Kind, is_id, kind_of, parse_document


def _refs(text: str) -> list[tuple[str, str, int, bool]]:
    document = parse_document("docs/x.md", text)
    assert document is not None
    return [(ref.target, ref.field, ref.line, ref.bracket) for ref in document.references]


def _doc(body: str, header: str = "id: CAP-CORE-x\nstatus: active\n") -> str:
    return f"---\n{header}---\n{body}"


@pytest.mark.parametrize(
    ("value", "kind"),
    [("CAP-CORE-x", Kind.CAPABILITY), ("UC-a_b-c", Kind.USECASE), ("REC-x", Kind.RECONCILE), ("MAT-9", Kind.MATERIAL)],
)
def test_ids_name_their_kind(value: str, kind: Kind) -> None:
    assert is_id(value) and kind_of(value) is kind


@pytest.mark.parametrize("value", ["CAP-", "cap-x", "CAP--x", "XYZ-x", "CAP-x y", " CAP-x"])
def test_malformed_ids(value: str) -> None:
    assert not is_id(value) and kind_of(value) is None


def test_identity_and_fields() -> None:
    document = parse_document("docs/c.md", _doc("", "id: CAP-CORE-x\ntitle: X\nstatus: active\narea: core\n"))
    assert document is not None
    assert (document.id, document.kind, document.title, document.status, document.area) == (
        "CAP-CORE-x",
        Kind.CAPABILITY,
        "X",
        "active",
        "core",
    )


def test_a_reconcile_file_is_identified_by_reconcile_id() -> None:
    document = parse_document("specs/m/b/reconcile.md", "---\nreconcile_id: REC-b\n---\n")
    assert document is not None and document.id == "REC-b" and document.kind is Kind.RECONCILE


@pytest.mark.parametrize("text", ["no frontmatter\n", "---\ntitle: x\n---\n", "---\nid: not-an-id\n---\n"])
def test_files_without_a_well_formed_id_are_not_documents(text: str) -> None:
    assert parse_document("docs/x.md", text) is None


@pytest.mark.parametrize("text", ["---\nid: [CAP-x]\n---\n", "---\nid: CAP-x\nstatus: 3\n---\n", "---\nid: CAP-x\n"])
def test_malformed_frontmatter_raises(text: str) -> None:
    with pytest.raises(FrontmatterError):
        parse_document("docs/x.md", text)


def test_frontmatter_references_keep_their_positions() -> None:
    text = _doc("", "id: CAP-CORE-x\nusecases:\n  - UC-a\n  - 'UC-b'\nspec: SPEC-s\nproposal: PROP-p\n")
    document = parse_document("docs/x.md", text)
    assert document is not None
    assert [(r.target, r.field, r.line, r.column) for r in document.references] == [
        ("UC-a", "usecases", 4, 5),
        ("UC-b", "usecases", 5, 5),
        ("SPEC-s", "spec", 6, 7),
    ]
    assert [text[r.start : r.end] for r in document.references] == ["UC-a", "'UC-b'", "SPEC-s"]
    assert [(r.target, r.field) for r in document.provenance] == [("PROP-p", "proposal")]


def test_malformed_reference_fields_are_issues() -> None:
    document = parse_document(
        "docs/x.md", _doc("", "id: CAP-CORE-x\nusecases: UC-a\nspec: [SPEC-s]\ncapabilities: [1]\n")
    )
    assert document is not None and document.references == []
    assert [(issue.line, issue.message) for issue in document.issues] == [
        (3, "usecases must be a list of IDs"),
        (5, "capabilities must contain string IDs"),
        (4, "spec must be one ID"),
    ]


def test_body_references() -> None:
    body = "# [CAP-CORE-x] Title\n\nSee `UC-a` and [ADR-b], not `UC-a b` or `x UC-c`.\n"
    assert _refs(_doc(body)) == [("UC-a", "body", 7, False), ("ADR-b", "body", 7, True)]


def test_body_reference_positions() -> None:
    text = _doc("intro\n  uses `UC-a` here\n")
    document = parse_document("docs/x.md", text)
    assert document is not None
    (ref,) = document.references
    assert (ref.line, ref.column, text[ref.start : ref.end]) == (6, 9, "UC-a")


@pytest.mark.parametrize(
    "body",
    [
        "```\n`UC-a`\n```\n",
        "~~~~md\n[UC-a]\n~~~\n~~~~\n",
        "    `UC-a` indented code\n",
        "<!-- `UC-a`\n[UC-b] -->\n",
        "``code `UC-a` code``\n",
        "~~`UC-a`~~\n",
        "[UC-a](path.md) ![UC-b] [UC-c][ref] [UC-d]: x\n",
        "\\[UC-a\\] \\`UC-b\\`\n",
        "`code\n`UC-a` [UC-b]\nend` after\n",
        "~~gone\n`UC-a`~~\n",
    ],
)
def test_non_prose_is_not_referenced(body: str) -> None:
    assert _refs(_doc(body)) == []


@pytest.mark.parametrize(
    "body",
    [
        "Type \\<!-- to open a comment.\n\nSee `UC-a` here.\n",
        "Type <!-- to open a comment.\n\nSee `UC-a` here.\n",
        "Type `<!--` to open a comment.\nSee `UC-a` here.\n",
        "Type <!-- to open a comment.\n```\ncode\n```\nSee `UC-a` here.\n",
    ],
)
def test_a_literal_comment_opener_hides_nothing_after_it(body: str) -> None:
    assert [ref[0] for ref in _refs(_doc(body))] == ["UC-a"]


def test_a_heading_does_not_reference_its_own_document() -> None:
    assert _refs(_doc("# `CAP-CORE-x` and `UC-a`\n## `CAP-CORE-x`\n")) == [
        ("UC-a", "body", 5, False),
        ("CAP-CORE-x", "body", 6, False),
    ]


def test_crlf_line_endings() -> None:
    text = "---\r\nid: CAP-CORE-x\r\nusecases:\r\n  - UC-a\r\n---\r\nsee `UC-b`\r\n"
    assert _refs(text) == [("UC-a", "usecases", 4, False), ("UC-b", "body", 6, False)]


def test_a_span_ends_with_its_paragraph() -> None:
    assert _refs(_doc("`open\n\n`UC-a`\n")) == [("UC-a", "body", 7, False)]
    assert _refs(_doc("``open `UC-a`\n~~~\n")) == [("UC-a", "body", 5, False)]


@pytest.mark.parametrize("fence", ["```", "~~~", "   ```"])
def test_a_fence_interrupts_a_stray_span(fence: str) -> None:
    # A stray backtick never swallows the fence opener: the block stays code and the text after it stays prose.
    body = f"a stray ` here\n{fence}\n`UC-inside` and ` again\n{fence.strip()}\n\nafter `UC-a`\n"
    assert _refs(_doc(body)) == [("UC-a", "body", 10, False)]


def test_text_after_a_multiline_span_stays_visible() -> None:
    assert _refs(_doc("`a\nb` `UC-a`\n")) == [("UC-a", "body", 6, False)]


@pytest.mark.parametrize(
    "body",
    [
        "- item\n    `UC-a` continued\n",
        "- item\n\n    `UC-a` a paragraph of the item\n",
        "1. item\n    - nested `UC-a`\n",
        "text\n    `UC-a` continues the paragraph\n",
    ],
)
def test_indented_prose_is_referenced(body: str) -> None:
    assert [target for target, *_ in _refs(_doc(body))] == ["UC-a"]


@pytest.mark.parametrize("body", ["    `UC-a`\n", "text\n\n    `UC-a`\n", "text\n\n    code\n\n    `UC-a`\n"])
def test_indented_code_is_not(body: str) -> None:
    assert _refs(_doc(body)) == []
