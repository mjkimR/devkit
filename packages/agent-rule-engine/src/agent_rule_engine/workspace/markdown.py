"""Markdown helpers shared by rules and by other engines that read the same files.

``count_tasks`` is the single checklist counter: a rule that reasons about task
completion and a workflow check that gates on it must agree on what a task is.
"""

from __future__ import annotations

import re

_CHECKLIST_ITEM = re.compile(r"^[ \t]*[-*+][ \t]+\[([ xX])\][ \t]+")


def _fence_run(stripped: str) -> str:
    """The leading run of three or more backticks or tildes, or an empty string."""
    if not stripped.startswith(("```", "~~~")):
        return ""
    char = stripped[0]
    n = 0
    while n < len(stripped) and stripped[n] == char:
        n += 1
    return stripped[:n]


def count_tasks(text: str) -> tuple[int, int]:
    """Return ``(checked, total)`` Markdown checklist items.

    Counts ``- [ ]``, ``- [x]`` and ``- [X]`` items (also with ``*`` and ``+``
    markers, any indentation, and at least one space or tab after the box)
    outside the leading YAML frontmatter and outside fenced code blocks. A
    fence closes only on a run of the same character at least as long as the
    opening run with nothing after it, as in CommonMark.
    """
    lines = text.replace("\r\n", "\n").split("\n")
    in_frontmatter = bool(lines) and lines[0].strip() == "---"
    fence = ""
    checked = total = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if in_frontmatter:
            if index > 0 and stripped == "---":
                in_frontmatter = False
            continue
        run = _fence_run(stripped)
        if not fence and run:
            fence = run
            continue
        if fence:
            if run and run[0] == fence[0] and len(run) >= len(fence) and not stripped[len(run) :].strip():
                fence = ""
            continue
        match = _CHECKLIST_ITEM.match(line)
        if match is None:
            continue
        total += 1
        if match.group(1) != " ":
            checked += 1
    return checked, total
