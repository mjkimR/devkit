---
id: FB-search-model-invalid-scope-disagrees
title: Document search capability limits SEARCH_MODEL_INVALID to explicit modes while the search capability raises it in auto too
scope: repo
kind: friction
category: docs-mismatch
target: CAP-DOCS-document-search
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-search-model-invalid-scope-disagrees] Document search capability limits SEARCH_MODEL_INVALID to explicit modes while the search capability raises it in auto too

## 1. Friction / Question (friction, question)

- **Context**: Writing an operations routing entry for document search mode and model errors.
- **Expectation**: `CAP-DOCS-document-search` §4.5 and `CAP-SRCH-document-search` §2 agree on when `SEARCH_MODEL_INVALID` reaches the caller.
- **Actual**: §4.5 says the three `SEARCH_*` codes pass through for explicit dense or hybrid searches; `CAP-SRCH-document-search` §2 and `SearchIndex.resolve_mode` raise `SEARCH_MODEL_INVALID` in every mode, auto included. The source matches neither fully: `--mode lexical` never loads the model, so it never raises the code, while auto, dense and hybrid do.
- **Workaround (or Interpretation Chosen)**: The new operations entry follows the search capability and the source.
- **Suggestion**: Narrow the §4.5 sentence so only `SEARCH_EXTRA_MISSING` and `SEARCH_MODEL_NOT_FOUND` are explicit-mode only, and replace "every mode" in `CAP-SRCH-document-search` §2 with the modes that load the model.

## Diagnostic Details

- **Reproduction**: Read-only source comparison.
- **Expected / Actual**: `devkit docs search` exit and code for a broken model package under `--mode auto`.
- **Versions**: repository head of the formal-document-coverage Development branch.
- **Conditions**: not reproduced; a broken model package was not installed
- **Workarounds Attempted**: not attempted
- **Related Assets**: packages/devkit-dist/src/devkit_dist/features/search/services/index.py, CAP-DOCS-document-search, CAP-SRCH-document-search

## Evidence

```text
CAP-DOCS-document-search §4.5: "SEARCH_EXTRA_MISSING, SEARCH_MODEL_NOT_FOUND and SEARCH_MODEL_INVALID pass through for explicit dense or hybrid searches"
CAP-SRCH-document-search §2: "A broken model package MUST raise SEARCH_MODEL_INVALID in every mode."
packages/devkit-dist/src/devkit_dist/features/search/services/index.py resolve_mode catches only SearchExtraMissingError and ModelNotFoundError; the LEXICAL branch of search never touches the embedder
```

## Disposition

- **Disposition**: Resolved in SPEC-remaining-feedback-fixes: CAP-DOCS-document-search 4.5 and CAP-SRCH-document-search 2 now state that SEARCH_MODEL_INVALID passes through for every mode that loads the model (auto, dense, hybrid) and never for lexical, while SEARCH_EXTRA_MISSING and SEARCH_MODEL_NOT_FOUND pass through only for explicit dense or hybrid.
