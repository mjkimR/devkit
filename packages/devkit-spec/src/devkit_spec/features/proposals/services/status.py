"""Exact proposal status edits that preserve unrelated frontmatter and body text."""

import re

from devkit_core.base.errors import FrontmatterError
from devkit_core.core.frontmatter import locate

# The frontmatter ``status:`` line (plain or quoted value); a trailing comment ("#" after whitespace) stays.
_STATUS = re.compile(r"""^status:[ \t]*(?:[A-Za-z-]+|"[A-Za-z-]*"|'[A-Za-z-]*')(?=[ \t]*\r?$|[ \t]+#)""", re.MULTILINE)


def accepted_text(text: str) -> str:
    """Replace the frontmatter status value, preserving comments, line endings and body.

    Raise ``ValueError`` when no replaceable status exists inside the frontmatter.
    A status-like line in the Markdown body never supplies the missing metadata.
    """
    try:
        block = locate(text)
    except FrontmatterError as exc:
        raise ValueError("proposal frontmatter is never closed") from exc
    end = block.end if block else 0
    updated, count = _STATUS.subn("status: accepted", text[:end], count=1)
    if count != 1:
        raise ValueError("proposal frontmatter has no replaceable status")
    return updated + text[end:]
