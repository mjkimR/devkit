---
id: FB-viewer-book-rendering
title: "Render book chapters near the viewport"
scope: repo
kind: suggestion
category: other
target: packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.svelte
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-24
---

# [FB-viewer-book-rendering] Render book chapters near the viewport

Performance improvement for the knowledge tab's cold load.

## 2. Suggestion / Change Request

- **Current Procedure**: The rendered derived value maps every visibleDocs document through renderDocument. In book view visibleDocs is the whole book; only diagrams use an IntersectionObserver. renderDocument also rebuilds its ID index for each document.
- **Proposed Procedure**: Measure browser parsing and rendering costs, share the document link index, and render chapter bodies near the viewport with stable headings and jump targets.
- **Expected Benefit**: Reduce initial work after the existing 30-second cache expires.
- **Cost & Risk**: Deferred rendering can break document jumps and heading tracking unless lightweight anchor placeholders are retained.
- **Attempted**: Source inspection and local request profiling only; implementation is deferred beyond the dashboard change.

## Diagnostic Details

- **Reproduction**: Inspect `packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.svelte` and `frontend/src/lib/api/documents.ts` below the viewer package.
- **Expected / Actual**: The next optimization should target initial work rather than repeating cached results; cold knowledge views still load and process a broad document set.
- **Versions**: Reviewed source commit 990b404f; devkit-viewer 0.1.0.
- **Conditions**: A repository with hundreds of documents and no reusable result cache.
- **Workarounds Attempted**: Selective dashboard reads, recursive metadata and short-lived parsed-result caches are implemented in this unit.
- **Related Assets**: `SPEC-viewer-dashboard-loading`, `CAP-VIEW-repository-viewer`.

## Evidence

The rendered derived value maps every visibleDocs document through renderDocument. In book view visibleDocs is the whole book; only diagrams use an IntersectionObserver. renderDocument also rebuilds its ID index for each document.

## Restart and Acceptance

Revisit when profiling identifies this path as the remaining user-visible delay. Measure main-thread work and first-content latency with a large book while preserving ID links, anchors, DOMPurify and theme behavior.
