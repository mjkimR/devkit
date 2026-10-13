"""Lexical ranking: a Unicode word tokenizer and BM25, standard library only."""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from collections.abc import Sequence

_WORD = re.compile(r"[^\W_]+")
_DIACRITICS = re.compile("[\u0300-\u036f]")
K1 = 1.5
B = 0.75


def tokenize(text: str) -> list[str]:
    """Casefolded words of letters and digits; Latin, Greek and Cyrillic accents are dropped, any script is kept.

    ``_`` and every other non-word character separate words, so ``RULE-file_length``
    gives ``rule``, ``file`` and ``length``. After a compatibility decomposition
    only the combining diacritical marks (U+0300 to U+036F) are removed, so
    ``Café`` gives ``cafe``, and the rest is composed again: Hangul syllables and
    marks such as the Japanese voicing mark survive.
    """
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return _WORD.findall(unicodedata.normalize("NFC", _DIACRITICS.sub("", decomposed)))


class Bm25:
    """BM25 over fixed documents (positive IDF, ``k1=1.5``, ``b=0.75``); a query counts each term once."""

    def __init__(self, documents: Sequence[str]) -> None:
        self._frequencies = [Counter(tokenize(document)) for document in documents]
        self._lengths = [sum(frequency.values()) for frequency in self._frequencies]
        self._average = sum(self._lengths) / len(self._lengths) if self._lengths else 0.0

    def scores(self, query: str) -> list[float]:
        """The score of every document, in document order; ``0`` where no query term occurs."""
        if not self._average:
            return [0.0] * len(self._frequencies)
        count = len(self._frequencies)
        idf = {
            term: math.log1p((count - found + 0.5) / (found + 0.5))
            for term in sorted(set(tokenize(query)))
            for found in [sum(term in frequency for frequency in self._frequencies)]
        }
        return [
            sum(
                weight * frequency[term] * (K1 + 1) / (frequency[term] + K1 * (1 - B + B * length / self._average))
                for term, weight in idf.items()
                if frequency[term]
            )
            for frequency, length in zip(self._frequencies, self._lengths, strict=True)
        ]


def bm25_scores(documents: Sequence[str], query: str) -> list[float]:
    """BM25 of every document against ``query``, in document order."""
    return Bm25(documents).scores(query)
