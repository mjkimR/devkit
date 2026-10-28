"""Shared text helpers: character classification and trailing YAML comments."""

import re
import unicodedata

_COMMENT = re.compile(r"[ \t]+#[^\r\n]*$")  # a trailing YAML comment: "#" after whitespace
_QUOTED = re.compile(r"\"(?:[^\"\\\r\n]|\\.)*\"|'(?:[^'\r\n]|'')*'")


def foreign_letters(text: str) -> list[str]:
    """The distinct letters of ``text`` outside the Latin script, in order of appearance."""
    found: list[str] = []
    for char in text:
        if char.isalpha() and "LATIN" not in unicodedata.name(char, "") and char not in found:
            found.append(char)
    return found


def trailing_comment(line: str, start: int) -> str | None:
    """The trailing YAML comment of the one-line value that starts at ``line[start:]`` (``None``: none).

    A ``#`` counts only after whitespace and outside a quoted scalar: ``"draft #2"`` is a value, not a comment. An
    unterminated quote has no comment.
    """
    value = len(line) - len(line[start:].lstrip(" \t"))
    if line[value : value + 1] in ('"', "'"):
        quoted = _QUOTED.match(line, value)
        if quoted is None:
            return None
        value = quoted.end()
    comment = _COMMENT.search(line, value)
    return comment.group() if comment else None
