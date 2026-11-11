"""``devkit_dist.features.search.services.lexical``: the Unicode tokenizer and BM25."""

from __future__ import annotations

import math

from devkit_dist.features.search import Bm25, tokenize


def test_tokenize_casefolds_drops_accents_and_splits_on_non_word_characters() -> None:
    assert tokenize("RULE-file_length: Café über 2x") == ["rule", "file", "length", "cafe", "uber", "2x"]
    assert tokenize("Straße") == ["strasse"]
    assert tokenize("") == [] and tokenize("--- __ !!") == []


def test_tokenize_keeps_other_scripts_composed() -> None:
    # The decomposition for accent stripping splits Hangul into jamo; composing again restores the syllables.
    assert tokenize("한국어 문서 검색, specrig") == ["한국어", "문서", "검색", "specrig"]
    assert tokenize("検索エンジン") == ["検索エンジン"]


def test_bm25_length_normalization_and_term_frequency() -> None:
    short, verbose = Bm25(["recovery replica", "recovery replica " + "other " * 50]).scores("recovery")
    assert short > verbose > 0
    scores = Bm25(["replica replica", "replica other", "unrelated words"]).scores("replica")
    assert scores[0] > scores[1] > scores[2] == 0
    assert Bm25(["replica"]).scores("replica replica") == Bm25(["replica"]).scores("replica")
    assert Bm25([]).scores("replica") == []
    assert Bm25([""]).scores("replica") == [0]
    assert all(math.isfinite(score) for score in scores)


def test_an_index_scores_every_query_like_a_fresh_index() -> None:
    documents = ["restore a replica", "publish a release", "replica lag alerts"]
    index = Bm25(documents)
    for query in ("replica", "release replica", "nothing"):
        assert index.scores(query) == Bm25(documents).scores(query)
