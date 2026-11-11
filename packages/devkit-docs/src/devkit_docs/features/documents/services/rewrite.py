"""Rewrite references in place: only parsed references change, never other occurrences of an ID."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping

import yaml

from devkit_docs.features.documents.models.model import BODY, Reference


def rewrite(text: str, references: Iterable[Reference], mapping: Mapping[str, str]) -> str:
    """``text`` with each reference whose target ``mapping`` names replaced by the mapped ID.

    A quoted frontmatter value keeps its quote style. A ``[ID]`` body reference becomes `` `ID` `` (mapping an ID to
    itself converts the notation only). The references must have been read from ``text``.
    """
    rewritten: set[tuple[int, int]] = set()
    for ref in sorted(references, key=lambda ref: ref.start, reverse=True):
        replacement = mapping.get(ref.target)
        if replacement is None or not 0 <= ref.start < ref.end <= len(text):
            continue
        start, end = ref.start, ref.end
        if (start, end) in rewritten:
            continue  # YAML aliases share their anchor node's source span.
        rewritten.add((start, end))
        if ref.field != BODY:
            original = text[start:end]
            # A scalar node span includes anchor/tag syntax; only replace the value token.
            scalar = next((token for token in yaml.scan(original) if isinstance(token, yaml.ScalarToken)), None)
            if scalar is None or scalar.value != ref.target:
                continue
            start, end = start + scalar.start_mark.index, start + scalar.end_mark.index
            original = text[start:end]
            if original.startswith('"'):
                replacement = json.dumps(replacement, ensure_ascii=False)
            elif original.startswith("'"):
                replacement = f"'{replacement}'"
        elif ref.bracket and text[start - 1 : start] == "[" and text[end : end + 1] == "]":
            start, end, replacement = start - 1, end + 1, f"`{replacement}`"
        text = text[:start] + replacement + text[end:]
    return text
