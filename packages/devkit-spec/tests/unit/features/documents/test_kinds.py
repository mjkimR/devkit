"""The kind definition table: one row per ``Kind`` member, and the ID grammar built from it."""

from __future__ import annotations

from dataclasses import replace

import pytest

from devkit_spec.features.documents import TERMINAL_STATUSES, Kind, KindTableError, definition, definitions, kind_of
from devkit_spec.features.documents.models import ids, kinds
from devkit_spec.features.documents.models.kinds import ROWS, Summary, by_prefix, relation_prefixes, validate
from devkit_spec.features.documents.repositories import memo


def test_the_table_holds_one_row_per_member_in_enum_order() -> None:
    assert [row.kind for row in definitions()] == list(Kind)
    assert all(definition(kind).kind is kind for kind in Kind)


def test_the_id_grammar_keeps_its_values() -> None:
    assert list(ids.PREFIXES.items()) == [
        ("CAP", Kind.CAPABILITY),
        ("UC", Kind.USECASE),
        ("UX", Kind.UX),
        ("ARCH", Kind.ARCHITECTURE),
        ("ADR", Kind.DECISION),
        ("PROP", Kind.PROPOSAL),
        ("PADR", Kind.PROPOSAL_DECISION),
        ("SPEC", Kind.SPEC),
        ("PLAN", Kind.PLAN),
        ("TASKS", Kind.TASKS),
        ("REC", Kind.RECONCILE),
        ("FB", Kind.FEEDBACK),
        ("MAT", Kind.MATERIAL),
        ("MS", Kind.MILESTONE),
    ]
    assert ids.ID_SOURCE == r"(?:CAP|UC|UX|ARCH|ADR|PROP|PADR|SPEC|PLAN|TASKS|REC|FB|MAT|MS)-[A-Za-z0-9][A-Za-z0-9_-]*"
    assert kind_of("UX-login") is Kind.UX
    assert kind_of("MS-roadmap") is Kind.MILESTONE and kind_of("XX-a") is None and kind_of("MS-") is None
    assert {
        Kind.FEEDBACK: frozenset({"resolved", "promoted", "dismissed", "forwarded"}),
        Kind.DECISION: frozenset({"superseded"}),
        Kind.PROPOSAL: frozenset({"rejected"}),
    } == TERMINAL_STATUSES


def test_the_rows_keep_each_kind_fact() -> None:
    def kinds_where(predicate) -> set[Kind]:
        return {row.kind for row in definitions() if predicate(row)}

    assert kinds_where(lambda row: row.living_spec) == {Kind.CAPABILITY, Kind.USECASE, Kind.UX, Kind.ARCHITECTURE}
    assert kinds_where(lambda row: row.area_scoped) == {Kind.CAPABILITY, Kind.USECASE, Kind.UX}
    assert kinds_where(lambda row: row.entrypoints) == {Kind.CAPABILITY, Kind.USECASE}
    assert {row.prefix for row in definitions() if row.heading_token} == {
        "SPEC", "PLAN", "TASKS", "REC", "ADR", "FB", "CAP", "UC", "UX", "ARCH", "MS",
    }  # fmt: skip
    assert kinds_where(lambda row: row.summary is Summary.ALWAYS) == {
        Kind.CAPABILITY, Kind.USECASE, Kind.UX, Kind.DECISION, Kind.ARCHITECTURE, Kind.MILESTONE,
    }  # fmt: skip
    assert {row.kind: row.anchor for row in definitions() if row.summary is Summary.ANCHOR} == {
        Kind.PROPOSAL: "proposal.md",
        Kind.SPEC: "spec.md",
    }
    assert {row.kind: row.default_status for row in definitions() if row.default_status != "draft"} == {
        Kind.FEEDBACK: "open",
        Kind.MILESTONE: "planned",
    }
    assert relation_prefixes() == {
        "usecases": "UC-",
        "related_usecases": "UC-",
        "capabilities": "CAP-",
        "related_capabilities": "CAP-",
        "spec": "SPEC-",
        "plan": "PLAN-",
        "milestone": "MS-",
        "depends_on": "MS-",
    }


def test_by_prefix_reads_the_prefix_before_the_first_dash() -> None:
    assert by_prefix("MS--odd") is definition(Kind.MILESTONE)
    assert by_prefix("FB-x") is definition(Kind.FEEDBACK)
    assert by_prefix("MS") is None and by_prefix("MSX-a") is None


@pytest.mark.parametrize(
    ("rows", "fragment"),
    [
        (ROWS[:-1], "missing: milestone"),
        ((ROWS[1], ROWS[0], *ROWS[2:]), "enum order"),
        ((*ROWS, ROWS[-1]), "enum order"),
        ((replace(ROWS[0], prefix="UC"), *ROWS[1:]), "prefix 'UC'"),
        ((replace(ROWS[0], prefix="cap"), *ROWS[1:]), "prefix 'cap'"),
        ((replace(ROWS[0], relation_fields=("plan",)), *ROWS[1:]), "relation field 'plan'"),
        ((replace(ROWS[0], summary=Summary.ANCHOR), *ROWS[1:]), "anchor file"),
        ((replace(ROWS[0], anchor="x.md"), *ROWS[1:]), "anchor file"),
        ((replace(ROWS[0], directory=""), *ROWS[1:]), "needs a directory"),
    ],
    ids=[
        "missing",
        "reordered",
        "extra",
        "duplicate-prefix",
        "lower-prefix",
        "shared-field",
        "anchorless",
        "anchor",
        "directory",
    ],
)
def test_an_inconsistent_table_is_refused(rows, fragment: str) -> None:
    with pytest.raises(KindTableError, match=fragment):
        validate(rows)


def test_a_kind_without_a_row_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kinds, "_TABLE", ROWS[:-1])
    with pytest.raises(KindTableError, match="milestone has no row"):
        definition(Kind.MILESTONE)


def test_the_parse_memo_fingerprint_covers_the_table() -> None:
    assert "devkit_spec.features.documents.models.kinds" in memo.fingerprint_modules()
