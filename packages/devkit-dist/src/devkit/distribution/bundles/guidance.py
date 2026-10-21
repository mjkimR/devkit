"""The context prerequisite devkit prepends to the skills of a bundle that has a context."""

from __future__ import annotations

from devkit_core.core import frontmatter

from devkit.distribution.bundles.common import locate_frontmatter

CONTEXT_START = "<!-- DEVKIT:CONTEXT -->"
CONTEXT_END = "<!-- /DEVKIT:CONTEXT -->"


def context_prerequisite(bundle: str) -> str:
    return (
        f"{CONTEXT_START}\n"
        f"Required first: `uv run devkit get-context {bundle}`, once per bundle per agent context"
        " (skip if already loaded; reload after compaction). Apply the full constitution;"
        " read instruction bodies only when relevant.\n"
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
