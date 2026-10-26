---
id: FB-viewer-knowledge-anchor-loading
title: "Load knowledge tab anchors before bundle contents"
scope: repo
kind: suggestion
category: other
target: packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.svelte
origin: agent
severity: noise
recurring: false
status: dismissed
created_at: 2026-10-24
---

# [FB-viewer-knowledge-anchor-loading] Load knowledge tab anchors before bundle contents

Performance improvement for the knowledge tab's cold load.

## 2. Suggestion / Change Request

- **Current Procedure**: The knowledge tabs call indexDocuments before listing proposals or specs. One measured repository snapshot required 814 blob reads for the full index.
- **Proposed Procedure**: Load the selected tab anchors first and fetch bundle contents only after selection. Preserve document link resolution and malformed-document reporting explicitly.
- **Expected Benefit**: Reduce initial work after the existing 30-second cache expires.
- **Cost & Risk**: Lazy bundle reads change which parse failures can be known before selection; define that boundary before implementation.
- **Attempted**: Source inspection and local request profiling only; implementation is deferred beyond the dashboard change.

## Diagnostic Details

- **Reproduction**: Inspect `packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.svelte` and `frontend/src/lib/api/documents.ts` below the viewer package.
- **Expected / Actual**: The next optimization should target initial work rather than repeating cached results; cold knowledge views still load and process a broad document set.
- **Versions**: Reviewed source commit 990b404f; devkit-viewer 0.1.0.
- **Conditions**: A repository with hundreds of documents and no reusable result cache.
- **Workarounds Attempted**: Selective dashboard reads, recursive metadata and short-lived parsed-result caches are implemented in this unit.
- **Related Assets**: `SPEC-viewer-dashboard-loading`, `CAP-VIEW-repository-viewer`.

## Evidence

The knowledge tabs call indexDocuments before listing proposals or specs. One measured repository snapshot required 814 blob reads for the full index.

## Restart and Acceptance

Revisit when profiling identifies this path as the remaining user-visible delay. Compare cold first-list latency and blob counts against full indexing; preserve filters, bundle navigation and cross-document links.

## Disposition

Dismissed on the user's decision (2026-10-26). The Read tab, the cold path that mattered, now shows the handbook
first (`SPEC-viewer-handbook-first-knowledge`: 3 reads instead of 922). The Proposals and Specs tabs still index the
whole tree on first open, about one second locally with a 30-second cache, and anchor-first loading would first need
a design for which parse failures are known before selection. Re-raise it with fresh profiling if those tabs become
the user-visible delay.
