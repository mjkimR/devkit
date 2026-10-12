"""YAML frontmatter helpers that preserve every byte outside the keys they touch."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DELIM = "---"


class FrontmatterError(ValueError):
    """Raised when a document has no usable frontmatter block."""


def split(text: str) -> tuple[str | None, str]:
    """Return (frontmatter_yaml, body). ``None`` frontmatter means no block."""
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith(DELIM + "\n"):
        return None, normalized
    rest = normalized[len(DELIM) + 1 :]
    idx = rest.find("\n" + DELIM + "\n")
    if idx < 0:
        if rest.endswith("\n" + DELIM):
            return rest[: -len(DELIM) - 1], ""
        return None, normalized
    return rest[:idx], rest[idx + len(DELIM) + 2 :]


def parse(text: str) -> dict[str, Any]:
    """Parse the frontmatter mapping; a missing or non-mapping block yields ``{}``."""
    front, _ = split(text)
    if front is None:
        return {}
    try:
        data = yaml.safe_load(front)
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"invalid YAML frontmatter: {exc}") from exc
    return data if isinstance(data, dict) else {}


def read(path: Path) -> dict[str, Any]:
    return parse(path.read_text("utf-8"))


def field(data: dict[str, Any], name: str) -> str:
    """Top-level scalar as a string; missing or null is ``""``."""
    value = data.get(name)
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def update(text: str, updates: dict[str, str]) -> str:
    """Replace or append top-level ``key: value`` lines, keeping every other byte.

    Only unindented lines whose key is in ``updates`` are replaced; nested keys with
    the same name are untouched. New keys are appended before the closing delimiter.
    """
    nl = "\r\n" if "\r\n" in text else "\n"
    if not text.startswith(DELIM + nl):
        raise FrontmatterError("document has no frontmatter block")
    rest = text[len(DELIM) + len(nl) :]
    end = rest.find(nl + DELIM)
    if end < 0:
        raise FrontmatterError("closing frontmatter delimiter not found")
    front, tail = rest[:end], rest[end:]
    kept: list[str] = []
    for line in front.split(nl):
        key = line.split(":", 1)[0].strip()
        if key in updates and not line.startswith((" ", "\t")):
            continue
        kept.append(line)
    kept.extend(f"{key}: {value}" for key, value in updates.items())
    return DELIM + nl + nl.join(kept) + tail


def render(data: dict[str, Any], body: str) -> str:
    """Build a new document with a frontmatter block followed by ``body``."""
    front = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).rstrip("\n")
    return f"{DELIM}\n{front}\n{DELIM}\n{body}"
