"""``guidance`` assets: fragments ``devkit sync`` renders into the root ``AGENTS.md`` guidance block.

The block is read on every agent turn, so a fragment is a few Markdown list
items (``- `` lines and two-space continuation lines) of at most
``MAX_FRAGMENT_BYTES`` UTF-8 bytes. It may not contain HTML comment syntax,
so it can never forge or close the block markers. ``{path:<asset-id>}`` names
another single-file asset of the same bundle; sync replaces it with the
workspace path agents read (the project override, else the managed copy).
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from devkit.distribution.errors import BundleError

MAX_FRAGMENT_BYTES = 300
PLACEHOLDER = re.compile(r"\{path:([a-z][a-z0-9-]*)\}")


def read_fragment(data: bytes, context: str) -> str:
    """The fragment text without trailing newlines; ``BundleError`` naming ``context`` when the block cannot hold it."""
    if len(data) > MAX_FRAGMENT_BYTES:
        raise BundleError(f"{context}: a guidance fragment is limited to {MAX_FRAGMENT_BYTES} bytes, not {len(data)}")
    try:
        text = data.decode("utf-8").rstrip("\n")
    except UnicodeError as exc:
        raise BundleError(f"{context}: a guidance fragment must be UTF-8") from exc
    if "\r" in text:
        raise BundleError(f"{context}: a guidance fragment uses LF line endings")
    if "<!--" in text or "-->" in text:
        raise BundleError(f"{context}: a guidance fragment may not contain HTML comment markers")
    lines = text.split("\n")
    for number, line in enumerate(lines, 1):
        item = line.startswith("- ") and line[2:].strip()
        continuation = number > 1 and line.startswith("  ") and line.strip()
        if not (item or continuation):
            raise BundleError(
                f"{context}: line {number}: a guidance fragment holds Markdown list items only"
                " ('- ' lines and two-space continuation lines, no blank lines)"
            )
    return text


def references(text: str) -> list[str]:
    """Asset IDs named by ``{path:<asset-id>}`` placeholders, in order of first use."""
    return list(dict.fromkeys(PLACEHOLDER.findall(text)))


def render_fragment(text: str, paths: Mapping[str, str]) -> str:
    """``text`` with every placeholder replaced by the workspace path ``paths`` gives its asset."""
    return PLACEHOLDER.sub(lambda match: paths[match.group(1)], text)
