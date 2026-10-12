from __future__ import annotations

import pytest
from devkit.rules import extract_links
from devkit.rules.workspace.markdown import local_target, prose_lines


@pytest.mark.parametrize(
    ("line", "target"),
    [
        ('[t](t.md "Title")', "t.md"),
        ("[t](t.md 'Title')", "t.md"),
        ("[t](t.md (Title))", "t.md"),
        ("[s](my%20file.md)", "my%20file.md"),
        ("[n](<my file.md>)", "my file.md"),
        ("[q](t.md?plain=1#L3)", "t.md?plain=1#L3"),
        ("[p](foo(1).md)", "foo(1).md"),
        ("[e](a\\)b.md)", "a\\)b.md"),
        ("![alt](img.png)", "img.png"),
        ("[ ]( spaced.md )", "spaced.md"),
    ],
)
def test_destination_forms(line: str, target: str) -> None:
    links = extract_links(line + "\n")
    assert [link.target for link in links] == [target]
    link = links[0]
    assert line[link.target_start : link.target_end] == target


def test_link_text_with_brackets_and_nested_image() -> None:
    links = extract_links("[a [b] c](x.md) [![logo](logo.png)](home.md)\n")
    assert [(link.text, link.target) for link in links] == [
        ("a [b] c", "x.md"),
        ("![logo](logo.png)", "home.md"),
        ("logo", "logo.png"),
    ]


def test_not_inline_links() -> None:
    text = "\\[escaped](x.md) [ref][label] [unclosed](x.md [title](x.md\n- [ ] task\n"
    assert extract_links(text) == []


def test_code_spans_and_fences_hide_links() -> None:
    text = (
        "`[a](one.md)` ``[b](two.md) ` `` [c](three.md)\n"
        "````md\n```\n[d](four.md)\n```\n````\n"
        "~~~\n[e](five.md)\n~~~\n"
        "[f](six.md)\n"
    )
    assert [(link.target, link.line) for link in extract_links(text)] == [("three.md", 1), ("six.md", 10)]


def test_prose_lines_keep_carriage_returns_and_numbering() -> None:
    assert list(prose_lines("a\r\n```\nb\n```\nc", first_line=5)) == [(5, "a\r"), (9, "c")]


@pytest.mark.parametrize(
    "destination",
    ["https://x", "HTTPS://x", "mailto:a@b", "tel:123", "vscode://file", "#anchor", "/root.md", "//cdn/x", "", "?q"],
)
def test_non_local_destinations(destination: str) -> None:
    assert local_target(destination) is None


def test_local_target_decodes_and_keeps_suffix() -> None:
    target = local_target("my%20dir/a\\_b.md?x=1#frag")
    assert target is not None
    assert (target.path, target.raw_path, target.suffix) == ("my dir/a_b.md", "my%20dir/a\\_b.md", "?x=1#frag")
