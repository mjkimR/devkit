"""The English summary check shared by ``RULE-document-summary`` and ``RULE-steering-documents``.

A summary is listed or embedded where agents search, so it must be a non-empty English string (no letter outside the
Latin script) of at most a rule's length limit. Each rule words its own findings.
"""

from __future__ import annotations

from dataclasses import dataclass

from devkit_docs.utils.text import foreign_letters


@dataclass(frozen=True, slots=True)
class SummaryProblem:
    """What is wrong with a summary value, one of: ``blank`` (not a string, or only whitespace), ``foreign`` (up to
    five letters outside the Latin script, in order of appearance) or ``length`` (its stripped length, over the
    limit)."""

    blank: bool = False
    foreign: str = ""
    length: int = 0


def summary_problem(value: object, limit: int) -> SummaryProblem | None:
    """The first problem of the summary ``value`` against ``limit`` characters, else ``None``."""
    if not isinstance(value, str) or not value.strip():
        return SummaryProblem(blank=True)
    letters = foreign_letters(value)
    if letters:
        return SummaryProblem(foreign="".join(letters[:5]))
    if len(value.strip()) > limit:
        return SummaryProblem(length=len(value.strip()))
    return None
