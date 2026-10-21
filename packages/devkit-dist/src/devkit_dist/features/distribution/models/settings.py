"""Distribution selection grammars and search limits."""

import re

from devkit_dist.features.search import SearchMode

AGENT_NAMES = ("antigravity", "claude-code", "codex")
SLUG = re.compile(r"[a-z][a-z0-9-]*\Z")
DEFAULT_PRESET = ""
DEFAULT_PLAYBOOK_MIN_SIMILARITY = 0.35
DEFAULT_PLAYBOOK_MODE = SearchMode.AUTO
DEFAULT_PLAYBOOK_MAX_BYTES = 8192
DEFAULT_PLAYBOOK_MIN_SCORE = 0.1
DEFAULT_PLAYBOOK_LIMIT = 5
PLAYBOOK_MAX_BYTES_MIN, PLAYBOOK_MAX_BYTES_MAX = 1024, 65536
PLAYBOOK_LIMIT_MIN, PLAYBOOK_LIMIT_MAX = 1, 20
