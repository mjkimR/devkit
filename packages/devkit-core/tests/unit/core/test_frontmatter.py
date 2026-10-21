from __future__ import annotations

import datetime

import pytest
from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import locate, parse


def test_no_frontmatter_returns_whole_text() -> None:
    doc = parse("# Title\n\nbody\n")
    assert doc.data is None and doc.body == "# Title\n\nbody\n" and doc.body_line == 1
    assert locate("# Title\n") is None


@pytest.mark.parametrize("text", ["", "﻿", " ---\na: 1\n---\n", "----\na: 1\n---\n", "x\n---\na: 1\n---\n"])
def test_texts_without_an_opener(text: str) -> None:
    assert locate(text) is None
    assert parse(text).data is None


def test_bom_is_dropped_from_a_body_without_frontmatter() -> None:
    assert parse("﻿hello\n").body == "hello\n"


def test_basic_block() -> None:
    doc = parse("---\ntitle: Hello\ntags: [a, b]\n---\nbody line\n")
    assert doc.data == {"title": "Hello", "tags": ["a", "b"]}
    assert doc.body == "body line\n"
    assert doc.body_line == 5


def test_crlf_and_trailing_spaces_on_delimiters() -> None:
    text = "--- \r\ntitle: Hello\r\n---\t\r\nbody\r\n"
    doc = parse(text)
    assert doc.data == {"title": "Hello"} and doc.body == "body\r\n" and doc.body_line == 4
    block = locate(text)
    assert block is not None and block.newline == "\r\n" and block.closer == "---"


def test_dot_closer() -> None:
    doc = parse("---\na: 1\n...\nrest\n")
    assert doc.data == {"a": 1} and doc.body == "rest\n"
    block = locate("---\na: 1\n...\nrest\n")
    assert block is not None and block.closer == "..."


def test_bom_before_opener() -> None:
    text = "﻿---\nname: x\n---\nbody"
    block = locate(text)
    assert block is not None and block.start == 1 and text[block.start : block.header_start] == "---\n"
    doc = parse(text)
    assert doc.data == {"name": "x"} and doc.body == "body"


def test_closer_at_end_without_newline() -> None:
    doc = parse("---\na: 1\n---")
    assert doc.data == {"a": 1} and doc.body == "" and doc.body_line == 4


def test_empty_header_is_an_empty_mapping() -> None:
    for text in ("---\n---\nbody\n", "---\n\n  \n---\n"):
        assert parse(text).data == {}


def test_offsets_allow_byte_preserving_rewrites() -> None:
    text = "---\r\nb: 2 # keep\r\na: 1\r\n...\r\n\r\n# Body\r\n"
    block = locate(text)
    assert block is not None
    assert block.header == "b: 2 # keep\r\na: 1\r\n"
    assert text[block.header_start : block.header_end] == block.header
    assert text[block.header_end : block.end] == "...\r\n"
    assert text[block.end :] == "\r\n# Body\r\n"
    rebuilt = text[: block.header_start] + block.header.replace("a: 1", "a: 9") + text[block.header_end :]
    assert rebuilt == text.replace("a: 1", "a: 9")
    assert block.body_line == 5


@pytest.mark.parametrize("text", ["---\na: 1\n", "---\n", "---", "﻿---\r\na: 1\r\n"])
def test_unclosed_block_is_an_error(text: str) -> None:
    with pytest.raises(FrontmatterError, match="never closed"):
        locate(text)
    with pytest.raises(FrontmatterError):
        parse(text)


@pytest.mark.parametrize(
    ("header", "message"),
    [
        ("- a\n- b\n", "must be a YAML mapping, not list"),
        ("just text\n", "must be a YAML mapping, not str"),
        ("1: one\n", "keys must be strings"),
        ("a: [unclosed\n", "invalid YAML frontmatter"),
        ("a: 1\na: 2\n", "duplicate key 'a'"),
        ("outer:\n  x: 1\n  x: 2\n", "duplicate key 'x'"),
        ("? [a]\n: 1\n", "invalid YAML frontmatter"),
    ],
)
def test_invalid_headers(header: str, message: str) -> None:
    with pytest.raises(FrontmatterError, match=message.replace("[", r"\[")):
        parse(f"---\n{header}---\n")


def test_duplicate_detection_compares_resolved_keys() -> None:
    with pytest.raises(FrontmatterError, match="duplicate key"):
        parse("---\nx:\n  1: a\n  0x1: b\n---\n")


def test_merge_keys_may_be_overridden() -> None:
    doc = parse("---\nbase: &b {x: 1, y: 2}\nchild:\n  <<: *b\n  x: 3\n---\n")
    assert doc.data == {"base": {"x": 1, "y": 2}, "child": {"x": 3, "y": 2}}


def test_dates_stay_python_objects() -> None:
    doc = parse("---\nday: 2026-10-12\nat: 2026-10-12T08:30:00Z\n---\n")
    assert doc.data is not None
    assert doc.data["day"] == datetime.date(2026, 10, 12)
    assert isinstance(doc.data["at"], datetime.datetime)


def test_unicode_content() -> None:
    doc = parse("---\ntitle: 안녕 — ünïcode ✓\n---\n본문\n")
    assert doc.data == {"title": "안녕 — ünïcode ✓"} and doc.body == "본문\n"


def test_horizontal_rule_later_in_body_is_body() -> None:
    doc = parse("---\na: 1\n---\ntext\n---\nmore\n")
    assert doc.data == {"a": 1} and doc.body == "text\n---\nmore\n"


def test_only_newline_ends_a_line() -> None:
    # A form feed or a lone carriage return does not split lines.
    assert locate("---\x0ca: 1\n---\n") is None
    assert locate("---\ra: 1\n---\n") is None


@pytest.mark.parametrize("header", ["created: 2024-02-30\n", "created: 2024-13-01\n", "at: 2024-01-01 25:00:00\n"])
def test_an_impossible_date_is_a_frontmatter_error(header: str) -> None:
    with pytest.raises(FrontmatterError, match="invalid YAML frontmatter"):
        parse(f"---\n{header}---\nbody\n")


def test_deeply_nested_yaml_is_a_frontmatter_error() -> None:
    with pytest.raises(FrontmatterError, match="nested too deeply"):
        parse("---\nk: " + "[" * 10_000 + "]" * 10_000 + "\n---\n")
