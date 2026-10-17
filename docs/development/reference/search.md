# devkit.search

Lexical, dense and hybrid search over a caller's documents. Semantics, measurements and the model package: `CAP-SRCH-document-search`. There is no CLI of its own; `devkit playbook search` ranks with it.

## Install

Lexical search is part of `devkit`, and the default `auto` mode uses it when nothing more is installed. Dense and hybrid search need the extra, which adds `numpy`, `tokenizers` and the `devkit-embed` model package (15 MB):

```bash
uv add 'devkit-agt[search] @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'
```

From Git or in this repository, the extra installs the model wheel from the release that `packages/devkit/pyproject.toml` pins; from a release wheel, add `devkit-embed` by its URL ([README](../../../README.md#using-devkit-in-another-project)).

## Library

```python
from devkit.search import SearchDocument, SearchIndex, SearchMode

index = SearchIndex([
    SearchDocument("restore-replica", "Restore a PostgreSQL replica after failure", body="..."),
    SearchDocument("publish-release", "Publish a software release"),
])
index.resolve_mode(SearchMode.AUTO)  # SearchMode.HYBRID with devkit-agt[search], else SearchMode.LEXICAL
index.search("standby database is broken", limit=5, min_similarity=0.35)
# [SearchHit(id="restore-replica", score=0.0328), ...]; hit.to_dict() == {"id": ..., "score": ...}
```

| Name | Purpose |
| --- | --- |
| `SearchDocument(id, metadata, body="")` | `metadata` is ranked lexically and densely, `body` only lexically. |
| `SearchIndex(documents, *, embedder=None, model="potion-base-8m")` | Ids must be unique (`ValueError`). The model loads, and the documents are embedded, on the first dense or hybrid search; pass `embedder` to share a loaded model. |
| `SearchIndex.search(query, *, mode=SearchMode.AUTO, limit=None, min_score=0.0, min_similarity=0.0)` | Hits best first, ties by id; `min_score` bounds the BM25 ranking, `min_similarity` the cosine ranking, each before a hybrid fusion. |
| `SearchIndex.resolve_mode(mode)` | The mode a search runs in: `AUTO` resolves to `HYBRID` when the model loads, else `LEXICAL`; other modes are returned unchanged. |
| `SearchMode` | `AUTO`, `LEXICAL`, `DENSE`, `HYBRID`. |
| `load_embedder(name="potion-base-8m")`, `Embedder.from_directory(path)` | Load a model package; `Embedder.encode(texts)` returns unit-length `float32` rows. |
| `tokenize`, `Bm25`, `bm25_scores`, `reciprocal_rank_fusion` | The ranking primitives. |
| `DEFAULT_MODEL`, `MODEL_GROUP` | `"potion-base-8m"`, `"devkit.embedding_models"`. |

## Error codes

Only dense and hybrid search raise them; `auto` resolves to lexical instead of raising the first two.

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `SEARCH_EXTRA_MISSING` | `ERROR` (`INTERACTION`) | `SearchExtraMissingError` | `numpy` or `tokenizers` cannot be imported; `[FIX]` installs `devkit-agt[search]`. |
| `SEARCH_MODEL_NOT_FOUND` | `ERROR` (`INTERACTION`) | `ModelNotFoundError` | No installed package registers the requested model name. |
| `SEARCH_MODEL_INVALID` | `ERROR` (`MAINTENANCE`) | `ModelInvalidError` | The model package's files are missing or malformed, it cannot be imported, or two packages register the same name. |
