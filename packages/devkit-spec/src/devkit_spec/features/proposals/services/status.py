"""Exact proposal status edits that preserve unrelated frontmatter and body text."""

from devkit_core.base.errors import FrontmatterError
from devkit_core.core.frontmatter import set_field


def accepted_text(text: str) -> str:
    """Replace the frontmatter status value, whatever it is, preserving comments, line endings and body
    (``set_field``).

    Raise ``ValueError`` when the frontmatter has no top-level ``status:`` line or never closes.
    A status-like line in the Markdown body never supplies the missing metadata.
    """
    try:
        updated = set_field(text, "status", "accepted", missing=None)
    except FrontmatterError as exc:
        raise ValueError("proposal frontmatter is never closed") from exc
    if updated is None:
        raise ValueError("proposal frontmatter has no replaceable status")
    return updated
