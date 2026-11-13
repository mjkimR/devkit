"""The context prerequisite devkit prepends to the skills of a bundle that has a context."""

from __future__ import annotations

from devkit_core.core import frontmatter

from devkit_dist.features.distribution.services.bundles.common import locate_frontmatter

CONTEXT_START = "<!-- DEVKIT:CONTEXT -->"
CONTEXT_END = "<!-- /DEVKIT:CONTEXT -->"


def requires_context(*, constitution: bool, instructions: bool, documents: str | None) -> bool:
    """Whether synchronized sources require a load, independent of runtime document listings."""
    return constitution or instructions or documents is not None


def context_prerequisite(bundle: str) -> str:
    return (
        f"{CONTEXT_START}\n"
        f"Required first, once per agent context and again after compaction: `uv run devkit get-context {bundle}`."
        " Apply its constitution; read instruction bodies only when relevant.\n"
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
