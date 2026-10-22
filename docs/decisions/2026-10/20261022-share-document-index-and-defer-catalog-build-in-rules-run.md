---
id: ADR-share-document-index-and-defer-catalog-build-in-rules-run
title: Share document index and defer catalog build in rules run
summary: For Markdown rules in devkit-spec and devkit-agt, we share one DocumentIndex per rules run via WorkspaceCache and defer DocumentCatalog building in markdown_link, to eliminate redundant re-reads and whole-workspace scans, accepting that the shared index is read-only.
proposal: SPEC-spec-rules-shared-document-index
status: accepted
created_at: 2026-10-22
---

# [ADR-share-document-index-and-defer-catalog-build-in-rules-run] Share document index and defer catalog build in rules run

- **Status**: Accepted
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

Evaluating Markdown rules during a rules run (such as `devkit workflow next` running `lint-clean` on targeted files) is currently bottlenecked by redundant indexing. Seven spec rules independently call `document_index(ctx)`, each triggering `DocumentIndex.load` which scans, reads, and hashes all ~690 Markdown files, totaling over 300 ms across the run even with a warm parse memo. Meanwhile, `RULE-markdown-link` unconditionally constructs `DocumentCatalog` across the entire workspace upon evaluation, scanning every Markdown file even when all links in the targeted files are valid and no repair candidate lookup is needed.

## 2. Decision Drivers

- Rule findings remain identical for both whole-workspace and targeted runs.
- Redundant file reads, hashes, and AST/catalog constructions across rules are eliminated from rules evaluation.
- Package boundaries between `devkit-agt` (foundation harness) and `devkit-spec` (spec extension) remain strict and acyclic.
- Invalidation upon autofix (`ctx.cache.write_text`) reliably purges cached indices before convergence rechecks.

## 3. Considered Options

- **Shared index in `WorkspaceCache` and deferred catalog in `markdown_link`**: `WorkspaceCache` provides a run-scoped computed cache helper (`get_or_compute`), which `document_index(ctx)` uses to build and reuse `DocumentIndex` once per `RuleContext`. `markdown_link` defers calling `ctx.cache.get_catalog(root)` until a broken relative link is encountered.
- **Stat-based file skipping in parse memo**: skip reading and hashing files whose mtime/size have not changed since the memo write. Violates the correctness-by-construction driver of `ADR-content-keyed-document-parse-memo` due to clock skew and filesystem granularity risks.
- **Keep independent rule loads**: zero architectural changes, but retains over 300 ms of repeated index loads and whole-workspace catalog scans on every targeted workflow run.

## 4. Decision Outcome

Chosen: **Shared index in `WorkspaceCache` and deferred catalog in `markdown_link`**.

- **WorkspaceCache shared slot**: add a generic per-run cache helper (`get_or_compute(key: str, factory: Callable[[], T]) -> T`) to `WorkspaceCache`, purged on `invalidate_all()` and file writes.
- **Spec rules memoization**: `document_index(ctx)` retrieves or computes `DocumentIndex` via `ctx.cache.get_or_compute("spec.document_index", ...)`, ensuring exactly one build per `RuleContext`.
- **Autofix invalidation**: when `ctx.cache.write_text` modifies a Markdown file, `spec.document_index` and `_catalog` are invalidated so convergence rechecks see updated content.
- **Deferred markdown catalog**: `MarkdownLinkRule._broken_links` retrieves `ctx.cache.get_catalog(root)` lazily only when an invalid local target requires a repair candidate.

## 5. Consequences

- Positive: cuts `DocumentIndex.load` invocations from up to 7 down to 1 per rules run, saving ~300 ms on targeted runs like `workflow next`.
- Positive: eliminates whole-workspace directory walks and basename catalog builds in `markdown_link` when all links in target files exist.
- Positive: preserves unidirectional layering: `devkit-agt` remains unaware of `DocumentIndex`.
- Negative: cached `DocumentIndex` instance remains in memory for the duration of the `RuleContext` (negligible RSS impact, < 5 MB).
- Risk (accepted): rules receiving `DocumentIndex` must treat it and its parsed documents as strictly read-only.

## 6. Confirmation

- Unit tests in `packages/devkit/tests/unit/` and `packages/devkit-spec/tests/unit/` verify that `get_or_compute` caches results and invalidates properly on `write_text`.
- Integration tests verify that `markdown_link` passes without building `DocumentCatalog` when no links are broken.
- Rule evaluation output on this repository remains identical before and after the change.
