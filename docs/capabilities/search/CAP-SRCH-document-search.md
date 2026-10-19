---
id: CAP-SRCH-document-search
title: "Document Search"
summary: "Lexical BM25, dense embedding, and hybrid retrieval ranking over project documents."
area: search
status: active
created_at: 2026-10-17
---

# [CAP-SRCH-document-search] Document Search: Overview

`devkit.search` ranks a caller's documents against a query: lexically (BM25), densely (embedding similarity) or both (hybrid). It is SDD-agnostic: it knows documents only as an id, metadata text and an optional body. Choosing which documents to rank (scopes, namespaces) and pinning exact id matches are the caller's job. Quick reference: [reference.md](../../development/reference/search.md).

## 1. Document Model

| Field | Read by | Purpose |
| --- | --- | --- |
| `id` | (result) | Unique within an index; ties rank by id. |
| `metadata` | lexical and dense | The text written for finding the document: title, description, aliases, usually from frontmatter. Write it in English. |
| `body` | lexical only | Optional; any language. |

The embedding model is English-only, so dense ranking reads only `metadata`. A repository whose documents are in another language stays searchable by giving each document English frontmatter metadata; its body still contributes to BM25.

## 2. Modes

| Mode | Ranking | Needs |
| --- | --- | --- |
| `auto` (default) | `hybrid` when the dense dependencies are installed, else `lexical` | Nothing |
| `lexical` | BM25 over `metadata` and `body` | Standard library only |
| `dense` | Cosine similarity of the query vector and each document's `metadata` vector | the `search` extra |
| `hybrid` | Reciprocal Rank Fusion (`k = 60`) of the lexical and the dense ranking | the `search` extra |

The lexical ranking keeps documents whose BM25 score is positive and at least `min_score`, the dense ranking those whose cosine similarity is positive and at least `min_similarity` (both `0` by default); a hybrid hit appears in at least one of the two, and its score is the fused value, `sum(1 / (60 + rank))`. Results are ordered by score, then id. A static model gives most unrelated texts a positive similarity, so a caller that shows hybrid results should set `min_similarity`; `devkit playbook search` uses `0.35`, which on the corpus below kept the hybrid gain while dropping the long tail.

`auto` lets callers search without caring what is installed: `SearchIndex.resolve_mode` loads the model on the first `auto` search and resolves to `hybrid`, or to `lexical` when numpy, tokenizers or the model package is not installed (`SEARCH_EXTRA_MISSING`, `SEARCH_MODEL_NOT_FOUND`). Only `auto` falls back: an explicit `dense` or `hybrid` without the extra raises, and a broken model package raises `SEARCH_MODEL_INVALID` in every mode. A caller reports the resolved mode with its results, so the kind of ranking is never hidden.

Dense ranking does not replace BM25. On devkit's and specrig's English documents (146 documents, 33 paraphrased queries, 2026-10-13), dense alone ranked slightly below BM25 (MRR 0.47 against 0.50), while hybrid raised recall at 5 from 0.70 to 0.76 and recall at 10 from 0.73 to up to 0.85, leaving the first hit unchanged. It finds documents whose wording differs from the query's.

## 3. Lexical Ranking

**Tokenizer.** Text is casefolded and decomposed (NFKD); the combining diacritical marks U+0300 to U+036F are removed and the rest is composed again (NFC). Words are runs of letters and digits; `_` and every other character separate them. `Café` gives `cafe`, `RULE-file_length` gives `rule`, `file`, `length`, and Hangul, kana and other scripts keep their letters. There is no stemming or stop-word list.

**BM25.** `k1 = 1.5`, `b = 0.75`, IDF `ln(1 + (N - n + 0.5) / (n + 0.5))` (always positive), and each distinct query term counted once. A document's lexical text is its `metadata` and `body` joined by a newline.

## 4. Dense Ranking

**Model.** The default model is `potion-base-8m`: [potion-base-8M](https://huggingface.co/minishlab/potion-base-8M), a static Model2Vec distillation of `BAAI/bge-base-en-v1.5` (English, 256 dimensions, 29,528 tokens), converted to float16 (15 MB). A static model has no network: a text's vector is the mean of the embedding rows of its tokens. Measured on the corpus of section 2, float16 and float32 rank identically; the smaller potion-base-4M and 2M models were within noise there but score 28.4 and 23.0 against 31.1 on MTEB retrieval.

**Encoding.** The text is tokenized with the model's tokenizer (no special tokens), unknown tokens are left out, the first `max_tokens` (512) tokens are kept, their rows are averaged in float32 and the mean is scaled to unit length. A text without tokens, or whose rows cancel out, gets the zero vector and therefore matches nothing. Keeping the first 512 tokens ranked better than embedding a whole document or its sections separately.

**Model packages.** A model ships as a data-only Python package that registers its module under the `devkit.embedding_models` entry-point group; the files sit next to the module's `__init__.py`:

| File | Content |
| --- | --- |
| `model.json` | `name`, `max_tokens`; the default package also pins its source (`repository`, `revision`, SHA-256 per source file) and the SHA-256 of each shipped file |
| `tokenizer.json` | A Hugging Face `tokenizers` file |
| `model.safetensors` | One tensor, `embeddings`, of shape `[vocabulary, dimensions]`, `F16` or `F32`; memory-mapped read-only |

`devkit.search` ships in `devkit-dist`. `devkit-embed` provides `potion-base-8m` and is installed by its `search` extra (`devkit-dist[search]`; `devkit-agt[search]` requires it) together with `numpy` and `tokenizers`. A missing extra is `SEARCH_EXTRA_MISSING`, whose `[FIX]` adds the extra to the devkit requirement the project declares, `devkit-agt[search]` or `devkit-dist[search]`, never a second requirement (`ADR-dist-module-split`). Another model needs only another package registering another name; `SearchIndex(..., model="<name>")` selects it. A name registered by two packages is `SEARCH_MODEL_INVALID`.

**Cost.** numpy and tokenizers are imported on the first dense, hybrid or `auto` search, never on `import devkit.search` or a `lexical` search (a test enforces this). On an Apple Silicon laptop the first dense search costs about 25 ms of imports and 25 ms to load the model; embedding 150 metadata texts takes a few milliseconds. An index embeds its documents once, on its first dense or hybrid search. There is no vector cache across processes.

## 5. Building the Model Package

The package lives in `models/devkit-embed`, outside the uv workspace, and is built only when the model changes; the `[tool.uv.sources]` of `devkit-dist` installs the released wheel, so the workspace and Git installs of `devkit-dist[search]` and `devkit-agt[search]` get the files without fetching them. The weights and tokenizer are not committed. `just model-build` runs `scripts/fetch_model.py`, which downloads each file from the pinned Hugging Face revision, checks its source SHA-256, rounds the float32 embeddings to float16 (round to nearest even, deterministic) with an 8-byte aligned canonical header, checks the output SHA-256 against `model.json` and moves the file into place (files that already match are left alone), then builds the wheel into `dist/model/`. The package's Hatch build hook refuses to build a wheel whose files are missing or do not match `model.json`; an editable install builds without them, and a dense search then reports `SEARCH_MODEL_INVALID`. The build is reproducible: a rebuild from the same `model.json` matches the released wheel byte for byte.

Licensing: potion-base-8M and bge-base-en-v1.5 are MIT licensed; the package ships the MIT license of Model2Vec as `LICENSE` and the provenance in `NOTICE`.

## 6. Module Layout

`devkit.search` imports only `devkit.core` and `devkit.advisory`; `devkit.distribution` ranks `devkit playbook search` with it (`CAP-DIST-context-and-playbooks`).

- `lexical.py`: `tokenize`, `Bm25`, `bm25_scores`.
- `dense.py`: `Embedder`, `load_embedder`, the model package layout.
- `fusion.py`: `reciprocal_rank_fusion`.
- `index.py`: `SearchIndex`, `SearchDocument`, `SearchHit`, `SearchMode`.
- `errors.py`: the `SearchError` hierarchy, one class per code ([reference](../../development/reference/search.md#error-codes)).
