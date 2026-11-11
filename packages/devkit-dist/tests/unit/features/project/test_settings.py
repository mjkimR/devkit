"""The ``[playbooks]`` value check every reader shares (shared configuration, local overlay, search options)."""

from __future__ import annotations

import math

import pytest
from devkit_dist.features.project.models.settings import PLAYBOOK_KEYS, PLAYBOOK_MODES, playbook_value
from devkit_dist.features.search import SearchMode


def test_the_modes_are_the_search_modes_in_their_order() -> None:
    assert tuple(mode.value for mode in SearchMode) == PLAYBOOK_MODES


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("limit", 1, 1),
        ("limit", 20, 20),
        ("max_bytes", 1024, 1024),
        ("max_bytes", 65536, 65536),
        ("min_score", 0, 0.0),
        ("min_score", 2.5, 2.5),
        ("min_similarity", 1, 1.0),
        ("min_similarity", 0.35, 0.35),
        ("mode", "HYBRID", "hybrid"),
        ("mode", "auto", "auto"),
    ],
)
def test_a_value_within_bounds_is_returned_as_the_search_uses_it(key: str, value: object, expected: object) -> None:
    result = playbook_value(key, value)
    assert result == expected and type(result) is type(expected)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("limit", 0),
        ("limit", 21),
        ("limit", 5.0),
        ("max_bytes", 1023),
        ("max_bytes", 65537),
        ("min_score", -0.1),
        ("min_score", math.inf),
        ("min_score", math.nan),
        ("min_score", "1"),
        ("min_similarity", 1.5),
        ("min_similarity", math.nan),
        ("mode", "semantic"),
        ("mode", 1),
        ("unknown", 1),
    ],
)
def test_a_value_out_of_bounds_is_none(key: str, value: object) -> None:
    assert playbook_value(key, value) is None


@pytest.mark.parametrize("key", sorted(PLAYBOOK_KEYS - {"mode"}))
def test_a_boolean_is_never_a_number(key: str) -> None:
    assert playbook_value(key, True) is None
    assert playbook_value(key, False) is None
