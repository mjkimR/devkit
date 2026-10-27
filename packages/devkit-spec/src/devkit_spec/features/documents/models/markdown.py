"""The Markdown body scanner behind reference extraction.

``visible_lines`` yields each body line with everything that is not prose
replaced by spaces, so character offsets still match the original text. Blocks
come from the shared scanner (``devkit_agt.features.rules.scan``):

- fenced and indented code blocks are left out entirely; HTML comments are
  blanked (a line wholly inside one is yielded blank);
- on top of that, backslash escapes, inline code spans (a backtick run closed
  by the next run of the same length) and ``~~strikethrough~~`` are blanked;
  a span may continue on the following lines of its paragraph (it ends at a
  blank line or a fence), and an opener that nothing closes is a literal;
- with ``mask_links``, a link or image label (``[label](...)``, ``[label][ref]``,
  ``[label]:`` and ``![alt]``) is blanked, so a link's text never counts as a
  bracket reference;
- with ``keep_id_spans``, a single-backtick code span holding exactly one
  document ID stays visible: `` `CAP-...` `` is how prose references a
  document.
"""

from __future__ import annotations

import itertools
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from devkit_agt.features.rules.models.markdown import LineKind, scan

from devkit_spec.features.documents.models.ids import is_id


@dataclass(frozen=True, slots=True)
class VisibleLine:
    """One body line: its 1-based ``number`` in the document, the ``offset`` of its first character in the
    document text, and its ``text`` (without the line ending) with non-prose characters blanked."""

    number: int
    offset: int
    text: str


def _closing_run(line: str, start: int, char: str, width: int) -> int:
    """Index of the next run of exactly ``width`` ``char`` characters at or after ``start``, else ``-1``."""
    index = start
    while index < len(line):
        if line[index] != char:
            index += 1
            continue
        end = index
        while end < len(line) and line[end] == char:
            end += 1
        if end - index == width:
            return index
        index = end
    return -1


# A line without any of these characters is all prose.
_SPECIAL = "`[\\~"
_NEXT_SPECIAL = re.compile(r"[`\[\\~]")


class _Masker:
    def __init__(self, *, mask_links: bool, keep_id_spans: bool) -> None:
        # The delimiter run (character, width) of a code or strikethrough span continuing from an earlier line.
        self.span: tuple[str, int] | None = None
        self.mask_links = mask_links
        self.keep_id_spans = keep_id_spans

    def visible(self, line: str, following: Iterable[str]) -> str:
        """``line`` with non-prose blanked; ``following`` are the next lines, read only to find where a span ends."""
        if self.span is None and not any(char in line for char in _SPECIAL):
            return line
        out = list(line)

        def blank(start: int, end: int) -> None:
            out[start:end] = " " * (end - start)

        index, size = 0, len(line)
        if self.span is not None:
            char, width = self.span
            close = _closing_run(line, 0, char, width)
            if close < 0:
                return " " * size
            blank(0, close + width)
            index, self.span = close + width, None
        while index < size:
            special = _NEXT_SPECIAL.search(line, index)
            if special is None:
                break
            index = special.start()
            char = line[index]
            if char == "\\" and index + 1 < size:
                blank(index, index + 2)
                index += 2
                continue
            if char == "`":
                run_end = index
                while run_end < size and line[run_end] == "`":
                    run_end += 1
                width = run_end - index
                close = _closing_run(line, run_end, "`", width)
                if close < 0:
                    if _closes_later(following, "`", width):
                        blank(index, size)
                        self.span = ("`", width)
                        break
                    index = run_end
                    continue
                finish = close + width
                if not (self.keep_id_spans and width == 1 and is_id(line[run_end:close])):
                    blank(index, finish)
                index = finish
                continue
            if char == "~" and line.startswith("~~", index):
                run_end = index
                while run_end < size and line[run_end] == "~":
                    run_end += 1
                close = _closing_run(line, run_end, "~", 2) if run_end - index == 2 else -1
                if close < 0:
                    if run_end - index == 2 and _closes_later(following, "~", 2):
                        blank(index, size)
                        self.span = ("~", 2)
                        break
                    index = run_end
                    continue
                blank(index, close + 2)
                index = close + 2
                continue
            if self.mask_links and char == "[":
                end = line.find("]", index)
                if end >= 0:
                    after = line[end + 1 : end + 2]
                    if (index > 0 and line[index - 1] == "!") or after in ("(", "[", ":"):
                        blank(index, end + 1)
            index += 1
        return "".join(out)


def _closes_later(following: Iterable[str], char: str, width: int) -> bool:
    """Whether a run of exactly ``width`` ``char`` appears on the following lines before the paragraph ends.

    A blank line ends the paragraph, and so does a fence opener (a ``~~~`` or a backtick fence indented at most three
    spaces), which interrupts a paragraph.
    """
    for line in following:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if not stripped or (indent <= 3 and stripped.startswith(("```", "~~~"))):
            return False
        if _closing_run(line, 0, char, width) >= 0:
            return True
    return False


def visible_lines(
    text: str, *, start: int = 0, first_line: int = 1, mask_links: bool = True, keep_id_spans: bool = True
) -> Iterator[VisibleLine]:
    """The prose lines of ``text[start:]`` (a document body), numbered from ``first_line``.

    Blank lines, fence delimiters, fenced code and indented code (as the shared scanner classifies them) are left
    out; a non-blank line wholly inside an HTML comment is yielded blank.
    """
    masker = _Masker(mask_links=mask_links, keep_id_spans=keep_id_spans)
    lines = text[start:].split("\n")
    for position, scanned in enumerate(scan(text, start=start, first_line=first_line)):
        if scanned.kind not in (LineKind.PROSE, LineKind.COMMENT):
            # A fence or a code block ends the paragraph, and with it any span left open.
            masker.span = None
        elif not scanned.line.strip():
            continue
        elif scanned.kind is LineKind.PROSE:
            following = itertools.islice(lines, position + 1, None)
            yield VisibleLine(scanned.number, scanned.offset, masker.visible(scanned.text, following))
        else:
            yield VisibleLine(scanned.number, scanned.offset, scanned.text)
