"""The parse memo codec, its entries and the parser fingerprint (``SPEC-document-index-cache``)."""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import fields
from datetime import date, datetime, timedelta, tzinfo
from pathlib import Path
from types import FrameType
from typing import Any

import devkit_core
import pytest
import yaml
from devkit_core.core.frontmatter import load_header

import devkit_docs
from devkit_docs.features.documents import Document, Issue, Reference, parse_document
from devkit_docs.features.documents.repositories import index as index_module
from devkit_docs.features.documents.repositories import memo
from devkit_docs.features.documents.repositories.memo import (
    CODEC_FIELDS,
    UNSTORABLE,
    UNSTORABLE_RESULT,
    Invalid,
    MemoError,
    Unstorable,
    decode_entry,
    decode_value,
    digest,
    encode_entry,
    encode_value,
)

_DOCUMENT = (
    "---\n"
    "id: CAP-A-a\n"
    "status: active\n"
    "created: 2026-10-22\n"
    "aliases:\n  - CAP-A-old\n"
    "usecases:\n  - UC-b\n"
    "proposal: PROP-x\n"
    "nested:\n  2: one\n  true: yes\n  null: none\n  2026-01-02: day\n"
    "---\n"
    "# [CAP-A-a] Title\n\nSee `UC-b` and [UC-c].\n"
)


class _Zone(tzinfo):
    """A zone that is not a fixed ``timezone`` offset."""

    def utcoffset(self, dt: datetime | None) -> timedelta:
        return timedelta(hours=9)

    def dst(self, dt: datetime | None) -> timedelta:
        return timedelta(0)


def _round_trip(value: object) -> Any:
    return decode_value(json.loads(json.dumps(encode_value(value), allow_nan=False)))


def test_frontmatter_values_round_trip_with_their_types_and_key_order() -> None:
    header = (
        "day: 2026-10-22\n"
        "naive: 2026-10-22 10:11:12.5\n"
        "utc: 2026-10-22T10:11:12Z\n"
        "seoul: 2026-10-22T10:11:12+09:00\n"
        "nested:\n  2: int\n  true: bool\n  null: none\n  2026-01-02: date\n  z: last\n"
        "tagged:\n  l: [1]\n"
        "other:\n  m: x\n  d: '2026-01-01'\n"
        "values: [1, 1.5, -0.0, true, null, '', 'é', [a, {b: c}]]\n"
    )
    data = load_header(header)
    assert _round_trip(data) == data
    decoded = _round_trip(data)
    assert list(decoded) == list(data) and list(decoded["nested"]) == list(data["nested"])
    assert type(decoded["day"]) is date and type(decoded["naive"]) is datetime
    assert decoded["utc"].utcoffset() == timedelta(0) and decoded["seoul"].utcoffset() == timedelta(hours=9)
    assert decoded["tagged"] == {"l": [1]} and decoded["other"] == {"m": "x", "d": "2026-01-01"}
    assert [type(value) for value in decoded["values"][:3]] == [int, float, float]


@pytest.mark.parametrize(
    "value",
    [
        {"x": float("nan")},
        {"x": float("inf")},
        {"x": {1, 2}},
        {"x": b"bytes"},
        {"x": (1, 2)},
        {"x": object()},
        {"x": datetime(2026, 1, 1, tzinfo=_Zone())},
    ],
)
def test_values_the_codec_cannot_store_are_refused(value: object) -> None:
    with pytest.raises(Unstorable):
        encode_value(value)


def test_a_cycle_is_unstorable_and_a_shared_value_is_not() -> None:
    shared = [1]
    assert _round_trip({"a": shared, "b": shared}) == {"a": [1], "b": [1]}
    cycle: list[object] = []
    cycle.append(cycle)
    with pytest.raises(Unstorable):
        encode_value(cycle)


@pytest.mark.parametrize(
    "stored",
    [
        {"x": 1},
        {"l": [1], "m": []},
        {"l": "no list"},
        {"m": [[1]]},
        {"m": [[{"l": []}, 1]]},
        {"m": [["a", 1], ["a", 2]]},
        {"d": "2026-13-01"},
        {"d": "20261022"},
        {"t": 5},
        {"t": "2026-10-22"},
        float("nan"),
        [1],
    ],
)
def test_stored_values_the_codec_cannot_have_written_are_refused(stored: object) -> None:
    with pytest.raises(MemoError):
        decode_value(stored)


def test_document_entries_round_trip() -> None:
    document = parse_document("docs/a.md", _DOCUMENT)
    assert document is not None and document.references and document.provenance and document.aliases
    text_digest = digest(_DOCUMENT)
    entry = json.loads(json.dumps(encode_entry(text_digest, document)))
    assert entry[0] == text_digest
    assert decode_entry("docs/a.md", entry) == document


def test_no_document_invalid_and_unstorable_entries() -> None:
    assert decode_entry("docs/a.md", encode_entry("d", None)) is None
    assert decode_entry("docs/a.md", encode_entry("d", Invalid("bad"))) == Invalid("bad")
    document = parse_document("docs/a.md", "---\nid: CAP-A-a\nx: .nan\n---\n")
    entry = encode_entry("d", document)
    assert entry == ["d", UNSTORABLE]
    assert decode_entry("docs/a.md", entry) is UNSTORABLE_RESULT


def test_a_digest_is_of_the_exact_text() -> None:
    assert digest("a\r\nb") != digest("a\nb")
    assert digest("\ud800") != digest("\ud801")


def _payload() -> list[Any]:
    document = parse_document("docs/a.md", _DOCUMENT)
    return json.loads(json.dumps(encode_entry("d", document)))[2]


@pytest.mark.parametrize(
    "broken",
    [
        lambda p: p[:8],
        lambda p: [1, *p[1:]],
        lambda p: [p[0], "usecase", *p[2:]],
        lambda p: [p[0], "nonsense", *p[2:]],
        lambda p: [*p[:2], {"l": []}, *p[3:]],
        lambda p: [*p[:3], [["UC-b", "body", 1, 1, 1, 1, "no"]], *p[4:]],
        lambda p: [*p[:3], [["UC-b", "body", 1, 1, 1]], *p[4:]],
        lambda p: [*p[:3], "refs", *p[4:]],
        lambda p: [*p[:5], [[True, "x"]], *p[6:]],
        lambda p: [*p[:6], [5], *p[7:]],
        lambda p: [*p[:7], [[1]], *p[8:]],
        lambda p: [*p[:8], [["1", "x"]]],
    ],
)
def test_document_entries_that_cannot_be_rebuilt_are_refused(broken: Any) -> None:
    with pytest.raises(MemoError):
        decode_entry("docs/a.md", ["d", "d", broken(_payload())])


@pytest.mark.parametrize("entry", [["d"], ["d", "x"], ["d", "n", 1], ["d", "e"], ["d", "e", 1], ["d", "d"]])
def test_entries_without_a_known_shape_are_refused(entry: list[Any]) -> None:
    with pytest.raises(MemoError):
        decode_entry("docs/a.md", entry)


def _traced_files() -> set[str]:
    """The ``devkit_docs`` and ``devkit_core`` source files whose code runs while documents are read, parsed,
    encoded and decoded."""
    roots = (str(Path(devkit_docs.__file__).parent), str(Path(devkit_core.__file__).parent))
    seen: set[str] = set()

    def profile(frame: FrameType, event: str, arg: object) -> None:
        name = frame.f_code.co_filename
        if name.startswith(roots):
            seen.add(name)

    texts = [_DOCUMENT, "---\nid: CAP-A-a\nid: twice\n---\n", "---\nid: 5\n---\n", "---\nnever closed\n", "plain\n"]
    sys.setprofile(profile)
    try:
        for text in texts:
            result = index_module._fresh("docs/a.md", text)
            entry = json.loads(json.dumps(encode_entry(digest(text), result)))
            decode_entry("docs/a.md", entry)
    finally:
        sys.setprofile(None)
    return seen


def _uncovered(modules: tuple[str, ...]) -> set[str]:
    covered = set()
    for name in modules:
        spec = importlib.util.find_spec(name)
        assert spec is not None and spec.origin is not None
        covered.add(spec.origin)
    return _traced_files() - covered


def test_every_module_on_the_read_parse_and_codec_path_is_in_the_fingerprint() -> None:
    assert _uncovered(memo.fingerprint_modules()) == set()


def test_a_module_missing_from_the_fingerprint_is_found() -> None:
    modules = tuple(name for name in memo.fingerprint_modules() if name != "devkit_core.core.frontmatter")
    assert [Path(path).name for path in _uncovered(modules)] == ["frontmatter.py"]


def test_the_fingerprint_covers_versions_and_sources() -> None:
    modules = memo.fingerprint_modules()
    assert "devkit_docs.features.documents.repositories.memo" in modules
    assert "devkit_docs.features.documents.models.parse" in modules
    assert {"devkit_core.core.frontmatter", "devkit_core.core.yaml", "devkit_core.base.errors"} <= set(modules)
    assert memo.fingerprint() == memo.fingerprint() and memo.fingerprint() is not None
    assert yaml.__version__  # part of the fingerprint


def test_the_codec_stores_every_field_of_documents_references_and_issues() -> None:
    for kind in (Document, Reference, Issue):
        assert tuple(field.name for field in fields(kind)) == CODEC_FIELDS[kind], kind.__name__
