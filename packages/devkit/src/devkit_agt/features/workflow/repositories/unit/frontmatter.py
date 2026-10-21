"""Anchor and document frontmatter on top of ``devkit_core.core.frontmatter``.

Reading uses the shared grammar. ``update`` rewrites top-level keys in place
and keeps every other character of the document, including comments, key order
and the body.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from devkit_core.base.errors import FrontmatterError
from devkit_core.core import frontmatter as core

__all__ = ["FrontmatterError", "field", "parse", "read", "render", "update"]


def parse(text: str) -> dict[str, Any]:
    """The frontmatter mapping; a document without a block yields ``{}``.

    Raises ``FrontmatterError`` for an unclosed block, invalid YAML, duplicate
    keys or a header that is not a mapping.
    """
    data = core.parse(text).data
    return data if data is not None else {}


def read(path: Path) -> dict[str, Any]:
    return parse(path.read_text("utf-8"))


def field(data: Mapping[str, Any], name: str) -> str:
    """Top-level scalar as a string; missing or null is ``""``, dates are ISO 8601."""
    value = data.get(name)
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _top_level_key(line: str) -> str | None:
    """The key of an unindented ``key: value`` line, else ``None``."""
    if not line.strip() or line[:1] in (" ", "\t", "#", "-") or ":" not in line:
        return None
    return line.split(":", 1)[0].strip().strip("'\"")


def _continues(lines: list[str], index: int) -> bool:
    """Whether ``lines[index]`` belongs to the value of the key line above it.

    Indented lines and column-0 sequence items continue a block value; a blank
    line continues it only when more continuation follows.
    """
    line = lines[index]
    if line[:1] in (" ", "\t", "-"):
        return True
    if line.strip():
        return False
    following = index + 1
    while following < len(lines) and not lines[following].strip():
        following += 1
    return following < len(lines) and lines[following][:1] in (" ", "\t", "-")


def update(text: str, updates: Mapping[str, str]) -> str:
    """Replace or append top-level ``key: value`` lines, keeping every other character.

    A replaced key loses its whole value, including the indented or sequence
    lines of a block value; nested keys with the same name are untouched. New
    keys are appended at the end of the header. Values are written verbatim and
    must already be valid YAML scalars or flow collections. A document without
    a block gets one, inserted before its first line, holding ``updates``.

    Raises ``FrontmatterError`` when the text opens a block that never closes.
    """
    block = core.locate(text)
    if block is None:
        start = 1 if text.startswith(core.BOM) else 0
        first = text[start:].split("\n", 1)[0]
        newline = "\r\n" if first.endswith("\r") else "\n"
        header = "".join(f"{key}: {value}{newline}" for key, value in updates.items())
        return f"{text[:start]}{core.OPENER}{newline}{header}{core.OPENER}{newline}{text[start:]}"
    newline = block.newline or "\n"
    header = block.header
    lines = header[:-1].split("\n") if header else []
    kept: list[str] = []
    index = 0
    while index < len(lines):
        key = _top_level_key(lines[index])
        if key is not None and key in updates:
            index += 1
            while index < len(lines) and _continues(lines, index):
                index += 1
            continue
        kept.append(lines[index])
        index += 1
    carriage = "\r" if newline == "\r\n" else ""
    kept.extend(f"{key}: {value}{carriage}" for key, value in updates.items())
    rebuilt = "\n".join(kept) + "\n" if kept else ""
    return text[: block.header_start] + rebuilt + text[block.header_end :]


def render(data: Mapping[str, Any], body: str) -> str:
    """Build a new document with a frontmatter block followed by ``body``."""
    front = yaml.safe_dump(dict(data), sort_keys=False, allow_unicode=True).rstrip("\n")
    return f"{core.OPENER}\n{front}\n{core.OPENER}\n{body}"
