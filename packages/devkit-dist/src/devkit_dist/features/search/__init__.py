"""devkit_dist.features.search: lexical, dense and hybrid document search, SDD-agnostic.

Lexical search (BM25) uses the standard library only. Dense and hybrid search
embed document metadata with a static embedding model and need the
``search`` extra (``devkit-dist[search]``, or ``devkit-agt[search]`` where
devkit-agt is installed: numpy, tokenizers and the ``potion-base-8m`` model
package); those imports happen on the first dense search, never on import.
Semantics: ``docs/capabilities/search/CAP-SRCH-document-search.md``.
"""

from devkit_dist.features.search.models.contracts import SearchDocument, SearchHit, SearchMode
from devkit_dist.features.search.models.errors import (
    ModelInvalidError,
    ModelNotFoundError,
    SearchError,
    SearchExtraMissingError,
)
from devkit_dist.features.search.services.dense import DEFAULT_MODEL, MODEL_GROUP, Embedder, load_embedder
from devkit_dist.features.search.services.fusion import reciprocal_rank_fusion
from devkit_dist.features.search.services.index import SearchIndex
from devkit_dist.features.search.services.lexical import Bm25, bm25_scores, tokenize

__all__ = [
    "DEFAULT_MODEL",
    "MODEL_GROUP",
    "Bm25",
    "Embedder",
    "ModelInvalidError",
    "ModelNotFoundError",
    "SearchDocument",
    "SearchError",
    "SearchExtraMissingError",
    "SearchHit",
    "SearchIndex",
    "SearchMode",
    "bm25_scores",
    "load_embedder",
    "reciprocal_rank_fusion",
    "tokenize",
]
