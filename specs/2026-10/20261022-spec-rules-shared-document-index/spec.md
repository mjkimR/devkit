---
id: SPEC-spec-rules-shared-document-index
title: Share one document index across a rules run
summary: Lets the spec rules and markdown_link share one in-process document index and catalog per rules run, and keeps markdown_link to its targets, so targeted runs such as workflow lint-clean stop re-reading every document.
status: completed
created: 2026-10-22
related_capabilities:
  - CAP-GOV-rules-engine
  - CAP-GOV-spec-rules
related_usecases:
  - UC-keep-the-living-spec-consistent
workflow: sdd-spec-feature
---

# [SPEC-spec-rules-shared-document-index] Share one document index across a rules run

## 1. Problem Statement & Motivation

During targeted rules evaluation (such as `devkit workflow next` running `lint-clean` on targeted files), performance is heavily impacted by redundant Markdown document reads and parsing. Seven spec governance rules (`code_entrypoints`, `document_reference`, `document_summary`, `id_convention`, `proposal_boundaries`, `spec_format`, `traceability_link`) each independently call `document_index(ctx)`, rebuilding `DocumentIndex.load` up to 7 times per run across ~690 Markdown files.

Additionally, `RULE-markdown-link` unconditionally calls `ctx.cache.get_catalog(root)` upon evaluation, which scans every Markdown file in the entire workspace to build a basename index, even when every link in the targeted files is valid and no repair candidate lookup is needed.

Sharing one in-process document index across spec rules within a `RuleContext` and deferring catalog construction in `RULE-markdown-link` eliminates this redundant overhead while keeping rule findings identical.

## 2. User Stories

- **US-1**: As a developer running `devkit workflow next` or `devkit rules check`, I want targeted rules execution to run without repeatedly re-reading and re-hashing all workspace documents across multiple rules.
- **US-2**: As an agent fixing rules with `devkit rules fix`, I want the shared document index to invalidate properly after file modifications so that convergence rechecks evaluate updated document content.

## 3. Non-Goals

1. **No timestamp-based disk memo skipping**: We do not replace BLAKE2b content digest verification in `ParseMemo` with filesystem timestamps (`mtime`), preserving the exactness guarantees of `ADR-content-keyed-document-parse-memo`.
2. **No reverse dependency from `devkit-agt` to `devkit-spec`**: `WorkspaceCache` provides a generic cache slot (`get_or_compute`) without importing `DocumentIndex` or any spec document structures.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Shared DocumentIndex across spec rules in one rules evaluation run
- **Given** a `RuleContext` in a rules evaluation run (such as `evaluate_rules`),
- **When** multiple spec governance rules call `document_index(ctx)`,
- **Then** `DocumentIndex.load` is executed only once, and subsequent calls within the same run return the cached `DocumentIndex` instance.

### [AC-02] Cache invalidation on workspace write during autofix
- **Given** a `RuleContext` with a cached `DocumentIndex`,
- **When** `ctx.cache.write_text` modifies a Markdown file or `ctx.cache.invalidate_all()` is called,
- **Then** the cached `DocumentIndex` is purged so subsequent calls return a fresh `DocumentIndex`.

### [AC-03] Deferred DocumentCatalog build in `RULE-markdown-link`
- **Given** a targeted rules run evaluating `RULE-markdown-link` on Markdown files where all relative links exist and resolve to valid targets,
- **When** `MarkdownLinkRule.check(ctx)` evaluates the targeted files,
- **Then** `ctx.cache.get_catalog` is not invoked and whole-workspace Markdown scanning does not occur.

### [AC-04] Candidate repair on broken link in `RULE-markdown-link`
- **Given** a targeted rules run evaluating `RULE-markdown-link` on a Markdown file containing a broken relative link,
- **When** `MarkdownLinkRule.check(ctx)` evaluates the broken link,
- **Then** `ctx.cache.get_catalog` is invoked lazily to provide unique candidate repairs by basename.

### [AC-05] Rule findings byte-identical across workspace and targeted runs
- **Given** rules evaluation across the entire repository or a subset of files,
- **When** evaluating governance rules with the shared document index and deferred catalog build,
- **Then** rule findings (violations, line numbers, remediation messages) are identical to the unscoped/unshared baseline.
