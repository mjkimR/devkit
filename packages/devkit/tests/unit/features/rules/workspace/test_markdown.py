from __future__ import annotations

import pytest
from devkit_agt.features.rules import ChecklistItem, count_tasks, extract_links, scan
from devkit_agt.features.rules.models.markdown import fenced_lines, prose_lines


def test_count_tasks_skips_frontmatter_and_fences() -> None:
    text = (
        "---\nid: TASKS-x\n- [ ] not a task in frontmatter\n---\n\n"
        "- [x] **Task 1.1**: done\n"
        "  - [X] nested done\n"
        "\t* [ ] tab-indented open\n"
        "+ [ ] plus open\n"
        "- [x]no space is not a task\n"
        "-[ ] no marker space is not a task\n"
        "```markdown\n- [ ] fenced example\n- [x] fenced example\n```\n"
        "~~~\n- [ ] tilde fenced example\n~~~\n"
        "- [ ] trailing open\n"
    )
    assert count_tasks(text) == (2, 5)


def test_count_tasks_without_frontmatter_or_tasks() -> None:
    assert count_tasks("# Title\n\nNo checklist here.\n") == (0, 0)
    assert count_tasks("- [x] a\r\n- [ ] b\r\n") == (1, 2)
    assert count_tasks("") == (0, 0)


def test_count_tasks_fence_closes_only_on_matching_run() -> None:
    text = (
        "- [x] Task 1\n  ~~~markdown\n  ```go\n  - [ ] inside the tilde fence\n  ~~~\n- [ ] Task 2\n"
        "````\n```\n- [ ] inside the four-backtick fence\n````\n- [x] Task 3\n"
        "```\n- [ ] inside\n``` not a close\n```\n- [ ] Task 4\n"
    )
    assert count_tasks(text) == (2, 4)


def test_count_tasks_uses_the_core_frontmatter_grammar() -> None:
    # An unclosed block leaves no body; a block closed by "..." ends like "---".
    assert count_tasks("---\nstatus: draft\n- [ ] a\n") == (0, 0)
    assert count_tasks("---\nstatus: draft\n...\n- [x] a\n") == (1, 1)
    # " ---" does not open frontmatter, so the item after it counts.
    assert count_tasks(" ---\n- [ ] a\n") == (0, 1)


@pytest.mark.parametrize(
    ("text", "fenced", "prose"),
    [
        ("```\na\n```\nb", [2], [4]),
        ("```python\na\n```", [2], []),
        ("~~~ js `x`\na\n~~~", [2], []),  # a tilde fence's info string may hold backticks
        ("````\n```\na\n````\nb", [2, 3], [5]),  # closed only by a run at least as long
        ("```\na\n``` trailing\n```\nb", [2, 3], [5]),  # a closing run has nothing after it
        ("```\nunclosed", [2], []),  # an unclosed fence runs to the end
        ("```js``` is inline\nb", [], [1, 2]),  # a backtick fence's info string cannot hold a backtick
        ("``` a ` b\nc", [], [1, 2]),
        ("``\nnot a fence\n``", [], [1, 2, 3]),
    ],
)
def test_fence_detection(text: str, fenced: list[int], prose: list[int]) -> None:
    assert [number for number, _ in fenced_lines(text)] == fenced
    assert [number for number, _ in prose_lines(text)] == prose


def test_a_backtick_line_with_an_inline_span_does_not_hide_later_links() -> None:
    text = "```js``` is inline\n[a](a.md)\n"
    assert [(link.line, link.target) for link in extract_links(text)] == [(2, "a.md")]
    assert [link.target for link in extract_links("```\n[a](a.md)\n```\n[b](b.md)\n")] == ["b.md"]


def _kinds(text: str, **options: bool) -> list[str]:
    return [line.kind.value for line in scan(text, **options)]


@pytest.mark.parametrize(
    ("text", "kinds"),
    [
        # A fence indented within a list item's content is a fence; four columns outside a list are indented code.
        ("- item\n    ```\n    code\n    ```", ["prose", "fence", "code", "fence"]),
        ("Intro\n\n    ```\n    code", ["prose", "prose", "indented", "indented"]),
        ("Intro\n    ```\nmore", ["prose", "prose", "prose"]),  # a paragraph continues; no indented code
        # A line opening with "<!--" is an HTML block through the line holding "-->"; a fence inside it is not one.
        ("<!--\n```\n--> tail\n```", ["comment", "comment", "comment", "fence"]),
        ("<!-- one line --> tail\nnext", ["comment", "prose"]),
        # A "<!--" after content is an inline span up to its "-->"; one inside a code span is literal.
        ("a <!-- b\nc\nd --> e\n```", ["prose", "comment", "prose", "fence"]),
        ("a `<!--` b\n```", ["prose", "fence"]),
        ("---\n- [ ] a\n---\nb", ["frontmatter", "frontmatter", "frontmatter", "prose"]),
    ],
)
def test_scan_kinds(text: str, kinds: list[str]) -> None:
    assert _kinds(text, frontmatter=True) == kinds


def test_scan_blanks_comments_in_place_and_reports_tasks() -> None:
    lines = list(scan("- [x] Done <!-- [AC-99] -->\r\n-  [ ] Spaced\n1. [ ] ordered\n       - [ ] continuation\n"))
    assert lines[0].text == "- [x] Done                 "
    assert lines[0].line.endswith("\r")
    assert lines[0].task == ChecklistItem(checked=True, title="Done")
    assert lines[1].task == ChecklistItem(checked=False, title="Spaced")
    assert lines[1].offset == len(lines[0].line) + 1
    assert lines[2].task is None  # an ordered item is no checklist task
    assert lines[3].task is None  # four columns past its container: continuation text
    assert count_tasks("- [ ] a\n  <!--\n  - [ ] b\n  -->\n  - [ ] nested\n") == (0, 2)


def test_an_inline_comment_opener_without_a_closer_in_its_paragraph_is_literal() -> None:
    marker = "- [x] 1. Remove the marker (it starts with <!-- and is one line).\n- [ ] 2. Not done\n"
    assert count_tasks(marker) == (1, 2)
    text = "Prose with <!-- an opener.\n\n```\n[x](missing.md)\n```\nLater\n"
    assert [number for number, _ in fenced_lines(text)] == [4]
    assert [number for number, _ in prose_lines(text)] == [1, 2, 6, 7]
    assert extract_links(text) == []
    # A closer on a later line of the same paragraph keeps the comment open; a list item ends the paragraph.
    assert _kinds("a <!-- b\nc --> d\n- [ ] e") == ["prose", "prose", "prose"]
    assert count_tasks("a <!-- b\n- [ ] c -->\n") == (0, 1)


@pytest.mark.parametrize(
    ("text", "masked"),
    [
        ("a \\<!-- b", "a \\<!-- b"),  # escaped
        ("a `<!--` b", "a `<!--` b"),  # in a code span
        ("a `x\ny <!-- z` w", "y <!-- z` w"),  # in a code span wrapping onto the next line
        ("a <!-- b --> c", "a            c"),
    ],
)
def test_literal_comment_openers(text: str, masked: str) -> None:
    assert [line.text for line in scan(text)][-1] == masked
