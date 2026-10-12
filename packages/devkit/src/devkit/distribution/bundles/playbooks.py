from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from devkit.core import frontmatter
from devkit.core.errors import FrontmatterError

from ..errors import BundleError

FIELDS = {"name", "description", "aliases"}
# Extension keys: kept for other tools, never indexed by search nor shown by devkit.
EXTENSION_KEY = re.compile(r"x-[a-z][a-z0-9-]*\Z")
MAX_HEADER_BYTES = 4096


@dataclass(frozen=True)
class PlaybookHeader:
    name: str
    description: str
    aliases: tuple[str, ...]
    extensions: tuple[tuple[str, Any], ...] = ()


def require_english_text(value: str, context: str) -> None:
    """Reject non-Latin prose; actual English language use remains an authoring rule."""
    if any(char.isalpha() and "LATIN" not in unicodedata.name(char, "") for char in value):
        raise BundleError(f"{context}: use English text (non-Latin letters are not supported)")


def playbook_entry(root: Path, source: str) -> Path:
    path = root / source
    if path.is_dir():
        path /= "SKILL.md"
    if not path.is_file() or path.suffix.lower() != ".md":
        raise BundleError(f"{source}: playbook must be a Markdown file or directory containing SKILL.md")
    return path


def read_playbook_header(data: bytes, context: str) -> PlaybookHeader:
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise BundleError(f"{context}: playbook must be UTF-8") from exc
    try:
        block = frontmatter.locate(text)
        if block is None:
            raise BundleError(f"{context}: playbook requires YAML frontmatter")
        if len(block.header.encode()) > MAX_HEADER_BYTES:
            raise BundleError(f"{context}: playbook frontmatter exceeds {MAX_HEADER_BYTES} bytes")
        require_english_text(block.header, f"{context}.frontmatter")
        metadata = frontmatter.load_header(block.header)
    except FrontmatterError as exc:
        raise BundleError(f"{context}: {exc}") from exc
    if any(key not in FIELDS and not EXTENSION_KEY.fullmatch(key) for key in metadata):
        raise BundleError(f"{context}: supported frontmatter fields are name, description, aliases and x-<name>")
    for field in ("name", "description"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            raise BundleError(f"{context}: {field} must be a nonempty string")
        require_english_text(value, f"{context}.{field}")
    aliases = metadata.get("aliases", [])
    if not isinstance(aliases, list) or not all(isinstance(v, str) and v.strip() for v in aliases):
        raise BundleError(f"{context}: aliases must be an array of nonempty strings")
    for alias in aliases:
        require_english_text(alias, f"{context}.aliases")
    extensions = tuple((key, value) for key, value in metadata.items() if key not in FIELDS)
    return PlaybookHeader(metadata["name"].strip(), metadata["description"].strip(), tuple(aliases), extensions)
