from __future__ import annotations

import pytest
from devkit.rules import count_tasks, extract_links
from devkit.rules.workspace.markdown import fenced_lines, prose_lines


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
