"""Reciprocal Rank Fusion of several rankings."""

from __future__ import annotations

from collections.abc import Sequence

RRF_K = 60


def reciprocal_rank_fusion(rankings: Sequence[Sequence[str]], *, k: int = RRF_K) -> dict[str, float]:
    """``sum(1 / (k + rank))`` over the rankings that contain each id; ranks start at 1.

    Each ranking lists ids best first; an id missing from a ranking contributes nothing for it.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1 / (k + rank)
    return scores
