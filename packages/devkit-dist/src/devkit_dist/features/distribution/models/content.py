"""File contents as devkit records them: bytes plus a normalized mode, their digest and canonical JSON.

Neutral helpers shared by bundle packaging (``devkit_dist.features.distribution.services.bundles``)
and installation (``devkit_dist.features.distribution.services.installation``); they know nothing
about the consumer workspace. ``is_by_product`` is the one filter of editing by-products that bundle sources and
snapshot trees skip.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import PurePath

# By-products of editing a source in place (Finder metadata, bytecode caches); never bundle or snapshot content.
IGNORED_NAMES = frozenset({".DS_Store", "__pycache__"})
IGNORED_SUFFIXES = (".pyc",)


def is_by_product(rel: PurePath) -> bool:
    """Whether the path ``rel``, relative to the tree it was found in, is an editing by-product, or lies inside one."""
    return any(part in IGNORED_NAMES for part in rel.parts) or rel.name.endswith(IGNORED_SUFFIXES)


@dataclass(frozen=True)
class Content:
    """A file's bytes and permission mode."""

    data: bytes
    mode: int


def normal_mode(mode: int) -> int:
    """The mode devkit records and compares: ``0o755`` when any execute bit is set, else ``0o644``.

    Group-writable checkouts (umask ``002``) and other permission noise are not edits.
    """
    return 0o755 if mode & 0o111 else 0o644


def same_content(left: Content | None, right: Content | None) -> bool:
    """Equal bytes and equal normalized mode (``None`` means absent)."""
    if left is None or right is None:
        return left is right
    return left.data == right.data and normal_mode(left.mode) == normal_mode(right.mode)


def sha256(data: bytes) -> str:
    """The hex SHA-256 digest devkit records for file contents and asset digests."""
    return hashlib.sha256(data).hexdigest()


def json_content(value: object) -> Content:
    """``value`` as the canonical JSON devkit writes (sorted keys, two-space indent, final newline), mode ``0o644``."""
    return Content((json.dumps(value, sort_keys=True, indent=2) + "\n").encode(), 0o644)


def signature(content: Content) -> tuple[str, int]:
    """``(sha256, normalized mode)``: what the receipt records for a file."""
    return sha256(content.data), normal_mode(content.mode)
