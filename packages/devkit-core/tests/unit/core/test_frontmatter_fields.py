"""``devkit_core.core.frontmatter.set_field`` and ``trailing_comment``: one top-level line rewritten in place."""

from __future__ import annotations

import pytest
from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import Missing, parse, set_field, trailing_comment


@pytest.mark.parametrize(
    ("line", "start", "expected"),
    [
        ("status: draft  # draft | done", 7, "  # draft | done"),
        ('status: "draft #2"', 7, None),
        ('status: "draft #2" # c', 7, " # c"),
        ("status: 'it''s #x'\t# c", 7, "\t# c"),
        ("status: a#b", 7, None),
        ('status: "unterminated # c', 7, None),
        ("status:", 7, None),
    ],
)
def test_trailing_comment(line: str, start: int, expected: str | None) -> None:
    assert trailing_comment(line, start) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("---\nid: X\nstatus: draft\n---\nbody\n", "---\nid: X\nstatus: done\n---\nbody\n"),
        ("---\r\nid: X\r\nstatus: draft\r\n---\r\nbody", "---\r\nid: X\r\nstatus: done\r\n---\r\nbody"),
        ("---\nstatus: draft  # a | b\n---\n", "---\nstatus: done  # a | b\n---\n"),
        ('---\nstatus: "draft #2"\n---\n', "---\nstatus: done\n---\n"),
        ("---\n'status': draft # c\n---\n", "---\nstatus: done # c\n---\n"),
        ("---\nstatus:\n  - a\n\n  - b\nnext: 1\n---\n", "---\nstatus: done\nnext: 1\n---\n"),
        ("---\nstatus: |\n  text\n---\n", "---\nstatus: done\n---\n"),
        ("---\nnested:\n  status: keep\nstatus: draft\n---\n", "---\nnested:\n  status: keep\nstatus: done\n---\n"),
        ("﻿---\nstatus: draft\n---\n", "﻿---\nstatus: done\n---\n"),
        ("---\nstatus: a\nstatus: b\n---\n", "---\nstatus: done\nstatus: done\n---\n"),
        ("---\nstatus:draft\n---\n", "---\nstatus: done\n---\n"),
        ("---\nstatus : draft\n---\n", "---\nstatus: done\n---\n"),
    ],
)
def test_set_field_rewrites_the_line_in_place(text: str, expected: str) -> None:
    assert set_field(text, "status", "done") == expected


def test_set_field_can_drop_the_comment() -> None:
    assert (
        set_field("---\nstatus: draft # c\n---\n", "status", "done", keep_comment=False) == "---\nstatus: done\n---\n"
    )


def test_set_field_leaves_lookalike_lines_alone() -> None:
    text = "---\nstatus_x: a\n# status: b\n  status: c\n---\nstatus: body\n"
    assert set_field(text, "status", "done", missing=None) is None


@pytest.mark.parametrize(
    ("missing", "after", "expected"),
    [
        ("append", None, "---\nid: X\ntitle: t\nstatus: done\n---\n"),
        ("prepend", None, "---\nstatus: done\nid: X\ntitle: t\n---\n"),
        ("prepend", "id", "---\nid: X\nstatus: done\ntitle: t\n---\n"),
        ("append", "absent", "---\nid: X\ntitle: t\nstatus: done\n---\n"),
        (None, None, None),
    ],
)
def test_set_field_missing_key(missing: Missing | None, after: str | None, expected: str | None) -> None:
    text = "---\nid: X\ntitle: t\n---\n"
    assert set_field(text, "status", "done", missing=missing, after=after) == expected


def test_set_field_after_skips_the_anchor_block_value() -> None:
    text = "---\nid: X\ntags:\n  - a\nend: 1\n---\n"
    assert set_field(text, "area", "core", after="tags") == "---\nid: X\ntags:\n  - a\narea: core\nend: 1\n---\n"


def test_set_field_on_an_empty_header_and_crlf() -> None:
    assert set_field("---\r\n---\r\n", "status", "done") == "---\r\nstatus: done\r\n---\r\n"


def test_set_field_without_a_block() -> None:
    assert set_field("body\r\n", "status", "done") == "---\r\nstatus: done\r\n---\r\nbody\r\n"
    assert set_field("﻿body\n", "status", "done") == "﻿---\nstatus: done\n---\nbody\n"
    assert set_field("body\n", "status", "done", missing=None) is None


def test_set_field_raises_for_an_unclosed_block() -> None:
    with pytest.raises(FrontmatterError):
        set_field("---\nstatus: draft\n", "status", "done")


def test_set_field_result_parses() -> None:
    text = "---\nid: X\nstatus:\n  - a\n  - b\n# keep\n---\nbody\n"
    updated = set_field(text, "status", "done")
    assert parse(updated).data == {"id": "X", "status": "done"}
    assert "# keep" in updated


def test_a_quoted_hash_inside_a_flow_collection_is_not_a_comment() -> None:
    text = "---\nworkflow_history: [{workflow: a, note: 'x #1'}]\ntags: [\"a #b\", c]  # keep\n---\nbody\n"
    text = set_field(text, "workflow_history", "[new]")
    assert set_field(text, "tags", "[c]") == "---\nworkflow_history: [new]\ntags: [c]  # keep\n---\nbody\n"
