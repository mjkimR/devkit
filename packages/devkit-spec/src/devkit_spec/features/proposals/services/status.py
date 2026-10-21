"""Exact proposal status edits that preserve unrelated frontmatter and body text."""

import re

# The frontmatter ``status:`` line (plain or quoted value); a trailing comment ("#" after whitespace) stays.
_STATUS = re.compile(r"""^status:[ \t]*(?:[A-Za-z-]+|"[A-Za-z-]*"|'[A-Za-z-]*')(?=[ \t]*\r?$|[ \t]+#)""", re.MULTILINE)


def accepted_text(text: str) -> str:
    """Replace the frontmatter status value, preserving comments, line endings and body.

    Raise ``ValueError`` when no replaceable status exists inside the frontmatter.
    A status-like line in the Markdown body never supplies the missing metadata.
    """
    end = _frontmatter_end(text)
    updated, count = _STATUS.subn("status: accepted", text[:end], count=1)
    if count != 1:
        raise ValueError("proposal frontmatter has no replaceable status")
    return updated + text[end:]


def _frontmatter_end(text: str) -> int:
    """The offset just past the closing ``---`` of the frontmatter (0 when there is none)."""
    match = re.match(r"---\r?\n.*?^---[ \t]*\r?$", text, re.DOTALL | re.MULTILINE)
    return match.end() if match else 0
