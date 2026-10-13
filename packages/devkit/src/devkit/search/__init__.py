"""devkit.search: lexical, dense and hybrid document search, SDD-agnostic.

Lexical search (BM25) uses the standard library only. Dense and hybrid search
embed document metadata with a static embedding model and need the
``devkit[search]`` extra (numpy, tokenizers and the ``potion-base-8m`` model
package); those imports happen on the first dense search, never on import.
Semantics: ``docs/search/overview.md``.
"""

from devkit.search.dense import DEFAULT_MODEL, MODEL_GROUP, Embedder, load_embedder
from devkit.search.errors import ModelInvalidError, ModelNotFoundError, SearchError, SearchExtraMissingError
from devkit.search.fusion import reciprocal_rank_fusion
from devkit.search.index import SearchDocument, SearchHit, SearchIndex, SearchMode
from devkit.search.lexical import Bm25, bm25_scores, tokenize

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
