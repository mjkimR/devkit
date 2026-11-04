---
id: PLAN-viewer-namespace-roadmap
spec: SPEC-viewer-namespace-roadmap
---

# Technical Plan: `SPEC-viewer-namespace-roadmap`

## 1. Constitution & Invariant Review

`ADR-viewer-namespace-roadmap-discovery` authorizes structural namespace discovery. Preserve
`ARCH-05-2-components`, `ADR-repository-viewer` and the independent read-only working-tree contract.
No new feature edge, dependency, API method or approval flow is needed.

## 2. Architecture Overview & Impact

`WorkingTreeReader.dashboard_headers` discovers roots with shallow metadata reads, then reads candidate headers.
A frontend API helper owns the same structural path policy and shallow discovery for generic dashboard and roadmap.
`buildRoadmap` already computes statuses before history filtering; expand its path predicate.
US-1 uses discovery; US-2 uses the combined graph and direct-member logic.

## 3. Component & Interface Design

Keep `RepositoryDataSource` unchanged. Share a frontend function returning milestone paths and discovery errors;
callers retain body loading and cache publication. Enumerate docs, optional packages, direct package directories,
their roadmap and flat archive. Keep proposal discovery in the roadmap loader. The generic dashboard retains the
six-request body scanner; optimized dashboard reads headers only. Python uses equivalent scenario tests.

## 4. Storage & State Management

No persisted data or migration. Existing callers own cache keys, generation tokens, TTL and page snapshots;
shared discovery has no cache. Rebuild the tracked static frontend artifact.

## 5. Error Handling & Edge Cases

Missing optional roots are empty; other errors retain successes and name failed paths. Validate direct children
against traversal and hostile source paths. Local symlinks remain filesystem-reader concerns; generic sources
retain observable type guarantees only. Abort and errors suppress cache publication.

## 6. Verification & Test Plan

AC-01/03/04: backend and frontend parity across global/two namespace/archive/config states.
AC-02: three cross-root directions, hidden archive, missing/unfinished and membership exclusions.
AC-05: namespace cases plus existing cache/page/concurrency/refresh suites.
AC-06: retained fixture before/after; viewer Python lint/type checks, test-affected from accepted input with full
fallback and its named frontend command; frontend lint/check/test/build and generated viewer-assets check.
Cumulative CI rules compare the retained base. Independent Code Review and Reconcile Review precede final report.
