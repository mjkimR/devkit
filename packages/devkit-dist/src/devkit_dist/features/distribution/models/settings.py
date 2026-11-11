"""Distribution selection grammars, native agent directories and search defaults."""

from devkit_dist.features.project import SLUG as SLUG
from devkit_dist.features.search import SearchMode

# Agent name -> (skill directory, subagent directory) of its native projections. Codex and Antigravity share the
# ``.agents/skills`` standard, so identical skill projections are written once.
NATIVE_DIRS = {
    "codex": (".agents/skills", ".codex/agents"),
    "claude-code": (".claude/skills", ".claude/agents"),
    "antigravity": (".agents/skills", ".agents/agents"),
}
# Agents devkit projects native assets for; also the only valid ``variants`` and ``[subagents.levels.<level>]`` keys.
AGENT_NAMES = tuple(sorted(NATIVE_DIRS))
# The workspace roots of the native projections (``.agents``, ``.claude``, ``.codex``).
NATIVE_ROOTS = tuple(sorted({path.split("/", 1)[0] for paths in NATIVE_DIRS.values() for path in paths}))
# Workspace roots owned by devkit, Git or the agent projections: no seeded target or snapshot destination enters one.
# Compared case-insensitively: on a case-insensitive file system ``.GIT`` is ``.git``.
PROTECTED_ROOTS = frozenset({".devkit", ".git", *NATIVE_ROOTS})
# A requested preset that stands for the bundle's ``default_preset`` (a bare ``bundle`` on the command line).
DEFAULT_PRESET = ""
# ``devkit playbook search`` defaults; the bounds every reader checks are ``devkit_dist.features.project``'s.
# Measured on English metadata: keeps most matches while dropping the long tail of weak cosine similarities.
DEFAULT_PLAYBOOK_MIN_SIMILARITY = 0.35
DEFAULT_PLAYBOOK_MODE = SearchMode.AUTO
DEFAULT_PLAYBOOK_MAX_BYTES = 8192
DEFAULT_PLAYBOOK_MIN_SCORE = 0.1
DEFAULT_PLAYBOOK_LIMIT = 5
