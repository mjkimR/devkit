"""``RULE-task-coverage``: active specs and their tasks cover each other's acceptance criteria.

Every ``tasks.md`` under ``specs/`` is checked against the ``spec.md`` beside it, unless that spec has
``status: completed``:

- each H3 under an H2 whose title contains ``Acceptance Criteria`` carries exactly one ``[AC-NN]`` ID (``AC-`` and two
  or more digits), unique in the spec, and the spec defines at least one;
- each checklist task covers the IDs it carries as ``[AC-NN]``, and the IDs of a direct child line
  ``- _Requirements: AC-01, AC-02_`` (every listed ID must be well-formed);
- every defined ID is covered by a task, and every covered ID is defined.

A missing or unreadable ``spec.md`` and malformed spec frontmatter are violations. Frontmatter, fenced and indented
code and HTML comments are not read (inline Markdown is left as written: ``[AC-01]: Title`` is a heading's ID, not a
link label); the shared scanner (``devkit_agt.features.rules.scan``) decides what they are
and which lines are checklist tasks, so ``count_tasks`` and this rule agree. Tables, prose, blockquotes and indirect
descendants never cover an ID.

Changing either file can break the pair, so a pair is checked when either file is targeted, and its violations are
reported on the file they belong to unless ``[rules] exclude`` matches it. A completed spec's pair is work history,
checked only when one of its files is named as an explicit target. The rule has no fix.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import PurePosixPath

from devkit_agt.features.rules import LineKind, Phase, RuleContext, Severity, Violation, match_path, scan
from devkit_agt.features.rules.services.builtins import BaseRule
from devkit_core.core import FrontmatterError
from devkit_docs.features.governance import explicitly_targeted

RULE_ID = "RULE-task-coverage"
COMPLETED = "completed"
type Add = Callable[[str, int, str, str], None]

_HEADING = re.compile(r"^ {0,3}(#{1,6})[\t\f\r ]+(.+)$")
_AC_TAG = re.compile(r"\[(AC-[0-9]{2,})\]")
_AC_ID = re.compile(r"AC-[0-9]{2,}")
_REQUIREMENT = re.compile(r"^_Requirements:\s*(.*?)_$")


def _excluded(ctx: RuleContext, path: str) -> bool:
    return any(match_path(pattern, path) for pattern in ctx.exclude)


def _defined(spec_path: str, spec: str, add: Add) -> set[str]:
    """The acceptance criterion IDs ``spec`` defines, reporting malformed and duplicate headings."""
    defined: set[str] = set()
    in_criteria = False
    for scanned in scan(spec, frontmatter=True):
        number = scanned.number
        heading = _HEADING.match(scanned.text) if scanned.kind is LineKind.PROSE else None
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
    for scanned in scan(tasks, frontmatter=True):
        number, line = scanned.number, scanned.text
        stripped = line.strip()
        if scanned.kind is not LineKind.PROSE or not stripped:
            continue
        indent = len(line) - len(line.lstrip(" "))
        while stack and indent <= stack[-1]:
            stack.pop()
        if scanned.task is not None:
            stack.append(indent)
            covered.update(_AC_TAG.findall(scanned.task.title))
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
            tasks_path = ctx.cache.relative_name(path)
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
