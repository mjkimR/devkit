"""Document ID aliases: parsing, shape issues and the canonical mapping of ``DocumentIndex``."""

from __future__ import annotations

from pathlib import Path

import pytest

from devkit_docs.base.errors import DuplicateIdError, UnresolvedIdError
from devkit_docs.features.documents import Document, DocumentIndex, parse_document
from devkit_docs.features.documents.models.ids import is_legacy_id


def _doc(document_id: str, aliases: str, body: str = "", field: str = "id", status: str = "active") -> str:
    return f"---\n{field}: {document_id}\nstatus: {status}\naliases: {aliases}\n---\n{body}"


def _parse(text: str, path: str = "docs/x.md") -> Document:
    document = parse_document(path, text)
    assert document is not None
    return document


@pytest.mark.parametrize(
    ("document_id", "alias"),
    [
        ("CAP-A-new", "CAP-A-old"),
        ("UC-new", "UC-old"),
        ("ARCH-05-new", "ARCH-05-old"),
        ("ADR-new", "ADR-old"),
        ("MS-new", "MS-old"),
        ("MAT-new", "MAT-old"),
        ("PROP-new", "PROP-old"),
        ("PADR-new", "PADR-old"),
        ("SPEC-new", "SPEC-old"),
        ("PLAN-new", "PLAN-old"),
        ("TASKS-new", "TASKS-old"),
        ("FB-new", "FB-old"),
    ],
)
def test_every_kind_declares_aliases(document_id: str, alias: str) -> None:
    document = _parse(_doc(document_id, f"[{alias}]"))
    assert document.aliases == (alias,) and document.alias_issues == []


def test_reconcile_id_declares_aliases() -> None:
    document = _parse(_doc("REC-new", "[REC-old]", field="reconcile_id"), "specs/2026-10/20261001-new/reconcile.md")
    assert document.aliases == ("REC-old",)


def test_aliases_are_not_references() -> None:
    document = _parse(_doc("CAP-A-new", "\n  - CAP-A-old\n  - 'CAP-A-older'", "`UC-x`\n"))
    assert document.aliases == ("CAP-A-old", "CAP-A-older")
    assert [ref.target for ref in document.references] == ["UC-x"]


def test_shape_issues() -> None:
    text = _doc(
        "CAP-A-new",
        "\n  - CAP-A-old\n  - UC-old\n  - CAP-A-new\n  - CAP-A-old\n  - not an id\n  - 3\n  - CAP-HARN-007\n",
    )
    document = _parse(text)
    assert document.aliases == ("CAP-A-old",)
    assert [(issue.line, issue.message) for issue in document.alias_issues] == [
        (6, "alias UC-old must have the document's own prefix CAP-"),
        (7, "alias CAP-A-new is the document's own ID"),
        (8, "alias CAP-A-old is repeated"),
        (9, "aliases must contain full document IDs, got 'not an id'"),
        (10, "aliases must contain string IDs"),
        (11, "alias CAP-HARN-007 has a date- or number-based form; use a slug ID"),
    ]


def test_aliases_must_be_a_list() -> None:
    document = _parse(_doc("CAP-A-new", "CAP-A-old"))
    assert document.aliases == ()
    assert [(issue.line, issue.message) for issue in document.alias_issues] == [(4, "aliases must be a list of IDs")]


@pytest.mark.parametrize(
    ("value", "legacy"),
    [
        ("ADR-0006", True),
        ("PADR-0001", True),
        ("SPEC-20261006-x", True),
        ("UC-010", True),
        ("CAP-HARN-007", True),
        ("ARCH-06", True),
        ("ARCH-05-1", True),
        ("ARCH-05-old", False),
        ("CAP-A-old", False),
        ("MS-next", False),
    ],
)
def test_legacy_forms(value: str, legacy: bool) -> None:
    assert is_legacy_id(value) is legacy


def _index(tmp_path: Path, files: dict[str, str]) -> DocumentIndex:
    for name, text in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return DocumentIndex.load(tmp_path)


def test_canonical_mapping(tmp_path: Path) -> None:
    index = _index(
        tmp_path,
        {
            "docs/new.md": _doc("CAP-A-new", "[CAP-A-old]"),
            "docs/ref.md": _doc("UC-ref", "[]", "`CAP-A-old` and `CAP-A-new`\n"),
        },
    )
    new = index.resolve("CAP-A-new")
    assert index.canonical("CAP-A-old") == (new, "CAP-A-old")
    assert index.canonical("CAP-A-new") == (new, None)
    assert index.canonical("CAP-A-none") is None
    assert index.canonical_id("CAP-A-old") == "CAP-A-new" and index.canonical_id("CAP-A-none") == "CAP-A-none"
    assert index.lookup("CAP-A-old") == (new, "CAP-A-old")
    assert index.resolve("CAP-A-old") is new
    assert [ref.target for ref in index.incoming("CAP-A-new")["UC-ref"]] == ["CAP-A-old", "CAP-A-new"]
    assert list(index.outgoing(index.resolve("UC-ref"))) == ["CAP-A-new"]
    assert index.alias_collisions() == []


def test_declared_id_wins_over_an_alias(tmp_path: Path) -> None:
    """An ID declared later (any status) shadows the alias; the collision lists every document involved."""
    index = _index(
        tmp_path,
        {
            "docs/new.md": _doc("CAP-A-new", "[CAP-A-old]"),
            "docs/old.md": _doc("CAP-A-old", "[]", status="retired"),
        },
    )
    assert index.resolve("CAP-A-old").path == "docs/old.md"
    assert [(alias, [d.path for d in docs]) for alias, docs in index.alias_collisions()] == [
        ("CAP-A-old", ["docs/old.md", "docs/new.md"])
    ]
    assert list(index.incoming("CAP-A-new")) == []


def test_alias_declared_twice_stays_ambiguous(tmp_path: Path) -> None:
    index = _index(
        tmp_path,
        {"docs/a.md": _doc("CAP-A-a", "[CAP-A-old]"), "docs/b.md": _doc("CAP-A-b", "[CAP-A-old]")},
    )
    assert index.canonical("CAP-A-old") is None
    with pytest.raises(DuplicateIdError, match="2 documents declare the alias CAP-A-old"):
        index.resolve("CAP-A-old")
    with pytest.raises(UnresolvedIdError):
        index.resolve("CAP-A-none")
    assert [alias for alias, _ in index.alias_collisions()] == ["CAP-A-old"]
