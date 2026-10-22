"""``playbook`` assets: occasional procedures found by ``devkit playbook search`` through their frontmatter.

``aliases`` are previous asset IDs of the playbook in the same bundle (``ADR-playbook-aliases-as-identifiers``): each
matches the manifest slug grammar, and ``devkit playbook get <bundle>/<alias>`` resolves one. They are identity, not
search text. Uniqueness within the bundle is checked by the manifest and again at retrieval.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.services.bundles.common import EXTENSION_KEY, SLUG, read_frontmatter

FIELDS = {"name", "description", "aliases"}
MAX_HEADER_BYTES = 4096


@dataclass(frozen=True)
class PlaybookHeader:
    name: str
    description: str
    aliases: tuple[str, ...]
    extensions: tuple[tuple[str, Any], ...] = ()


def is_latin_text(value: str) -> bool:
    """Whether every letter of ``value`` is Latin; actual English language use remains an authoring rule."""
    return not any(char.isalpha() and "LATIN" not in unicodedata.name(char, "") for char in value)


def _require_english(value: str, context: str) -> None:
    if not is_latin_text(value):
        raise BundleError(f"{context}: use English text (non-Latin letters are not supported)")


def playbook_entry(root: Path, source: str) -> Path:
    path = root / source
    if path.is_dir():
        path /= "SKILL.md"
    if not path.is_file() or path.suffix.lower() != ".md":
        raise BundleError(f"{source}: playbook must be a Markdown file or directory containing SKILL.md")
    return path


def read_playbook_header(data: bytes, context: str) -> PlaybookHeader:
    _, block, metadata = read_frontmatter(data, context, "playbook")
    if len(block.header.encode()) > MAX_HEADER_BYTES:
        raise BundleError(f"{context}: playbook frontmatter exceeds {MAX_HEADER_BYTES} bytes")
    _require_english(block.header, f"{context}.frontmatter")
    if any(key not in FIELDS and not EXTENSION_KEY.fullmatch(key) for key in metadata):
        raise BundleError(f"{context}: supported frontmatter fields are name, description, aliases and x-<name>")
    for field in ("name", "description"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            raise BundleError(f"{context}: {field} must be a nonempty string")
        _require_english(value, f"{context}.{field}")
    aliases = metadata.get("aliases", [])
    if not isinstance(aliases, list) or not all(isinstance(v, str) and SLUG.fullmatch(v) for v in aliases):
        raise BundleError(
            f"{context}: aliases must be an array of previous playbook asset IDs ([a-z][a-z0-9-]*)",
            fix="List previous asset IDs of this playbook in aliases; move search phrases into the description",
        )
    if len(set(aliases)) != len(aliases):
        raise BundleError(f"{context}: aliases must not repeat an ID")
    extensions = tuple((key, value) for key, value in metadata.items() if key not in FIELDS)
    return PlaybookHeader(metadata["name"].strip(), metadata["description"].strip(), tuple(aliases), extensions)
