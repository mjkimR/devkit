"""Assert that agent guidance states a rule, without pinning its wording.

A guidance test checks that a rule is still stated, not how it is phrased: ``assert_rule`` passes when one block of
the Markdown (a paragraph, a list item with its continuation lines, a table row or a heading) contains every token,
case-insensitively and across line wraps. Tokens are the identifiers and the few words that carry the rule (a code,
a command, a path, "never delete"); a rewording that keeps them passes, and a rule that is dropped or split apart
fails. Negative checks (a phrase that must be gone) stay plain ``not in`` assertions.
"""

from __future__ import annotations

import re

_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_FENCE = re.compile(r"^\s*(```|~~~)")


def blocks(markdown: str) -> list[str]:
    """The Markdown's blocks, each with whitespace collapsed and lowercased; fenced code is one block."""
    found: list[list[str]] = []
    current: list[str] = []
    fenced = False

    def close() -> None:
        if current:
            found.append(current.copy())
            current.clear()

    for line in markdown.splitlines():
        if _FENCE.match(line):
            if fenced:
                current.append(line)
                close()
            else:
                close()
                current.append(line)
            fenced = not fenced
            continue
        if fenced:
            current.append(line)
        elif not line.strip():
            close()
        elif line.lstrip().startswith(("#", "|")) or _ITEM.match(line):
            close()
            current.append(line)
            if not _ITEM.match(line):
                close()
        else:
            current.append(line)
    close()
    return [" ".join(" ".join(block).split()).lower() for block in found]


def states_rule(markdown: str, *tokens: str) -> bool:
    """Whether one block of ``markdown`` contains every token (case-insensitive, whitespace-collapsed)."""
    wanted = [" ".join(token.split()).lower() for token in tokens]
    return any(all(token in block for token in wanted) for block in blocks(markdown))


def assert_rule(markdown: str, *tokens: str) -> None:
    """Fail unless one block of ``markdown`` contains every token; see the module docstring."""
    assert tokens, "assert_rule needs at least one token"
    assert states_rule(markdown, *tokens), f"no single paragraph, list item, row or heading states all of {tokens!r}"
