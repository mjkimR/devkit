---
id: PLAN-viewer-dashboard-loading
spec: SPEC-viewer-dashboard-loading
---

# Technical Plan: `SPEC-viewer-dashboard-loading`

## 1. Constitution & Invariant Review

No conflict with `CAP-VIEW-repository-viewer`. Keep browser parsing, injected data sources, current worktree reads and HTTP security boundaries.

## 2. Architecture Overview & Impact

Add a WeakMap result cache keyed by source, branch and purpose, limited to eight entries per source with a 30-second lifetime. Cache completed successes only. Independent requests retain their own abort signals. Cache full document indices and roadmap results too.

## 3. Component & Interface Design

Measured full-directory discovery needs over 450 HTTP calls in this repository. Add optional treeRecursive to RepositoryDataSource and recursive=true to the local tree endpoint. Use scandir metadata with follow_symlinks=False; retain path validation, symlink exclusion and .git exclusion. Recursive scans use one metadata call per root. Other injected hosts retain the worker fallback.

A shared scanDocuments loader uses six continuous workers and validates descendant paths. Dashboard loaders read milestone and proposal anchors from dedicated roots. Feedback discovery walks docs and specs directory metadata to preserve nested coverage, reading only feedback blobs. Each section owns loading and error state. Refresh invalidates the source cache before a new loading generation.

## 4. Storage & State Management

Retain caches across component remounts by source identity. Browser reload clears memory. Counts remain unknown until their section completes. Missing optional roots are empty; other errors remain visible and are not cached.

## 6. Verification & Test Plan

Vitest deferred sources verify selective reads, independent completion, worker refill, cache expiry, eviction, isolation, abort, retry and refresh. Component checks cover loading and source switches. Run viewer lint/check/test/build/pack, generated assets check and just test-affected. Review remaining loading paths and report concrete opportunities.


## 7. Measured Request Profile

One local HTTP run against this repository compared full indexing through per-directory requests with the selective dashboard.
The full index made 456 tree and 814 blob calls in 4233 ms.
The dashboard made seven tree, two recursive metadata and 172 blob calls.
Milestones completed at 46 ms, proposals at 78 ms and feedback at 763 ms.
A cache revisit made zero calls. These timings exclude browser rendering and are one warm filesystem run, not a portable latency guarantee.
The prior file adapter comparison read 4,108,717 bytes for the full index and 482,595 bytes for the dashboard.
