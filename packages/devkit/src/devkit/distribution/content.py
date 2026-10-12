"""File contents as devkit records them: bytes plus a normalized mode, their digest and canonical JSON.

Neutral helpers shared by bundle packaging (``devkit.distribution.bundles``)
and installation (``devkit.distribution.installation``); they know nothing
about the consumer workspace.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


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
