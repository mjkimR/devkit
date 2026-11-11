---
id: SPEC-remove-test-only-public-apis
title: Remove test-only public APIs
summary: 'Removes public parameters and APIs only tests use: the worktree finish and discard before_remove hook, status_records renames/ignore_submodules, and search bm25_scores, SearchIndex.search limit and SearchHit.to_dict.'
status: in-progress
created: 2026-11-11
related_capabilities: [CAP-WT-task-worktrees, CAP-SRCH-document-search]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-remove-test-only-public-apis] Remove test-only public APIs

## 1. Problem Statement & Motivation

The review-refactor code pass (findings AO-13, SM-3 and DS-14 in its material report) found public parameters and
API members that no production code calls: only tests exercise them, yet they are documented contracts that every
later change must keep working. Removing them shrinks the surface to what devkit uses. devkit has no external
consumer of these library APIs, so no compatibility shim is kept.

- **AO-13**: `finish(..., before_remove=)` and `discard(..., before_remove=)` in the worktree lifecycle library.
  `finish`'s `before_step("worktree_remove", result)` runs at the same point (once the merge is confirmed, before the
  removal) and the CLI's cleanup goes through the `devkit.post_finish` extensions.
- **SM-3**: `devkit_core.core.git.status_records`'s `renames` and `ignore_submodules` parameters.
- **DS-14**: `devkit_dist.features.search`'s `bm25_scores`, `SearchIndex.search(limit=)` and `SearchHit.to_dict`.

## 2. User Stories

- **US-1**: As a devkit maintainer, I want library APIs to expose only what production code uses, so that each
  documented contract is one devkit relies on.

## 3. Non-Goals

1. **Scope Excluded**: `status_records`'s `*pathspecs` stays: the maintenance-history snapshot
   (`devkit_agt.features.maintenance_history.repositories.snapshot.capture`) passes pathspecs, so it has a production
   caller. `untracked`, `optional_locks` and `deadline` stay (production callers and `dirty_paths`).
2. **Scope Excluded**: `SearchIndex`'s `model=` and `embedder=`, `Bm25`, `tokenize` and `reciprocal_rank_fusion` stay.
3. **Scope Excluded**: `finish`'s `before_step`, `guard` and `merge` parameters, the `devkit.post_finish`
   extension point and the `devkit worktree` CLI are unchanged (`finish --merge` retirement is separate work).
4. **Scope Excluded**: no deprecation shim, and `devkit-cli` and `devkit.advisory` are not touched.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The worktree lifecycle has no `before_remove` hook

- **Given** the worktree library functions `finish` and `discard`
- **When** a caller passes `before_remove=`
- **Then** Python raises `TypeError` (no such keyword), and the worktree tests that used it verify the same
  cleanup point through `finish`'s `before_step("worktree_remove", result)` (an `AdvisoryError` raised there still
  carries the partial result as `error.result`) and pass.

### [AC-02] `status_records` keeps only its used parameters

- **Given** `devkit_core.core.git.status_records`
- **When** its signature is inspected
- **Then** it is `status_records(cwd, *pathspecs, untracked="all", optional_locks=False, deadline=None)`, a call with
  `renames=` or `ignore_submodules=` raises `TypeError`, and the core tests for rename, copy, pathspec and untracked
  records pass.

### [AC-03] The search API drops its unused members

- **Given** `devkit_dist.features.search`
- **When** a caller imports `bm25_scores`, calls `SearchIndex.search(..., limit=)` or `SearchHit(...).to_dict()`
- **Then** the import raises `ImportError`, the call raises `TypeError` and the attribute access raises
  `AttributeError`; `SearchIndex.search` returns every matching hit best first, and `just test-dist` passes.

### [AC-04] The Living Spec matches the remaining surface

- **Given** `CAP-WT-task-worktrees`, `CAP-SRCH-document-search` and the worktree, search and core references
- **When** a reader looks up the removed members
- **Then** none of the documents names `before_remove`, `renames=`, `ignore_submodules`, `bm25_scores`,
  `search(limit=)` or `SearchHit.to_dict`, and `uv run devkit rules check` passes.

## 5. Assumptions

- The production-caller check covered `packages`, `tools`, `scripts`, `guides` and `docs` (entry points included);
  only `*pathspecs` had a caller, so it is kept as a recorded deviation from the intent's SM-3 list.
- `discard` gets no replacement hook: no production caller needs one, and its tests check the result instead.
