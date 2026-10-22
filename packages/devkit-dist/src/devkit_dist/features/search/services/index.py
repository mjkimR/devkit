"""``SearchIndex``: lexical, dense or hybrid ranking over a fixed set of documents.

A document has ``metadata`` (a title and description: the text written for
finding it, in English) and an optional ``body``. Lexical ranking (BM25) reads
both; dense ranking embeds only the metadata, because the embedding model is
English-only and a body may be in any language. Hybrid ranking fuses the two
rankings with Reciprocal Rank Fusion. ``auto`` (the default) is hybrid when the
dense dependencies are installed and lexical otherwise. Filtering (scopes,
namespaces, exact id matches) is the caller's: it indexes the documents it wants
ranked.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from devkit_dist.features.search.models.contracts import SearchDocument, SearchHit, SearchMode
from devkit_dist.features.search.models.errors import ModelNotFoundError, SearchExtraMissingError
from devkit_dist.features.search.services.dense import DEFAULT_MODEL, Embedder, load_embedder
from devkit_dist.features.search.services.fusion import reciprocal_rank_fusion
from devkit_dist.features.search.services.lexical import Bm25

if TYPE_CHECKING:
    import numpy as np


class SearchIndex:
    """Ranks ``documents`` against queries; ids must be unique.

    The embedding model is loaded, and the documents embedded, on the first dense,
    hybrid or ``auto`` search, so a lexical search never imports numpy. Pass
    ``embedder`` to share one loaded model between indexes.
    """

    def __init__(
        self,
        documents: Iterable[SearchDocument],
        *,
        embedder: Embedder | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.documents = tuple(documents)
        ids = [document.id for document in self.documents]
        if len(set(ids)) != len(ids):
            raise ValueError("SearchIndex: document ids must be unique")
        self._bm25 = Bm25([f"{document.metadata}\n{document.body}" for document in self.documents])
        self._embedder = embedder
        self._model = model
        self._vectors: np.ndarray | None = None
        self._dense_available: bool | None = None

    @property
    def embedder(self) -> Embedder:
        """The embedding model, loaded from its package on first use."""
        if self._embedder is None:
            self._embedder = load_embedder(self._model)
        return self._embedder

    def resolve_mode(self, mode: SearchMode) -> SearchMode:
        """The mode a search runs in: ``mode`` itself, or for ``AUTO`` hybrid when the model loads, else lexical.

        ``AUTO`` falls back to lexical only when the dense dependencies are not
        installed (``SEARCH_EXTRA_MISSING``, ``SEARCH_MODEL_NOT_FOUND``); a
        broken model package still raises ``SEARCH_MODEL_INVALID``.
        """
        if mode is not SearchMode.AUTO:
            return mode
        if self._dense_available is None:
            try:
                self.embedder  # noqa: B018 - loads the model
                self._dense_available = True
            except (SearchExtraMissingError, ModelNotFoundError):
                self._dense_available = False
        return SearchMode.HYBRID if self._dense_available else SearchMode.LEXICAL

    def search(
        self,
        query: str,
        *,
        mode: SearchMode = SearchMode.AUTO,
        limit: int | None = None,
        min_score: float = 0.0,
        min_similarity: float = 0.0,
    ) -> list[SearchHit]:
        """Matching documents, best first (ties by id); at most ``limit`` when given.

        The lexical ranking keeps documents whose BM25 score is positive and at
        least ``min_score``; the dense ranking those whose cosine similarity is
        positive and at least ``min_similarity``. A hybrid hit is in at least one
        of the two and scores its fused value.
        """
        mode = self.resolve_mode(mode)
        if mode is SearchMode.LEXICAL:
            hits = self._lexical(query, min_score)
        elif mode is SearchMode.DENSE:
            hits = self._dense(query, min_similarity)
        else:
            fused = reciprocal_rank_fusion(
                [
                    [hit.id for hit in self._lexical(query, min_score)],
                    [hit.id for hit in self._dense(query, min_similarity)],
                ]
            )
            hits = _ranked(fused.items(), 0.0)
        return hits if limit is None else hits[:limit]

    def _lexical(self, query: str, floor: float) -> list[SearchHit]:
        scores = self._bm25.scores(query)
        return _ranked(((document.id, score) for document, score in zip(self.documents, scores, strict=True)), floor)

    def _dense(self, query: str, floor: float) -> list[SearchHit]:
        if self._vectors is None:
            self._vectors = self.embedder.encode([document.metadata for document in self.documents])
        similarities = self._vectors @ self.embedder.encode([query])[0]
        return _ranked(
            (
                (document.id, float(similarity))
                for document, similarity in zip(self.documents, similarities.tolist(), strict=True)
            ),
            floor,
        )


def _ranked(scores: Iterable[tuple[str, float]], floor: float) -> list[SearchHit]:
    hits = [SearchHit(id, score) for id, score in scores if score > 0 and score >= floor]
    hits.sort(key=lambda hit: (-hit.score, hit.id))
    return hits
