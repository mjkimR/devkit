from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .manifest import BundleError

FIELDS = {"name", "description", "aliases"}
# Extension keys: kept for other tools, never indexed by search nor shown by devkit.
EXTENSION_KEY = re.compile(r"x-[a-z][a-z0-9-]*\Z")


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
        lines = data.decode("utf-8").splitlines(keepends=True)
    except UnicodeError as exc:
        raise BundleError(f"{context}: playbook must be UTF-8") from exc
    if not lines or lines[0].strip() != "---":
        raise BundleError(f"{context}: playbook requires YAML frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() in {"---", "..."}), None)
    if end is None:
        raise BundleError(f"{context}: unclosed playbook frontmatter")
    header = "".join(lines[1:end])
    if len(header.encode()) > 4096:
        raise BundleError(f"{context}: playbook frontmatter exceeds 4096 bytes")
    require_english_text(header, f"{context}.frontmatter")
    try:
        node = yaml.compose(header, Loader=yaml.SafeLoader)
        if not isinstance(node, yaml.MappingNode):
            raise BundleError(f"{context}: frontmatter must be a mapping")
        keys = [key.value for key, _ in node.value if isinstance(key, yaml.ScalarNode)]
        if len(keys) != len(node.value) or len(keys) != len(set(keys)):
            raise BundleError(f"{context}: duplicate or non-scalar frontmatter keys")
        metadata = yaml.safe_load(header)
    except yaml.YAMLError as exc:
        raise BundleError(f"{context}: invalid YAML frontmatter") from exc
    if not isinstance(metadata, dict) or any(
        key not in FIELDS and not EXTENSION_KEY.fullmatch(str(key)) for key in metadata
    ):
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
