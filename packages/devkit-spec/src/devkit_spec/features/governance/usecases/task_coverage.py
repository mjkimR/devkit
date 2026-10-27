"""``RULE-task-coverage``: active specs and their tasks cover each other's acceptance criteria.

Every ``tasks.md`` under ``specs/`` is checked against the ``spec.md`` beside it, unless that spec has
``status: completed``:

- each H3 under an H2 whose title contains ``Acceptance Criteria`` carries exactly one ``[AC-NN]`` ID (``AC-`` and two
  or more digits), unique in the spec, and the spec defines at least one;
- each checklist task covers the IDs it carries as ``[AC-NN]``, and the IDs of a direct child line
  ``- _Requirements: AC-01, AC-02_`` (every listed ID must be well-formed);
- every defined ID is covered by a task, and every covered ID is defined.

A missing or unreadable ``spec.md`` and malformed spec frontmatter are violations. Frontmatter, fenced code and HTML
comments are not read. A checklist item indented four or more spaces counts only as the direct child of a task (two
spaces deeper); otherwise it is indented code. Tables, prose, blockquotes and indirect descendants never cover an ID.

Changing either file can break the pair, so a pair is checked when either file is targeted, and its violations are
reported on the file they belong to unless ``[rules] exclude`` matches it. A completed spec's pair is work history,
checked only when one of its files is named as an explicit target. The rule has no fix.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import PurePosixPath

from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation, match_path
from devkit_agt.features.rules.services.builtins import BaseRule
from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import locate

from devkit_spec.features.governance import explicitly_targeted

RULE_ID = "RULE-task-coverage"
COMPLETED = "completed"
type Add = Callable[[str, int, str, str], None]

_HEADING = re.compile(r"^ {0,3}(#{1,6})[\t\f\r ]+(.+)$")
_AC_TAG = re.compile(r"\[(AC-[0-9]{2,})\]")
_AC_ID = re.compile(r"AC-[0-9]{2,}")
_TASK = re.compile(r"^( *)(?:- |\* |\+ )\[[ xX]\] (.*)$")
_REQUIREMENT = re.compile(r"^_Requirements:\s*(.*?)_$")


def _excluded(ctx: RuleContext, path: str) -> bool:
    return any(match_path(pattern, path) for pattern in ctx.exclude)


def _fence_width(stripped: str, char: str) -> int:
    width = 0
    while width < len(stripped) and stripped[width] == char:
        width += 1
    return width


def _code_span_end(line: str, start: int) -> int:
    """The end of the inline code span whose opening backtick run starts at ``start``; ``-1`` when no run of the same
    length closes it on this line (the run is then literal)."""
    end = start
    while end < len(line) and line[end] == "`":
        end += 1
    width, index = end - start, end
    while index < len(line):
        if line[index] != "`":
            index += 1
            continue
        run = index
        while index < len(line) and line[index] == "`":
            index += 1
        if index - run == width:
            return index
    return -1


def _without_comments(line: str, comment: bool) -> tuple[str, bool]:
    """``line`` with its inline HTML comment spans blanked, and whether a comment continues past it; ``comment``:
    the line starts inside one. A ``<!--`` inside a code span is literal."""
    out = list(line)
    index = 0
    while index < len(line):
        if comment:
            end = line.find("-->", index)
            stop = len(line) if end < 0 else end + 3
            out[index:stop] = " " * (stop - index)
            if end < 0:
                break
            index, comment = stop, False
            continue
        if line[index] == "`":
            end = _code_span_end(line, index)
            index = end if end >= 0 else len(line) - len(line[index:].lstrip("`"))
            continue
        if line.startswith("<!--", index):
            comment = True
            continue
        index += 1
    return "".join(out), comment


def _contract_lines(text: str) -> list[str]:
    """The lines of ``text`` with frontmatter (as devkit's grammar locates it), fenced code and HTML comments blanked,
    numbering kept: a line opening with ``<!--`` starts an HTML block, blanked through the line that closes it, and a
    comment after other content is blanked as a span (outside code spans), up to its ``-->``.

    Unlike ``devkit_spec.features.documents.visible_lines``, indented lines stay (nested tasks may be indented four or more
    spaces) and inline Markdown is left as written (``[AC-01]: Title`` is a heading's ID, not a link label).
    """
    lines = text.replace("\r\n", "\n").split("\n")
    try:
        block = locate(text)
        front = block.body_line - 1 if block is not None else 0
    except FrontmatterError:  # never closed: every line belongs to the frontmatter
        front = len(lines)
    fence = ""
    width = 0
    block = False  # inside an HTML comment block, which ends with the line that closes it
    comment = False  # inside an inline comment span continued from an earlier line
    for number, line in enumerate(lines):
        stripped = line.strip()
        if number < front:
            lines[number] = ""
            continue
        if block:
            lines[number] = ""
            block = "-->" not in line
            continue
        if comment:
            lines[number], comment = _without_comments(line, comment)
            continue
        if fence:
            lines[number] = ""
            run = _fence_width(stripped, fence)
            if run >= width and not stripped[run:].strip():
                fence = ""
            continue
        if stripped.startswith(("```", "~~~")):
            fence = stripped[0]
            width = _fence_width(stripped, fence)
            lines[number] = ""
            continue
        if line.lstrip(" ").startswith("<!--") and len(line) - len(line.lstrip(" ")) <= 3:
            lines[number] = ""
            block = "-->" not in line.split("<!--", 1)[1]
        elif "<!--" in line:
            lines[number], comment = _without_comments(line, comment)
    return lines


def _defined(spec_path: str, spec: str, add: Add) -> set[str]:
    """The acceptance criterion IDs ``spec`` defines, reporting malformed and duplicate headings."""
    defined: set[str] = set()
    in_criteria = False
    for number, line in enumerate(_contract_lines(spec), start=1):
        heading = _HEADING.match(line)
        if heading is None:
            continue
        level, title = len(heading.group(1)), heading.group(2)
        if level <= 2:
            in_criteria = level == 2 and "Acceptance Criteria" in title
            continue
        if not in_criteria or level != 3:
            continue
        ids = _AC_TAG.findall(title)
        if len(ids) != 1:
            add(
                spec_path,
                number,
                f"acceptance criterion heading must carry exactly one [AC-NN] ID, found {len(ids)}",
                "Give this H3 exactly one unique [AC-01] style ID (AC- and two or more digits)",
            )
            continue
        if ids[0] in defined:
            add(
                spec_path,
                number,
                f"duplicate acceptance criterion ID {ids[0]}",
                "Give the scenario a distinct AC ID and update the task references to it",
            )
        defined.add(ids[0])
    if not defined:
        add(
            spec_path,
            1,
            "no acceptance criteria defined",
            "Add at least one H3 with an [AC-01] ID under an H2 Acceptance Criteria section",
        )
    return defined


def _covered(tasks_path: str, tasks: str, add: Add) -> set[str]:
    """The acceptance criterion IDs the checklist tasks of ``tasks`` reference, reporting malformed requirements."""
    covered: set[str] = set()
    stack: list[int] = []  # indentation of the enclosing checklist tasks
    for number, line in enumerate(_contract_lines(tasks), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip(" "))
        while stack and indent <= stack[-1]:
            stack.pop()
        task = _TASK.match(line)
        if task is not None:
            # Four or more spaces before a top-level item make indented code, not a list.
            if indent >= 4 and (not stack or indent != stack[-1] + 2):
                continue
            stack.append(indent)
            covered.update(_AC_TAG.findall(task.group(2)))
            continue
        if not stack or indent != stack[-1] + 2 or not stripped.startswith("- "):
            continue
        requirement = _REQUIREMENT.match(stripped.removeprefix("- "))
        if requirement is None:
            continue
        for raw in requirement.group(1).split(","):
            value = raw.strip()
            if _AC_ID.fullmatch(value) is None:
                add(
                    tasks_path,
                    number,
                    f"invalid requirement ID {value!r}",
                    "List well-formed IDs: _Requirements: AC-01, AC-02_",
                )
                continue
            covered.add(value)
    return covered


class TaskCoverageRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id=RULE_ID,
            name="task-acceptance-criteria-coverage",
            description="Acceptance criteria IDs of active specs and the task references in tasks.md cover each other.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
            related=("spec:contract-authoring",),
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        root = ctx.workspace_root
        found: list[Violation] = []

        def add(path: str, line: int, message: str, remediation: str) -> None:
            if not _excluded(ctx, path):
                found.append(Violation(rule_id=self.id, file=path, line=line, message=message, remediation=remediation))

        for path in ctx.cache.find_files(root / "specs", extensions=(".md",)):
            if path.name != "tasks.md":
                continue
            tasks_path = path.relative_to(root).as_posix()
            spec_path = (PurePosixPath(tasks_path).parent / "spec.md").as_posix()
            if not (ctx.is_file_targeted(tasks_path) or ctx.is_file_targeted(spec_path)):
                continue
            self._check_pair(ctx, spec_path, tasks_path, add)
        return found

    def _check_pair(self, ctx: RuleContext, spec_path: str, tasks_path: str, add: Add) -> None:
        try:
            spec = ctx.cache.read_text(spec_path)
        except OSError as exc:
            reason = "it does not exist" if isinstance(exc, FileNotFoundError) else str(exc)
            add(
                spec_path,
                1,
                f"the paired spec.md cannot be read: {reason}",
                "Restore a readable spec.md beside tasks.md",
            )
            return
        try:
            frontmatter = ctx.cache.get_frontmatter(spec_path) or {}
        except FrontmatterError as exc:
            add(
                spec_path,
                1,
                f"invalid spec frontmatter: {exc.message}",
                "Repair the YAML frontmatter so the spec status can be read",
            )
            return
        status = frontmatter.get("status")
        if (
            isinstance(status, str)
            and status.strip().lower() == COMPLETED
            and not (explicitly_targeted(ctx, spec_path) or explicitly_targeted(ctx, tasks_path))
        ):
            return
        defined = _defined(spec_path, spec, add)
        covered = _covered(tasks_path, ctx.cache.read_text(tasks_path), add)
        if missing := sorted(defined - covered):
            add(
                tasks_path,
                1,
                f"acceptance criteria without a task: {', '.join(missing)}",
                "Assign each missing ID to a checklist task with [AC-XX] or a direct _Requirements: AC-XX_ line",
            )
        if unknown := sorted(covered - defined):
            add(
                tasks_path,
                1,
                f"tasks reference undefined acceptance criteria: {', '.join(unknown)}",
                "Correct the task references to IDs defined in the paired spec.md",
            )
