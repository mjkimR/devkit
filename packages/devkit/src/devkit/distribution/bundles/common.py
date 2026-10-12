"""Names shared by every bundle module: the error type, slug and version grammars, agents."""

from __future__ import annotations

import re

SLUG = re.compile(r"[a-z][a-z0-9-]*\Z")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")
# Reserved preset available in every bundle; selects every declared asset.
ALL = "all"
# Agents devkit projects native assets for; also the only valid ``variants`` keys.
AGENT_NAMES = ("antigravity", "claude-code", "codex")


class BundleError(ValueError):
    """Invalid bundle input, or a distribution operation that cannot proceed."""
