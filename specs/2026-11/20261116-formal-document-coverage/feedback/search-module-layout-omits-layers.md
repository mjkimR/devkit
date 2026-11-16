---
id: FB-search-module-layout-omits-layers
title: The search capability module layout lists modules without their feature layers
scope: repo
kind: friction
category: docs-mismatch
target: CAP-SRCH-document-search
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-search-module-layout-omits-layers] The search capability module layout lists modules without their feature layers

## 1. Friction / Question (friction, question)

- **Context**: A Planning scout located search sources for an operations routing candidate.
- **Expectation**: `CAP-SRCH-document-search` §6 Module Layout locates the modules it names.
- **Actual**: §6 lists `lexical.py`, `dense.py`, `fusion.py`, `index.py` and `errors.py` directly under
  `devkit_dist.features.search`; the files live in `services/` (`lexical`, `dense`, `fusion`, `index`) and `models/`
  (`contracts`, `errors`). `contracts.py` is not listed.
- **Workaround (or Interpretation Chosen)**: Located the files by listing the package.
- **Suggestion**: Name the layer for each module, or move the layout statement to the reference or architecture owner.

## Evidence

```text
packages/devkit-dist/src/devkit_dist/features/search/services/: dense.py fusion.py index.py lexical.py
packages/devkit-dist/src/devkit_dist/features/search/models/: contracts.py errors.py
```

## Disposition

- **Disposition**: Resolved in SPEC-remaining-feedback-fixes: CAP-SRCH-document-search 6 now names each module with its layer: services/lexical.py, services/dense.py, services/fusion.py, services/index.py (SearchIndex), models/contracts.py (SearchMode, SearchDocument, SearchHit) and models/errors.py.
