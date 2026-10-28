"""Every reader of spec Markdown agrees with the shared scanner on code, comments, frontmatter and checklist tasks.

The same tricky documents go to ``count_tasks``, ``parse_boundaries``, ``RULE-task-coverage``, ``visible_lines`` and
the proposal body carrier; a task or heading hidden in code, a comment or frontmatter is invisible to all of them.
"""

from __future__ import annotations

import pytest
from devkit_agt.features.rules import LineKind, count_tasks, scan
from devkit_core.core.frontmatter import locate
from devkit_docs.features.documents import visible_lines

from devkit_spec.features.entrypoints import parse_boundaries
from devkit_spec.features.governance.usecases.task_coverage import _covered, _defined
from devkit_spec.features.proposals.services.body import demote_headings

# Each hidden task carries an AC-9x ID; each real one an AC-0x ID, so a reader's view shows in the IDs it reports.
DOCUMENTS = [
    pytest.param(
        "Use a ` stray backtick\n```\n- [ ] [AC-90] fenced\n```\n- [ ] [AC-01] after the fence\n", id="stray-backtick"
    ),
    pytest.param(
        "~~~~\n```\n- [ ] [AC-91] in tildes\n~~~~\n- [ ] [AC-01] after the tildes\n", id="tilde-holds-backticks"
    ),
    pytest.param("```js``` is inline\n- [ ] [AC-01] after the inline line\n", id="inline-backtick-line"),
    pytest.param("<!--\n- [ ] [AC-92] commented out\n-->\n- [ ] [AC-01] after the comment\n", id="comment-block"),
    pytest.param("Text <!-- note\n[AC-93] continued\n-->\n- [ ] [AC-01] after the span\n", id="comment-span"),
    pytest.param(
        "- [x] [AC-01] starts with <!-- and is one line\n- [ ] [AC-02] next\n```\n- [ ] [AC-97] fenced\n```\n",
        id="unclosed-inline-opener",
    ),
    pytest.param("-  [x] [AC-01] two spaces\n*\t[X] [AC-02] tab\n", id="marker-spacing"),
    pytest.param("Write `<!--` to open one\n- [ ] [AC-01] after a literal opener\n", id="opener-in-code-span"),
    pytest.param("---\nnote: |\n  - [ ] [AC-94] frontmatter\n---\n- [ ] [AC-01] body\n", id="frontmatter"),
    pytest.param("Intro\n\n    - [ ] [AC-95] indented code\n\n- [ ] [AC-01] listed\n", id="indented-code"),
    pytest.param("- [ ] [AC-01] parent\n    ```\n    - [ ] [AC-96] fenced in the item\n    ```\n", id="list-fence"),
]


def _ids(titles: list[str]) -> set[str]:
    return {word.strip("[]") for title in titles for word in title.split() if word.startswith("[AC-")}


@pytest.mark.parametrize("text", DOCUMENTS)
def test_every_task_reader_sees_the_same_tasks(text: str) -> None:
    scanned = [line for line in scan(text, frontmatter=True) if line.task is not None]
    expected = _ids([line.task.title for line in scanned if line.task is not None])
    assert expected and not any(identifier.startswith("AC-9") for identifier in expected)

    checked, total = count_tasks(text)
    assert total == len(scanned)
    assert checked == sum(line.task.checked for line in scanned if line.task is not None)

    boundaries = [task for task in parse_boundaries(text) if task.index]
    assert [task.index for task in boundaries] == list(range(1, total + 1))
    assert _ids([task.title for task in boundaries]) == expected

    problems: list[str] = []
    assert _covered("tasks.md", text, lambda *problem: problems.append(problem[2])) == expected
    assert problems == []

    block = locate(text)
    start, first_line = (block.end, block.body_line) if block is not None else (0, 1)
    visible = {line.number: line.text.strip() for line in visible_lines(text, start=start, first_line=first_line)}
    for line in scan(text, frontmatter=True):
        if line.task is not None:
            assert visible[line.number].startswith(("-", "*")), line.line
        elif "[AC-9" in line.line:
            assert not visible.get(line.number, "").startswith(("-", "*")), line.line


@pytest.mark.parametrize(
    "body",
    [
        pytest.param("~~~~\n```\n### [AC-91] in tildes\n~~~~\n", id="tilde-holds-backticks"),
        pytest.param("```js``` is inline\n", id="inline-backtick-line"),
        pytest.param("<!--\n### [AC-92] commented out\n-->\n", id="comment-block"),
        pytest.param("Write `<!--` to open one\n", id="opener-in-code-span"),
    ],
)
def test_heading_readers_agree(body: str) -> None:
    spec = f"## Acceptance Criteria\n{body}### Scenario [AC-01]: First <!-- was [AC-99] -->\n"
    problems: list[str] = []
    assert _defined("spec.md", spec, lambda *problem: problems.append(problem[2])) == {"AC-01"}
    assert problems == []

    lines = spec.split("\n")
    demoted = demote_headings(lines)
    for scanned, before, after in zip(scan(spec), lines, demoted, strict=True):
        if before.startswith("###"):
            assert (after != before) == (scanned.kind is LineKind.PROSE), before
