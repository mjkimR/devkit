"""Distribution selection grammars and search limits."""

import re

from devkit_dist.features.search import SearchMode

# Agents devkit projects native assets for; also the only valid ``variants`` and ``[subagents.levels.<level>]`` keys.
AGENT_NAMES = ("antigravity", "claude-code", "codex")
SLUG = re.compile(r"[a-z][a-z0-9-]*\Z")
# A requested preset that stands for the bundle's ``default_preset`` (a bare ``bundle`` on the command line).
DEFAULT_PRESET = ""
# ``devkit playbook search`` bounds: the ``[playbooks]`` table, the command's options and the library all check these.
# Measured on English metadata: keeps most matches while dropping the long tail of weak cosine similarities.
DEFAULT_PLAYBOOK_MIN_SIMILARITY = 0.35
DEFAULT_PLAYBOOK_MODE = SearchMode.AUTO
DEFAULT_PLAYBOOK_MAX_BYTES = 8192
DEFAULT_PLAYBOOK_MIN_SCORE = 0.1
DEFAULT_PLAYBOOK_LIMIT = 5
PLAYBOOK_MAX_BYTES_MIN, PLAYBOOK_MAX_BYTES_MAX = 1024, 65536
PLAYBOOK_LIMIT_MIN, PLAYBOOK_LIMIT_MAX = 1, 20
