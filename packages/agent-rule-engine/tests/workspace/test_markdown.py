from __future__ import annotations

from agent_rule_engine import count_tasks


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
