"""Source-aware statement boundaries and masking."""

import pytest

from devkit_docs.features.documents.models.supersession import replacement_texts, same_text


def test_source_text_keeps_inline_markup_and_stops_at_next_item() -> None:
    entries = replacement_texts(
        "- Supersedes in part `ADR-old`: the `fast` mode\n  and [link](https://example.com).\n- Other item.\n"
    )
    assert [(e.id, e.line, e.text, e.pointer) for e in entries] == [
        ("ADR-old", 1, "the `fast` mode\nand [link](https://example.com).", False)
    ]
    assert same_text(entries[0].text, "the `fast` mode and [link](https://example.com).")
    assert not same_text(entries[0].text, "the `slow` mode and [link](https://example.com).")


@pytest.mark.parametrize("wrapper", ["```md\n{}\n```", "    {}", "<!-- {} -->", "~~{}~~", "`{}`"])
def test_hidden_statement_is_ignored(wrapper: str) -> None:
    assert replacement_texts(wrapper.format("Supersedes in part `ADR-old`: retries.")) == []


def test_blank_heading_and_adjacent_statement_boundaries() -> None:
    source = "Supersedes in part `ADR-a`: one.\n\nSupersedes in part `ADR-b`: two.\n## Next\nrest\n"
    assert [e.text for e in replacement_texts(source)] == ["one.", "two."]


def test_frontmatter_block_is_not_a_body_statement() -> None:
    source = (
        "---\nid: PADR-new\nsupersedes: ADR-old\nsummary: |\n  Supersedes in part `ADR-old`: retries.\n---\n# Body\n"
    )
    assert replacement_texts(source) == []
    source += "\nSupersedes in part `ADR-old`: actual body.\n"
    entries = replacement_texts(source)
    assert len(entries) == 1 and entries[0].line == 9 and entries[0].text == "actual body."


@pytest.mark.parametrize("comment", ["<!-- reviewer note -->", "<!--\nreviewer note\n-->"])
def test_a_comment_after_a_statement_ends_its_text(comment: str) -> None:
    source = f"Supersedes in part `ADR-old`: retries\nand backoff.\n{comment}\nafter.\n"
    assert [e.text for e in replacement_texts(source)] == ["retries\nand backoff."]


@pytest.mark.parametrize("separator", ["\u2028", "\u0085", "\x0c", "\x1c"])
def test_only_newlines_split_source_lines(separator: str) -> None:
    source = f"Supersedes in part `ADR-old`: one{separator}two\nmore.\r\n\r\nSupersedes in part `ADR-b`: three.\n"
    entries = replacement_texts(source)
    assert [(e.id, e.line, e.text) for e in entries] == [
        ("ADR-old", 1, f"one{separator}two\nmore."),
        ("ADR-b", 4, "three."),
    ]


def test_a_code_span_line_continues_a_statement() -> None:
    source = "Supersedes in part `ADR-old`: retries use\n`backoff`\nnow.\n"
    assert [e.text for e in replacement_texts(source)] == ["retries use\n`backoff`\nnow."]
