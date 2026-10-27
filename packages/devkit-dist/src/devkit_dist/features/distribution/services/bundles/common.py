"""Names shared by every bundle module: grammars, the reserved preset, shared-skill agents, and frontmatter reading."""

from __future__ import annotations

import re
from typing import Any

from devkit_core.base.errors import FrontmatterError
from devkit_core.core import frontmatter
from devkit_core.core.frontmatter import FrontmatterBlock

from devkit_dist.features.distribution.models.errors import BundleError

VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")
# Frontmatter extension keys (``x-<name>``): kept for other tools, never interpreted by devkit.
EXTENSION_KEY = re.compile(r"x-[a-z][a-z0-9-]*\Z")
# Reserved preset available in every bundle; selects every declared asset.
ALL = "all"
# Agents reading one shared skill directory (``.agents/skills``): their skill variants must be identical.
SHARED_SKILL_AGENTS = ("codex", "antigravity")


def locate_frontmatter(data: bytes, context: str, kind: str) -> tuple[str, FrontmatterBlock | None]:
    """The UTF-8 text of a bundle document and its frontmatter block (``None`` without one), unparsed.

    Raises ``BundleError`` naming ``context`` when the bytes are not UTF-8 or
    a block is opened and never closed.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise BundleError(f"{context}: {kind} must be UTF-8") from exc
    try:
        return text, frontmatter.locate(text)
    except FrontmatterError as exc:
        raise BundleError(f"{context}: {exc}") from exc


def read_frontmatter(data: bytes, context: str, kind: str) -> tuple[str, FrontmatterBlock, dict[str, Any]]:
    """The text, frontmatter block and parsed header of a bundle document that requires frontmatter.

    Raises ``BundleError`` naming ``context`` for every failure: not UTF-8, no
    frontmatter, an unclosed block, invalid YAML.
    """
    text, block = locate_frontmatter(data, context, kind)
    if block is None:
        raise BundleError(f"{context}: {kind} requires YAML frontmatter")
    try:
        return text, block, frontmatter.load_header(block.header)
    except FrontmatterError as exc:
        raise BundleError(f"{context}: {exc}") from exc
