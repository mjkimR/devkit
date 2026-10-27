"""The one YAML frontmatter grammar every devkit package reads.

Grammar:

- An optional UTF-8 byte order mark (``U+FEFF``) at the start of the text is
  ignored.
- The opener is the first line of the text when it equals ``---`` after
  trailing whitespace is removed (so ``"--- "`` and ``"---\\r\\n"`` open a
  block, ``" ---"`` does not). Without an opener the text has no frontmatter.
- The closer is the next line equal to ``---`` or ``...`` after trailing
  whitespace is removed. An opener without a closer is a ``FrontmatterError``.
- Lines end with ``\\n``; a ``\\r`` before it is trailing whitespace. No other
  character ends a line.
- The header between opener and closer must be a YAML mapping with string
  keys; an empty header is ``{}``. Duplicate keys, at any nesting level, are a
  ``FrontmatterError``. Dates and timestamps stay ``datetime.date`` /
  ``datetime.datetime`` objects; callers normalize them.

``locate`` returns the block's character offsets without parsing YAML, so a
caller can rewrite the header and keep every other character of the text.
``parse`` returns the mapping and the body. ``scalar`` renders a string as a
one-line YAML scalar for a ``key: value`` header line.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

from devkit_core.base.errors import FrontmatterError
from devkit_core.core.yaml import require_libyaml, safe_load

BOM = "﻿"
OPENER = "---"
CLOSERS = frozenset({"---", "..."})
# Characters YAML reads as a line break; a value holding one is never written plain.
_LINE_BREAKS = frozenset("\n\r\x85\u2028\u2029")


@dataclass(frozen=True)
class FrontmatterBlock:
    """Character offsets of a frontmatter block inside the text given to ``locate``.

    ``text[start:header_start]`` is the opener line with its line ending,
    ``text[header_start:header_end]`` the YAML header (``header``), and
    ``text[header_end:end]`` the closer line with its line ending, if any.
    The body is ``text[end:]``. ``start`` is 1 when the text begins with a
    byte order mark, else 0. ``newline`` is the opener's line ending
    (``"\\n"`` or ``"\\r\\n"``); ``body_line`` is the 1-based line number
    of the first body line.
    """

    start: int
    header_start: int
    header_end: int
    end: int
    header: str
    closer: str
    newline: str
    body_line: int


@dataclass(frozen=True)
class Frontmatter:
    """A parsed document.

    ``data`` is ``None`` when the text has no frontmatter block. ``body`` is
    the text after the closer line (the whole text, without a byte order mark,
    when there is no block). ``body_line`` is the 1-based line number of the
    body's first line in the original text: add ``body_line - 1`` to a line
    number counted inside ``body`` to get the line in the document.
    """

    data: dict[str, Any] | None
    body: str
    body_line: int


def _lines(text: str, offset: int) -> list[tuple[int, int]]:
    """``(start, end)`` offsets of each ``\\n``-terminated line from ``offset``; ``end`` includes the newline."""
    spans: list[tuple[int, int]] = []
    position = offset
    length = len(text)
    while position < length:
        newline = text.find("\n", position)
        end = length if newline < 0 else newline + 1
        spans.append((position, end))
        position = end
    return spans


def locate(text: str) -> FrontmatterBlock | None:
    """Find the frontmatter block of ``text`` without parsing it; ``None`` when there is none.

    Raises ``FrontmatterError`` when the text opens a block that never closes.
    """
    start = 1 if text.startswith(BOM) else 0
    lines = _lines(text, start)
    if not lines:
        return None
    first_start, first_end = lines[0]
    if text[first_start:first_end].rstrip() != OPENER:
        return None
    opener_line = text[first_start:first_end]
    newline = "\r\n" if opener_line.endswith("\r\n") else ("\n" if opener_line.endswith("\n") else "")
    for index, (line_start, line_end) in enumerate(lines[1:], start=1):
        stripped = text[line_start:line_end].rstrip()
        if stripped in CLOSERS:
            return FrontmatterBlock(
                start=start,
                header_start=first_end,
                header_end=line_start,
                end=line_end,
                header=text[first_end:line_start],
                closer=stripped,
                newline=newline,
                body_line=index + 2,
            )
    raise FrontmatterError("frontmatter opened with '---' is never closed by a '---' or '...' line")


def _strict_loader(base: type[Any]) -> type[Any]:
    """Apply the frontmatter duplicate-key check to LibYAML's safe loader."""

    class StrictLoader(base):
        """Safe YAML loader that rejects duplicate mapping keys at every nesting level."""

        def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Any, Any]:
            seen: list[Any] = []
            for key_node, _ in node.value:
                if key_node.tag == "tag:yaml.org,2002:merge":
                    continue  # merged keys may be overridden explicitly
                key = self.construct_object(key_node, deep=True)
                if key in seen:
                    raise ConstructorError(
                        "while constructing a mapping",
                        node.start_mark,
                        f"found duplicate key {key!r}",
                        key_node.start_mark,
                    )
                seen.append(key)
            return super().construct_mapping(node, deep=deep)

    return StrictLoader


def load_header(header: str, *, line_offset: int = 0, source: str = "document frontmatter") -> dict[str, Any]:
    """Parse a frontmatter header (the YAML between the delimiters) into a mapping.

    Raises ``FrontmatterError`` for invalid YAML (including an impossible date
    such as ``2024-02-30`` and nesting too deep to parse), duplicate keys, a
    value that is not a mapping, or a top-level key that is not a string.
    """
    loader = _strict_loader(require_libyaml(source=source))
    try:
        data = safe_load(header, source=source, loader=loader)
    except RecursionError as exc:
        raise FrontmatterError("invalid YAML frontmatter: nested too deeply") from exc
    except (yaml.YAMLError, ValueError) as exc:  # PyYAML may raise ValueError for an impossible date
        mark = getattr(exc, "problem_mark", None)
        location = (
            f" at document line {line_offset + mark.line + 1}, column {mark.column + 1}" if mark is not None else ""
        )
        raise FrontmatterError(f"invalid YAML frontmatter{location}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise FrontmatterError(f"frontmatter must be a YAML mapping, not {type(data).__name__}")
    for key in data:
        if not isinstance(key, str):
            raise FrontmatterError(f"frontmatter keys must be strings; quote the key {key!r}")
    return data


def parse(text: str) -> Frontmatter:
    """Split ``text`` into its frontmatter mapping and body (see the module grammar)."""
    block = locate(text)
    if block is None:
        return Frontmatter(None, text[1:] if text.startswith(BOM) else text, 1)
    header_line = text.count("\n", 0, block.header_start) + 1
    return Frontmatter(load_header(block.header, line_offset=header_line - 1), text[block.end :], block.body_line)


def _reads_back(value: str) -> bool:
    """Whether ``value`` written plain reads back as the same string, as a mapping value and as a list item."""
    try:
        mapping = safe_load(f"k: {value}", source="frontmatter scalar")
        sequence = safe_load(f"- {value}", source="frontmatter scalar")
    except (yaml.YAMLError, ValueError, RecursionError):  # ValueError: an impossible date such as 2024-02-30
        return False
    return mapping == {"k": value} and sequence == [value]


def scalar(value: str) -> str:
    """``value`` as a one-line YAML scalar for a ``key: value`` header line or a ``- value`` list item.

    Plain when it reads back as the same string (``plain title``, ``PROP-x``); otherwise single-quoted
    (``'A: B'``, ``'off'``, ``''``), or double-quoted with escapes when it holds a line break or a character a
    single-quoted scalar cannot carry (``"a\\nb"``), so the result never spans lines.
    """
    if not _LINE_BREAKS.intersection(value) and _reads_back(value):
        return value
    style = '"' if _LINE_BREAKS.intersection(value) else "'"
    dumped = yaml.safe_dump(value, default_style=style, allow_unicode=True, width=2**31)
    return dumped.removesuffix("\n")
