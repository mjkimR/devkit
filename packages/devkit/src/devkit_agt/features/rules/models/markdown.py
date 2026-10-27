"""Markdown helpers shared by rules and by other engines that read the same files.

``scan`` is the single Markdown block scanner: every reader that must agree on
what is code, comment or a checklist task (link extraction, the CLI-contract
citations, the checklist counter, devkit-spec's reference extraction, task
coverage and boundary parsing, proposal carrying, the wording rule) builds on
it rather than tracking fences itself. It classifies each line as one of:

- ``PROSE``: ordinary text; ``text`` has its HTML comments blanked;
- ``FENCE``/``CODE``: a fence delimiter line / a line inside a fenced code
  block. A fence (CommonMark) is a run of three or more backticks or tildes
  indented at most three spaces (relative to the enclosing list item's content),
  closed only by a run of the same character at least as long with nothing
  after it; a backtick run with another backtick later on its line is not a
  fence; an unclosed fence runs to the end;
- ``INDENTED``: indented code (four or more columns after a blank line or a
  fence-free start, outside a list); ``text`` keeps the line, so a caller that
  reads indented lines may;
- ``COMMENT``: a line inside an HTML comment. A line opening with ``<!--``
  (indented at most three) starts an HTML block that ends with the line
  holding ``-->``; a ``<!--`` after other content is an inline span, blanked
  up to its ``-->`` (on a later line if need be; an unclosed one runs to the
  end). A ``<!--`` inside an inline code span (a backtick run closed by the
  next run of the same length on its line) is literal;
- ``FRONTMATTER``: the leading YAML frontmatter (``devkit_core.core.frontmatter``
  grammar) when asked to skip it; a block never closed takes the whole text.

A ``PROSE`` line that begins outside a comment and is a checklist item
(``- [ ]``, ``- [x]``, ``* [X]``, ``+ [ ]``: a list marker indented at most three
columns relative to its container, a box, then at least one space or tab)
carries its ``task``. ``count_tasks`` counts exactly those, so a rule that
reasons about task completion and a workflow check that gates on it agree on
what a task is.

``prose_lines`` and ``fenced_lines`` are the fence-only views (comment and
indented lines count as prose) that link extraction and citations use, and
``code_spans`` the inline code of a prose line.

Lines end with ``\\n`` only, as in ``devkit_core.core.frontmatter``; a ``\\r``
before it stays part of ``line`` and is left out of ``text``.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import unquote

from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import locate

_CHECKLIST_ITEM = re.compile(r"^[ \t]*[-*+][ \t]+\[([ xX])\][ \t]+(.*)$")
_LIST_MARKER = re.compile(r"^([ \t]*)([-*+]|[0-9]{1,9}[.)])([ \t]+|$)")


class LineKind(StrEnum):
    """What a scanned line is; see the module docstring."""

    PROSE = "prose"
    FENCE = "fence"
    CODE = "code"
    INDENTED = "indented"
    COMMENT = "comment"
    FRONTMATTER = "frontmatter"


@dataclass(frozen=True, slots=True)
class ChecklistItem:
    """A checklist item: whether its box is checked and its ``title`` (the text after the box, stripped)."""

    checked: bool
    title: str


@dataclass(frozen=True, slots=True)
class ScannedLine:
    """One line of a scanned text.

    ``number`` is 1-based (from ``first_line``), ``offset`` the index of the line's first character in the scanned
    text, ``line`` the line as written (without ``\\n``) and ``text`` the line without a trailing ``\\r``, every
    character that is not readable as prose replaced by a space so columns still match: HTML comments of a ``PROSE``
    line, the whole of a ``FENCE``, ``CODE``, ``COMMENT`` or ``FRONTMATTER`` line; an ``INDENTED`` line is kept.
    ``task`` is the checklist item a ``PROSE`` line holds.
    """

    number: int
    offset: int
    line: str
    kind: LineKind
    text: str
    task: ChecklistItem | None = None


def _fence_run(stripped: str) -> str:
    """The leading run of three or more backticks or tildes, or an empty string.

    A backtick run followed by another backtick on the line is no fence: the
    info string of a backtick fence cannot contain one, so a line such as
    ````` ```js``` is inline ````` opens an inline code span instead.
    """
    if not stripped.startswith(("```", "~~~")):
        return ""
    char = stripped[0]
    n = 0
    while n < len(stripped) and stripped[n] == char:
        n += 1
    if char == "`" and "`" in stripped[n:]:
        return ""
    return stripped[:n]


def _indent(line: str) -> int:
    """The column of the first non-blank character of ``line`` (a tab advances to the next multiple of four)."""
    column = 0
    for char in line:
        if char == " ":
            column += 1
        elif char == "\t":
            column += 4 - column % 4
        else:
            break
    return column


def _code_span_end(line: str, start: int) -> int:
    """The end of the inline code span whose opening backtick run starts at ``start``, or ``-1`` when no run of the
    same length closes it on this line (the run is then literal)."""
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


def _mask_comments(line: str, comment: bool) -> tuple[str, bool]:
    """``line`` with its inline HTML comment spans blanked, and whether a comment continues past it; ``comment``
    tells whether the line starts inside one. A ``<!--`` inside a code span is literal."""
    if not comment and "<!--" not in line:
        return line, False
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


def parse_checklist_item(line: str) -> ChecklistItem | None:
    """The checklist item ``line`` holds by the shared grammar, ignoring its indentation and context.

    ``scan`` applies it only where a list item can start; use a scanned line's ``task`` to read a document.
    """
    match = _CHECKLIST_ITEM.match(line)
    if match is None:
        return None
    return ChecklistItem(checked=match.group(1) != " ", title=match.group(2).strip())


def split_lines(text: str) -> list[str]:
    """``text`` split on ``\\n`` without the terminators; ``"\\n".join`` restores it exactly."""
    return text.split("\n")


def scan(text: str, *, start: int = 0, first_line: int = 1, frontmatter: bool = False) -> Iterator[ScannedLine]:
    """Every line of ``text[start:]`` classified (see the module docstring), numbered from ``first_line``.

    With ``frontmatter``, the leading frontmatter of ``text[start:]`` is reported as ``FRONTMATTER`` lines.
    """
    lines = split_lines(text[start:])
    front = 0
    if frontmatter:
        try:
            block = locate(text[start:])
            front = block.body_line - 1 if block is not None else 0
        except FrontmatterError:  # never closed: every line belongs to the frontmatter
            front = len(lines)
    fence = ""
    block_comment = False  # inside an HTML block opened by a line starting with "<!--"
    comment = False  # inside an inline comment span continued from an earlier line
    columns: list[int] = []  # content columns of the enclosing list items
    after_blank, in_indented = True, False
    offset = start
    for position, line in enumerate(lines):
        number = first_line + position
        content = line.removesuffix("\r")
        blank = " " * len(content)
        kind, masked, task = LineKind.PROSE, content, None
        stripped = content.strip()
        indent = _indent(content)
        base = next((column for column in reversed(columns) if column <= indent), 0)
        if position < front:
            kind, masked = LineKind.FRONTMATTER, blank
        elif block_comment:
            kind, masked = LineKind.COMMENT, blank
            block_comment = "-->" not in content
        elif comment:
            masked, comment = _mask_comments(content, True)
            if comment:
                kind = LineKind.COMMENT
        elif fence:
            run = _fence_run(stripped) if indent - base <= 3 else ""
            closes = run[:1] == fence[0] and len(run) >= len(fence) and not stripped[len(run) :].strip()
            kind, masked = (LineKind.FENCE, blank) if closes else (LineKind.CODE, blank)
            if closes:
                fence = ""
        elif not stripped:
            after_blank = True
        elif indent >= 4 and (in_indented or (after_blank and not columns)):
            kind, in_indented = LineKind.INDENTED, True
        else:
            marker = _LIST_MARKER.match(content) if indent - base <= 3 else None
            if marker is not None:
                while columns and columns[-1] > indent:
                    columns.pop()
                spaces = len(marker.group(3).expandtabs(4))
                columns.append(indent + len(marker.group(2)) + (spaces if 1 <= spaces <= 4 else 1))
            elif after_blank or indent == 0:
                while columns and columns[-1] > indent:
                    columns.pop()
            run = _fence_run(stripped) if indent - base <= 3 else ""
            if run:
                kind, masked, fence = LineKind.FENCE, blank, run
            elif indent - base <= 3 and stripped.startswith("<!--"):
                kind, masked = LineKind.COMMENT, blank
                block_comment = "-->" not in stripped[4:]
            else:
                masked, comment = _mask_comments(content, False)
                if marker is not None:
                    task = parse_checklist_item(masked)
        if stripped and kind is not LineKind.FRONTMATTER:
            after_blank = False
        if kind is not LineKind.INDENTED and stripped:
            in_indented = False
        yield ScannedLine(number, offset, line, kind, masked, task)
        offset += len(line) + 1


def prose_lines(text: str, *, first_line: int = 1) -> Iterator[tuple[int, str]]:
    """``(line_number, line)`` for every line of ``text`` outside fenced code blocks.

    ``first_line`` is the number of the first line of ``text`` in its document.
    Fence delimiter lines themselves are not yielded; comment and indented lines are.
    """
    return (
        (scanned.number, scanned.line)
        for scanned in scan(text, first_line=first_line)
        if scanned.kind not in (LineKind.FENCE, LineKind.CODE)
    )


def fenced_lines(text: str, *, first_line: int = 1) -> Iterator[tuple[int, str]]:
    """``(line_number, line)`` for every line of ``text`` inside fenced code blocks, delimiter lines excluded.

    An unclosed fence runs to the end of ``text``, as in CommonMark.
    """
    return (
        (scanned.number, scanned.line) for scanned in scan(text, first_line=first_line) if scanned.kind is LineKind.CODE
    )


def count_tasks(text: str) -> tuple[int, int]:
    """Return ``(checked, total)`` Markdown checklist items: the ``task`` lines ``scan`` finds.

    Frontmatter, fenced and indented code and HTML comments hold no task. A frontmatter block that is never
    closed leaves no body, so such a text has no tasks.
    """
    checked = total = 0
    for scanned in scan(text, frontmatter=True):
        if scanned.task is None:
            continue
        total += 1
        checked += scanned.task.checked
    return checked, total


@dataclass(slots=True)
class MarkdownLink:
    """One inline link (or image) ``[text](destination "title")`` on a line.

    ``target`` is the destination exactly as written, without enclosing angle
    brackets. ``start``/``end`` delimit the whole link on its line (from the
    ``[``); ``target_start``/``target_end`` delimit ``target`` itself, so a
    repair can replace the destination and keep the text and the title.
    ``angle`` tells whether the destination was written as ``<...>``.
    """

    text: str
    target: str
    line: int
    start: int
    end: int
    target_start: int = 0
    target_end: int = 0
    angle: bool = False


def _escaped(line: str, index: int) -> bool:
    """Whether ``line[index]`` is preceded by an odd number of backslashes."""
    count = 0
    while index - count - 1 >= 0 and line[index - count - 1] == "\\":
        count += 1
    return count % 2 == 1


def _code_spans(line: str) -> list[tuple[int, int]]:
    """``(start, end)`` of inline code spans: a backtick run closed by the next run of the same length."""
    runs = [(m.start(), m.end()) for m in re.finditer(r"`+", line)]
    spans: list[tuple[int, int]] = []
    index = 0
    while index < len(runs):
        start, end = runs[index]
        width = end - start
        closer = next((k for k in range(index + 1, len(runs)) if runs[k][1] - runs[k][0] == width), None)
        if closer is None:
            index += 1
            continue
        spans.append((start, runs[closer][1]))
        index = closer + 1
    return spans


def code_spans(line: str) -> list[tuple[int, str]]:
    """``(column, content)`` of each inline code span of a prose line; ``column`` is 1-based, at the opening run.

    The content is stripped of surrounding whitespace.
    """
    found: list[tuple[int, str]] = []
    for start, end in _code_spans(line):
        width = len(line[start:end]) - len(line[start:end].lstrip("`"))
        found.append((start + 1, line[start + width : end - width].strip()))
    return found


def _skip_blanks(line: str, index: int) -> int:
    while index < len(line) and line[index] in " \t":
        index += 1
    return index


def _closing_bracket(line: str, start: int) -> int | None:
    depth = 0
    for index in range(start, len(line)):
        char = line[index]
        if char in "[]" and _escaped(line, index):
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return index
    return None


def _destination(line: str, index: int) -> tuple[int, int, int, bool] | None:
    """``(target_start, target_end, next_index, angle)`` of a destination starting at ``index``."""
    if index < len(line) and line[index] == "<":
        position = index + 1
        while position < len(line):
            if line[position] == ">" and not _escaped(line, position):
                return index + 1, position, position + 1, True
            if line[position] == "<" and not _escaped(line, position):
                return None
            position += 1
        return None
    depth = 0
    position = index
    while position < len(line):
        char = line[position]
        if char == "\\":
            position += 2
            continue
        if char in " \t":
            break
        if char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                break
            depth -= 1
        position += 1
    position = min(position, len(line))
    if depth != 0:
        return None
    return index, position, position, False


def _title_end(line: str, index: int) -> int | None:
    """Index after an optional link title starting at ``index`` (``index`` itself when there is none)."""
    if index >= len(line) or line[index] not in "\"'(":
        return index
    closer = ")" if line[index] == "(" else line[index]
    position = index + 1
    while position < len(line):
        if line[position] == closer and not _escaped(line, position):
            return position + 1
        position += 1
    return None


def _inline_link(line: str, start: int, line_number: int) -> MarkdownLink | None:
    close = _closing_bracket(line, start)
    if close is None or close + 1 >= len(line) or line[close + 1] != "(":
        return None
    destination = _destination(line, _skip_blanks(line, close + 2))
    if destination is None:
        return None
    target_start, target_end, position, angle = destination
    position = _skip_blanks(line, position)
    after_title = _title_end(line, position)
    if after_title is None:
        return None
    position = _skip_blanks(line, after_title)
    if position >= len(line) or line[position] != ")":
        return None
    return MarkdownLink(
        text=line[start + 1 : close],
        target=line[target_start:target_end],
        line=line_number,
        start=start,
        end=position + 1,
        target_start=target_start,
        target_end=target_end,
        angle=angle,
    )


def extract_links(text: str) -> list[MarkdownLink]:
    """Inline Markdown links and images of ``text`` in document order.

    Links inside fenced code blocks and inline code spans are skipped. A link
    nested in another link's text (an image inside a link) is reported too.
    Reference-style links and autolinks are not extracted.
    """
    links: list[MarkdownLink] = []
    for line_number, line in prose_lines(text):
        if "[" not in line:
            continue
        spans = _code_spans(line)
        for index, char in enumerate(line):
            if char != "[" or _escaped(line, index) or any(s <= index < e for s, e in spans):
                continue
            link = _inline_link(line, index, line_number)
            if link is not None:
                links.append(link)
    return links


_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_ESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")


@dataclass(frozen=True)
class LocalTarget:
    """The file part of a relative link destination.

    ``path`` is the decoded path (escapes removed, percent-encoding decoded);
    ``raw_path`` is the same part as written and ``suffix`` the ``?query`` and
    ``#fragment`` that follow it.
    """

    path: str
    raw_path: str
    suffix: str


# Characters that force an angle-bracket destination when a written path contains them.
_NEEDS_ANGLE = re.compile(r"[\s()]")
# Characters percent-encoded in a written path, so ``local_target`` reads it back unchanged:
# ``%`` and ``\`` would be decoded or unescaped, ``#`` and ``?`` would start a fragment or query,
# and ``<``/``>`` cannot appear inside an angle-bracket destination.
_ENCODE = {char: f"%{ord(char):02X}" for char in "%\\#?<>"}


def encode_destination(path: str, suffix: str = "", *, angle: bool = False) -> str:
    """The link destination for the relative ``path`` (decoded, POSIX) followed by ``suffix`` (``?query`` /
    ``#fragment`` as written), which ``local_target`` reads back as ``path``.

    ``%``, ``\\``, ``#``, ``?``, ``<`` and ``>`` are percent-encoded; a path with whitespace or parentheses is
    wrapped in ``<...>`` unless ``angle`` says the destination being replaced is already inside angle brackets
    (which the caller keeps).
    """
    encoded = "".join(_ENCODE.get(char, char) for char in path)
    destination = f"{encoded}{suffix}"
    return f"<{destination}>" if not angle and _NEEDS_ANGLE.search(encoded) else destination


def local_target(destination: str) -> LocalTarget | None:
    """The workspace file a link destination points to, or ``None`` for anything else.

    URLs with a scheme (``https:``, ``mailto:``, ``HTTPS:``...), fragment-only
    links, root-relative and protocol-relative paths (``/x``, ``//host``) and
    empty destinations are not local file links.
    """
    if not destination or destination.startswith(("#", "/")) or _SCHEME.match(destination):
        return None
    cut = len(destination)
    for marker in ("?", "#"):
        index = destination.find(marker)
        if index >= 0:
            cut = min(cut, index)
    raw_path = destination[:cut]
    if not raw_path:
        return None
    return LocalTarget(unquote(_ESCAPE.sub(r"\1", raw_path)), raw_path, destination[cut:])
