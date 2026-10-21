"""Shared text character classification."""

import unicodedata


def foreign_letters(text: str) -> list[str]:
    """The distinct letters of ``text`` outside the Latin script, in order of appearance."""
    found: list[str] = []
    for char in text:
        if char.isalpha() and "LATIN" not in unicodedata.name(char, "") and char not in found:
            found.append(char)
    return found
