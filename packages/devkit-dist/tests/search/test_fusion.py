"""``devkit.search.fusion``: Reciprocal Rank Fusion."""

from __future__ import annotations

import pytest
from devkit.search import reciprocal_rank_fusion


def test_fusion_sums_reciprocal_ranks_and_skips_absent_ids() -> None:
    scores = reciprocal_rank_fusion([["a", "b"], ["b", "c"]], k=60)
    assert scores == {"a": pytest.approx(1 / 61), "b": pytest.approx(1 / 62 + 1 / 61), "c": pytest.approx(1 / 62)}
    assert reciprocal_rank_fusion([]) == {} and reciprocal_rank_fusion([[], []]) == {}


def test_an_id_in_both_rankings_beats_one_ranked_first_in_only_one() -> None:
    scores = reciprocal_rank_fusion([["only", "both"], ["both"]])
    assert scores["both"] > scores["only"]
