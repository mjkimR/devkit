---
sources:
  CAP-DIST-context-and-playbooks: 34185acd0c3f1a6432909d7718d9b18f52eda6cf
  CAP-DOCS-document-search: b1fd38fddef38d5c97d094208acf6b5077e6f3f4
  CAP-SRCH-document-search: c77c202fd04e0cdec4687133cbef9637642eb0ca
  UC-find-the-right-documents: 722935d391e97c4a537ebe9d3950228b540dc591
title: Search
---

# Search

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `ae01161143be`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

The search area is the ranking engine behind `devkit playbook search` and `devkit spec search`. It knows documents
only as an ID, some metadata text and an optional body, and it ranks them against a query lexically, by meaning or
both. Which documents are candidates, and pinning an exact match first, is left to the command that calls it. The
contract is
[CAP-SRCH-document-search](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/search/CAP-SRCH-document-search.md).

## Where you meet it

| Command | Candidates | Contract |
| --- | --- | --- |
| `uv run devkit playbook search "<query>"` | synchronized playbook headers (`name`, `description`) | `CAP-DIST-context-and-playbooks` |
| `uv run devkit spec search <query>` | current Living Spec documents | `CAP-DOCS-document-search` |

Finding Living Spec documents end to end is the journey
[Find the right documents](../journeys/find-the-right-documents.md) (`UC-find-the-right-documents`); playbook
discovery is covered in [Distribution](distribution.md) and the spec command in [Documents](documents.md).

## Pick a mode

| Mode | What it does | Needs |
| --- | --- | --- |
| `auto` (default) | `hybrid` when the search extra is installed, else `lexical` | nothing |
| `lexical` | BM25 over metadata and body | standard library only |
| `dense` | cosine similarity of query and metadata embeddings | the `search` extra |
| `hybrid` | Reciprocal Rank Fusion of the two rankings | the `search` extra |

Both commands accept `--mode`. Only `auto` falls back: an explicit `dense` or `hybrid` without the extra fails with
`SEARCH_EXTRA_MISSING` (or `SEARCH_MODEL_NOT_FOUND`), and every result names the mode that actually ran, so you
always know what kind of ranking you got.

Hybrid is the better default when it is available. On devkit's own English documents dense alone ranked slightly
below BM25, while hybrid kept the first hit and raised recall in the top five and top ten: it finds documents whose
wording differs from your query.

## Install the search extra

Add the extra to the devkit requirement your project already declares, never as a second requirement:
`devkit-agt[search]` or `devkit-dist[search]` (and `devkit-spec[search]` for spec search). It brings `numpy`,
`tokenizers` and the `devkit-embed` model package, which provides the default model `potion-base-8m`. The model is
static and local: it needs no network, loads in tens of milliseconds and is imported only on the first dense, hybrid
or `auto` search, never for a lexical one.

## Write documents that search well

- The embedding model is English-only and reads only metadata. Give every document English metadata: a playbook's
  `name` and `description`, a Living Spec document's `summary`. Bodies may be in any language and still count
  lexically.
- The tokenizer casefolds, drops Latin accents and splits on `_`, `-` and every other non-letter character
  (`RULE-file_length` becomes `rule`, `file`, `length`). There is no stemming and no stop-word list.
- In `dense` and `hybrid` most unrelated texts get some positive similarity, so a floor matters:
  `--min-similarity` defaults to `0.35` in both commands, measured to drop the long tail while keeping the hybrid
  gain.

## Use another model

A model is a data-only Python package registering its module under the `devkit.embedding_models` entry point, with
`model.json`, `tokenizer.json` and `model.safetensors` beside it. Installing another package with another name makes
it selectable from the library. The default package lives in `models/devkit-embed` with a committed, reproducible
wheel built by `just model-build`, so workspace commands and tests run offline. A broken model package fails with
`SEARCH_MODEL_INVALID` in every mode.
