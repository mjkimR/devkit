"""``devkit_dist.features.search.SearchIndex``: lexical, dense and hybrid ranking over documents."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from devkit_dist.features.search import (
    Embedder,
    ModelInvalidError,
    ModelNotFoundError,
    SearchDocument,
    SearchHit,
    SearchIndex,
    SearchMode,
)
from distsupport.search import write_model

VECTORS = {"replica": [1.0, 0.0], "standby": [0.9, 0.1], "release": [0.0, 1.0], "publish": [0.1, 0.9]}
DOCUMENTS = [
    SearchDocument("restore-replica", "replica", body="steps for a failed standby"),
    SearchDocument("publish-release", "publish release"),
    SearchDocument("standby-notes", "standby", body="release"),
]


@pytest.fixture
def embedder(tmp_path: Path) -> Embedder:
    return Embedder.from_directory(write_model(tmp_path / "model", VECTORS))


def test_lexical_ranks_metadata_and_body_without_a_model() -> None:
    index = SearchIndex(DOCUMENTS, model="no-such-model")  # never loaded: lexical needs no model
    assert [hit.id for hit in index.search("standby", mode=SearchMode.LEXICAL)] == ["standby-notes", "restore-replica"]
    assert [hit.id for hit in index.search("release", mode=SearchMode.LEXICAL)] == ["publish-release", "standby-notes"]
    assert index.search("nothing matches", mode=SearchMode.LEXICAL) == []
    with pytest.raises(ModelNotFoundError):
        index.search("standby", mode=SearchMode.DENSE)


def test_dense_embeds_only_the_metadata(embedder: Embedder) -> None:
    hits = SearchIndex(DOCUMENTS, embedder=embedder).search("release", mode=SearchMode.DENSE)
    # standby-notes has "release" only in its body: its metadata scores low, and replica's not at all.
    assert [hit.id for hit in hits] == ["publish-release", "standby-notes"]
    assert hits[0].score == pytest.approx(1.0, abs=0.02) and all(hit.score > 0 for hit in hits)


def test_dense_drops_documents_without_positive_similarity(tmp_path: Path) -> None:
    embedder = Embedder.from_directory(write_model(tmp_path / "model", {"up": [1.0, 0.0], "down": [-1.0, 0.0]}))
    index = SearchIndex(
        [SearchDocument("a", "up"), SearchDocument("b", "down"), SearchDocument("c", "")], embedder=embedder
    )
    assert [hit.id for hit in index.search("up", mode=SearchMode.DENSE)] == ["a"]
    assert index.search("", mode=SearchMode.DENSE) == []


def test_hybrid_fuses_both_rankings(embedder: Embedder) -> None:
    index = SearchIndex(DOCUMENTS, embedder=embedder)
    hits = index.search("standby", mode=SearchMode.HYBRID)
    # Lexical: standby-notes, restore-replica. Dense: standby-notes, restore-replica, publish-release.
    assert [hit.id for hit in hits] == ["standby-notes", "restore-replica", "publish-release"]
    assert hits[0].score == pytest.approx(2 / 61) and hits[2].score == pytest.approx(1 / 63)


def test_limit_ties_and_results(embedder: Embedder) -> None:
    index = SearchIndex([SearchDocument("b", "replica"), SearchDocument("a", "replica")], embedder=embedder)
    assert [hit.id for hit in index.search("replica", mode=SearchMode.LEXICAL)] == ["a", "b"]  # ties rank by id
    assert [hit.id for hit in index.search("replica", mode=SearchMode.HYBRID, limit=1)] == ["a"]
    assert index.search("replica", limit=0) == []
    assert SearchHit("a", 0.5).to_dict() == {"id": "a", "score": 0.5}


def test_document_ids_must_be_unique() -> None:
    with pytest.raises(ValueError, match="unique"):
        SearchIndex([SearchDocument("a", "x"), SearchDocument("a", "y")])


def test_the_model_loads_once_and_embeds_the_documents_once(
    embedder: Embedder, monkeypatch: pytest.MonkeyPatch
) -> None:
    loads: list[str] = []
    monkeypatch.setattr(
        "devkit_dist.features.search.services.index.load_embedder", lambda name: loads.append(name) or embedder
    )
    calls: list[int] = []
    encode = embedder.encode
    monkeypatch.setattr(embedder, "encode", lambda texts: calls.append(len(texts)) or encode(texts))
    index = SearchIndex(DOCUMENTS, model="tiny")
    index.search("replica", mode=SearchMode.DENSE)
    index.search("release", mode=SearchMode.HYBRID)
    assert loads == ["tiny"] and calls == [3, 1, 1]


def test_auto_is_hybrid_with_a_model_and_lexical_without_one(
    embedder: Embedder, monkeypatch: pytest.MonkeyPatch
) -> None:
    with_model = SearchIndex(DOCUMENTS, embedder=embedder)
    assert with_model.resolve_mode(SearchMode.AUTO) is SearchMode.HYBRID
    assert with_model.search("standby") == with_model.search("standby", mode=SearchMode.HYBRID)
    without = SearchIndex(DOCUMENTS, model="no-such-model")
    assert without.resolve_mode(SearchMode.AUTO) is SearchMode.LEXICAL
    assert without.search("standby") == without.search("standby", mode=SearchMode.LEXICAL)
    assert without.resolve_mode(SearchMode.DENSE) is SearchMode.DENSE  # explicit modes are never changed
    monkeypatch.setitem(sys.modules, "numpy", None)
    assert SearchIndex(DOCUMENTS).resolve_mode(SearchMode.AUTO) is SearchMode.LEXICAL


def test_auto_still_reports_a_broken_model(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(name: str) -> Embedder:
        raise ModelInvalidError("embedding model: model.safetensors is truncated")

    monkeypatch.setattr("devkit_dist.features.search.services.index.load_embedder", broken)
    with pytest.raises(ModelInvalidError):
        SearchIndex(DOCUMENTS).search("standby")


def test_floors_apply_to_each_ranking_before_fusion(embedder: Embedder) -> None:
    index = SearchIndex(DOCUMENTS, embedder=embedder)
    scores = {hit.id: hit.score for hit in index.search("standby", mode=SearchMode.LEXICAL)}
    floor = max(scores.values())
    assert [hit.id for hit in index.search("standby", mode=SearchMode.LEXICAL, min_score=floor)] == ["standby-notes"]
    dense = index.search("release", mode=SearchMode.DENSE, min_similarity=0.5)
    assert [hit.id for hit in dense] == ["publish-release"]
    hybrid = index.search("standby", mode=SearchMode.HYBRID, min_score=floor, min_similarity=1.0)
    assert [hit.id for hit in hybrid] == ["standby-notes"]
