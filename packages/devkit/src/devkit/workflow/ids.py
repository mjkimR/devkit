"""The identifier grammar shared by workflow ids, stage ids, gates, roles, check names and envelope kinds."""

from __future__ import annotations

import re

IDENT_PATTERN = r"[a-z][a-z0-9-]*"
IDENT = re.compile(rf"^{IDENT_PATTERN}$")
IDENT_HINT = "[a-z][a-z0-9-]*"


def is_ident(value: object) -> bool:
    """Whether ``value`` is a string matching ``[a-z][a-z0-9-]*``."""
    return isinstance(value, str) and IDENT.match(value) is not None
