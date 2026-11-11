"""The document ID grammar: ``<PREFIX>-<slug>``, the prefix naming the document kind.

An ID starts with one of the prefixes below, a dash, then a letter or digit
followed by letters, digits, ``_`` and ``-``. Path and naming conventions per
kind (``CAP-<AREA>-<slug>`` under ``docs/capabilities/<area>/``, dated
partitions for decisions and specs) are checked by the rules, not here: the
index accepts any well-formed ID wherever it is declared. ``Kind`` and the facts of each
kind live in ``kinds``.
"""

from __future__ import annotations

import re

from devkit_docs.features.documents.models.kinds import Kind, definitions

__all__ = [
    "ID_PATTERN",
    "ID_SOURCE",
    "PREFIXES",
    "Kind",
    "is_id",
    "is_legacy_id",
    "is_word_led_slug",
    "kind_of",
    "legacy_references",
    "word_led",
]

# Built from the kind table at import (``ADR-kind-definition-table-keyed-on-the-declared-kind-enum``), in its order.
PREFIXES: dict[str, Kind] = {row.prefix: row.kind for row in definitions()}

ID_SOURCE = rf"(?:{'|'.join(PREFIXES)})-[A-Za-z0-9][A-Za-z0-9_-]*"
ID_PATTERN = re.compile(rf"^{ID_SOURCE}$")

# Date- or number-based references that are never valid identifiers (``RULE-id-convention`` reports them, and an
# alias of that form is refused, so the two never disagree).
_LEGACY_REF = re.compile(
    r"\b(SPEC-\d{8}(?:-[a-z0-9-]+)?|FB-\d{8}(?:-[a-z0-9-]+)?|P?ADR-\d{4}|UC-\d{3,}|CAP-[A-Z0-9]+-\d{3,})\b", re.ASCII
)
# The arc42 chapter number is part of an architecture slug: ARCH-03-context is valid, a bare ARCH-03 is not.
_ARCH_REF = re.compile(r"\bARCH-\d{2}(?:-[0-9a-z]+)*", re.ASCII)
_ARCH_SUBDOCUMENT = re.compile(r"^-[1-9](?=-|$)")
_HAS_LETTER = re.compile(r"[a-z]")
_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*", re.ASCII)


def word_led(slug: str) -> bool:
    """Whether the first ``-`` segment of ``slug`` has a letter: ``001-foo`` is a retired sequence number, and
    ``2024-budget`` reads as the number-based ``2024``."""
    return _HAS_LETTER.search(slug.split("-", 1)[0]) is not None


def is_word_led_slug(value: str) -> bool:
    """Whether ``value`` is a kebab-case slug (``[a-z0-9]`` words joined by ``-``) whose first segment has a letter."""
    return _SLUG.fullmatch(value) is not None and word_led(value)


def is_id(value: str) -> bool:
    """Whether ``value`` is a well-formed document ID."""
    return ID_PATTERN.match(value) is not None


def kind_of(document_id: str) -> Kind | None:
    """The kind named by the prefix of a well-formed ID, else ``None``."""
    if not is_id(document_id):
        return None
    return PREFIXES[document_id.split("-", 1)[0]]


def legacy_references(text: str) -> list[re.Match[str]]:
    """The date- or number-based identifier references in ``text`` (one line), in order."""
    found = list(_LEGACY_REF.finditer(text))
    for match in _ARCH_REF.finditer(text):
        rest = match.group(0)[len("ARCH-") + 2 :]
        rest = _ARCH_SUBDOCUMENT.sub("", rest, count=1)
        if not _HAS_LETTER.search(rest):
            found.append(match)
    return sorted(found, key=lambda match: match.start())


def is_legacy_id(value: str) -> bool:
    """Whether ``value`` contains a date- or number-based identifier form ``RULE-id-convention`` reports."""
    return bool(legacy_references(value))
