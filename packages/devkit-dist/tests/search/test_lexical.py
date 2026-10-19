"""``devkit.search.lexical``: the Unicode tokenizer and BM25."""

from __future__ import annotations

import math

from devkit.search import Bm25, bm25_scores, tokenize


def test_tokenize_casefolds_drops_accents_and_splits_on_non_word_characters() -> None:
    assert tokenize("RULE-file_length: Café über 2x") == ["rule", "file", "length", "cafe", "uber", "2x"]
    assert tokenize("Straße") == ["strasse"]
    assert tokenize("") == [] and tokenize("--- __ !!") == []


def test_tokenize_keeps_other_scripts_composed() -> None:
    # The decomposition for accent stripping splits Hangul into jamo; composing again restores the syllables.
    assert tokenize("한국어 문서 검색, specrig") == ["한국어", "문서", "검색", "specrig"]
    assert tokenize("検索エンジン") == ["検索エンジン"]


def test_bm25_length_normalization_and_term_frequency() -> None:
    short, verbose = bm25_scores(["recovery replica", "recovery replica " + "other " * 50], "recovery")
    assert short > verbose > 0
    scores = bm25_scores(["replica replica", "replica other", "unrelated words"], "replica")
    assert scores[0] > scores[1] > scores[2] == 0
    assert bm25_scores(["replica"], "replica replica") == bm25_scores(["replica"], "replica")
    assert bm25_scores([], "replica") == []
    assert bm25_scores([""], "replica") == [0]
    assert all(math.isfinite(score) for score in scores)


def test_an_index_scores_like_the_one_shot_function_for_every_query() -> None:
    documents = ["restore a replica", "publish a release", "replica lag alerts"]
    index = Bm25(documents)
    for query in ("replica", "release replica", "nothing"):
        assert index.scores(query) == bm25_scores(documents, query)
