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


def update(text: str, updates: Mapping[str, str]) -> str:
    """Set top-level ``key: value`` lines in place, keeping every other character (``core.set_field`` per key).

    A present key is rewritten where it stands and keeps its trailing comment; it loses its whole old value,
    including the indented or sequence lines of a block value; nested keys with the same name are untouched. Missing
    keys are appended at the end of the header in ``updates`` order. Values are written verbatim and must already be
    valid YAML scalars or flow collections. A document without a block gets one, inserted before its first line,
    holding ``updates``.

    Raises ``FrontmatterError`` when the text opens a block that never closes.
    """
    for key, value in updates.items():
        text = core.set_field(text, key, value, missing="append")
    return text


def render(data: Mapping[str, Any], body: str) -> str:
    """Build a new document with a frontmatter block followed by ``body``."""
    front = yaml.safe_dump(dict(data), sort_keys=False, allow_unicode=True).rstrip("\n")
    return f"{core.OPENER}\n{front}\n{core.OPENER}\n{body}"
