"""Strict JSON parsing shared by every devkit-owned JSON reader: a duplicate object key is an error, never a silent
last-one-wins, and ``NaN``/``Infinity``/``-Infinity`` are optionally rejected.

Each caller wraps these ``ValueError`` subclasses in its own advisory, so the wording a user sees stays the caller's.
"""

from __future__ import annotations

import json
from typing import Any


class StrictJSONError(ValueError):
    """Content ``json`` accepts that strict parsing refuses."""


class DuplicateKeyError(StrictJSONError):
    """An object repeats a key; ``key`` names it."""

    def __init__(self, key: str) -> None:
        super().__init__(f"duplicate JSON key {key!r}")
        self.key = key


class NonFiniteConstantError(StrictJSONError):
    """``NaN``, ``Infinity`` or ``-Infinity``; ``name`` is the constant as written."""

    def __init__(self, name: str) -> None:
        super().__init__(f"{name} is not valid JSON")
        self.name = name


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


def _reject(name: str) -> Any:
    raise NonFiniteConstantError(name)


def strict_json_loads(raw: str | bytes, *, reject_constants: bool) -> Any:
    """``json.loads`` of ``raw`` that raises ``DuplicateKeyError`` for a repeated object key and, with
    ``reject_constants``, ``NonFiniteConstantError`` for ``NaN``/``Infinity``/``-Infinity``.

    Otherwise it raises what ``json.loads`` raises (``json.JSONDecodeError``, ``UnicodeDecodeError`` for bytes,
    ``RecursionError``); the value need not be an object, so each caller checks the shape it requires.
    """
    if reject_constants:
        return json.loads(raw, object_pairs_hook=_unique, parse_constant=_reject)
    return json.loads(raw, object_pairs_hook=_unique)
