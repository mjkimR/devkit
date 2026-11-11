"""Pure readers for partial replacement statements and their reciprocal pointers."""

from __future__ import annotations

import re
from dataclasses import dataclass

from devkit_agt.features.rules.models.markdown import LineKind, scan

from devkit_docs.features.documents.models.ids import ID_SOURCE
from devkit_docs.features.documents.models.markdown import body_start, visible_lines

_START = re.compile(
    rf"^\s*(?:[-+*]\s+|\d+[.)]\s+)?Supersede(?P<pointer>d in part by|s in part) `(?P<id>{ID_SOURCE})`(?P<colon>:)?"
)
_BOUNDARY = re.compile(r"^\s*(?:#{1,6}\s|[-+*]\s|\d+[.)]\s)")


@dataclass(frozen=True)
class ReplacementText:
    """A visible replacement start and its original source text after the colon."""

    id: str
    line: int
    text: str
    pointer: bool


def replacement_texts(source: str) -> list[ReplacementText]:
    """Read starts from masked prose and payloads from source, bounded by paragraph/item/heading ends."""
    # Lines split on "\n" only, as the scanner does, so raw and visible line numbers agree.
    raw = [line.removesuffix("\r") for line in source.split("\n")]
    start, first_line = body_start(source)
    visible = {line.number: line.text for line in visible_lines(source, start=start, first_line=first_line)}
    comments = {
        line.number for line in scan(source, start=start, first_line=first_line) if line.kind is LineKind.COMMENT
    }
    result = []
    for number, line in visible.items():
        match = _START.match(line)
        if match is None:
            continue
        # A statement needs the colon; legacy pointers without one still name their successor.
        pointer = match.group("pointer").startswith("d")
        if not pointer and match.group("colon") is None:
            continue
        parts = [raw[number - 1][match.end() :].strip()] if match.group("colon") else []
        for following in range(number + 1, len(raw) + 1):
            text = raw[following - 1]
            # A line wholly inside an HTML comment ends the statement: it is not part of its visible text.
            if (
                not text.strip()
                or following not in visible
                or following in comments
                or _BOUNDARY.match(visible[following])
            ):
                break
            parts.append(text.strip())
        result.append(ReplacementText(match.group("id"), number, "\n".join(parts).strip(), pointer))
    return result


def supersedes_ids(value: object) -> list[str]:
    """Read the string entries of a supersedes field; schema validation belongs to the rule."""
    if isinstance(value, str):
        return [value.strip()]
    return [item.strip() for item in value if isinstance(item, str)] if isinstance(value, list) else []


def same_text(left: str, right: str) -> bool:
    """Compare source text, preserving inline markup, after collapsing whitespace."""
    return left.split() == right.split()
