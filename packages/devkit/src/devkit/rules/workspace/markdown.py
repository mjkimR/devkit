"""Markdown helpers shared by rules and by other engines that read the same files.

Two scanners live here so every reader agrees on them:

- ``prose_lines`` yields the lines outside fenced code blocks (CommonMark
  fences: a run of three or more backticks or tildes, closed only by a run of
  the same character at least as long with nothing after it; a backtick run
  with another backtick later on its line is not a fence). Link extraction
  and the checklist counter both use it; ``fenced_lines`` yields the lines
  inside, and ``code_spans`` the inline code of a prose line.
- ``count_tasks`` is the single checklist counter: a rule that reasons about
  task completion and a workflow check that gates on it must agree on what a
  task is.

Lines end with ``\\n`` only, as in ``devkit.core.frontmatter``; a ``\\r``
before it stays part of the line.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from urllib.parse import unquote

from devkit.core import FrontmatterError
from devkit.core.frontmatter import locate

_CHECKLIST_ITEM = re.compile(r"^[ \t]*[-*+][ \t]+\[([ xX])\][ \t]+")


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


def split_lines(text: str) -> list[str]:
    """``text`` split on ``\\n`` without the terminators; ``"\\n".join`` restores it exactly."""
    return text.split("\n")


def _lines(text: str, first_line: int) -> Iterator[tuple[int, str, bool]]:
    """``(line_number, line, fenced)`` for every line of ``text`` except fence delimiter lines."""
    fence = ""
    for offset, line in enumerate(split_lines(text)):
        stripped = line.strip()
        run = _fence_run(stripped)
        if not fence:
            if run:
                fence = run
                continue
            yield first_line + offset, line, False
            continue
        if run and run[0] == fence[0] and len(run) >= len(fence) and not stripped[len(run) :].strip():
            fence = ""
            continue
        yield first_line + offset, line, True


def prose_lines(text: str, *, first_line: int = 1) -> Iterator[tuple[int, str]]:
    """``(line_number, line)`` for every line of ``text`` outside fenced code blocks.

    ``first_line`` is the number of the first line of ``text`` in its document.
    Fence delimiter lines themselves are not yielded.
    """
    return ((number, line) for number, line, fenced in _lines(text, first_line) if not fenced)


def fenced_lines(text: str, *, first_line: int = 1) -> Iterator[tuple[int, str]]:
    """``(line_number, line)`` for every line of ``text`` inside fenced code blocks, delimiter lines excluded.

    An unclosed fence runs to the end of ``text``, as in CommonMark.
    """
    return ((number, line) for number, line, fenced in _lines(text, first_line) if fenced)


def count_tasks(text: str) -> tuple[int, int]:
    """Return ``(checked, total)`` Markdown checklist items.

    Counts ``- [ ]``, ``- [x]`` and ``- [X]`` items (also with ``*`` and ``+``
    markers, any indentation, and at least one space or tab after the box)
    outside the leading YAML frontmatter (``devkit.core.frontmatter`` grammar)
    and outside fenced code blocks. A frontmatter block that is never closed
    leaves no body, so such a text has no tasks.
    """
    try:
        block = locate(text)
    except FrontmatterError:
        return 0, 0
    body = text[block.end :] if block is not None else text
    checked = total = 0
    for _, line in prose_lines(body):
        match = _CHECKLIST_ITEM.match(line)
        if match is None:
            continue
        total += 1
        if match.group(1) != " ":
            checked += 1
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
