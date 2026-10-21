"""The identifier grammar shared by workflow ids, stage ids, gates, roles, check names and envelope kinds."""

from __future__ import annotations

import re

IDENT_PATTERN = r"[a-z][a-z0-9-]*"
IDENT_HINT = IDENT_PATTERN
IDENT = re.compile(IDENT_PATTERN)


def is_ident(value: object) -> bool:
    """Whether ``value`` is a string matching ``[a-z][a-z0-9-]*`` in full (a trailing newline does not match)."""
    return isinstance(value, str) and IDENT.fullmatch(value) is not None
