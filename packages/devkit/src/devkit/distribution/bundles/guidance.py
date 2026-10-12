"""The context prerequisite devkit prepends to the skills of a bundle that has a context."""

from __future__ import annotations

from devkit.core import frontmatter
from devkit.distribution.bundles.common import locate_frontmatter

CONTEXT_START = "<!-- DEVKIT:CONTEXT -->"
CONTEXT_END = "<!-- /DEVKIT:CONTEXT -->"


def context_prerequisite(bundle: str) -> str:
    return (
        f"{CONTEXT_START}\n"
        "Before performing this skill, load this bundle's context by running\n"
        f"`uv run devkit get-context {bundle}` from the consumer project.\n"
        "Run this only once per bundle in the current agent context, shared across\n"
        "all skills from this bundle. If its guidance is already available, skip\n"
        "the command. Read and apply the full constitution. The instruction catalog\n"
        "exposes headers and paths only; read an instruction body when relevant.\n"
        "If loading fails, resolve the failure before performing this skill.\n"
        "Reload only if\n"
        "the guidance is no longer available, for example after context compaction\n"
        "or in a new agent context.\n"
        f"{CONTEXT_END}\n\n"
    )


def prepend_context(data: bytes, bundle: str, context: str) -> bytes:
    """Insert the context prerequisite after the frontmatter; every other byte is kept.

    ``context`` names the skill file in a ``BundleError``.
    """
    text, block = locate_frontmatter(data, context, "skill")
    if block is None:
        offset = 1 if text.startswith(frontmatter.BOM) else 0
        prefix = text[:offset]
    else:
        offset = block.end
        prefix = text[:offset]
        prefix += "\n" if prefix.endswith("\n") else "\n\n"
    return (prefix + context_prerequisite(bundle) + text[offset:]).encode("utf-8")
