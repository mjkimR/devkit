---
id: PROP-document-id-aliases-and-compaction
title: Document ID Aliases and ADR Compaction
summary: "Introduces an optional aliases frontmatter field across Living Spec documents to preserve referential integrity during renaming and compaction, and defines an ADR compaction procedure to consolidate fragmented architectural decision chains."
status: draft
created_at: 2026-10-21
target_area: capabilities/documents/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/decisions/
  excludes:
    - packages/devkit-dist/src/devkit_dist/features/search/
    - packages/devkit-viewer/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-document-id-aliases-and-compaction] Document ID Aliases and ADR Compaction

## 1. Background & Hypothesis

Architecture Decision Records (ADRs) are managed under `docs/decisions/` as an append-only permanent ledger recording critical structural decisions and invariants (`ADR-dual-source-of-truth-and-periodic-reconciliation`). In accordance with standard ADR governance, approved ADRs are never retroactively modified or deleted in-place; when an update is required, authors create a new ADR linked via `supersedes` and `superseded_by`.

However, rapid development produces a proliferation of fine-grained decisions—over 70 ADRs were committed within a single month. This leads to several compounding problems:
1. **Context Window Debt**: AI agents and human engineers navigating architectural decisions face long, fragmented supersession chains (`ADR-step-1 -> ADR-step-2 -> ADR-step-3`), consuming excessive context budget and obscuring the current state of truth.
2. **Referential Fragility**: Merging or consolidating multiple micro-decisions into a unified record by deleting old files causes broken references across git commits, completed feature specs (`specs/`), and Living Spec documents, triggering `RULE-document-reference` errors.
3. **Playbook Schema Divergence**: The playbook asset format in `devkit-dist` currently uses an `aliases` array exclusively for manual keyword/synonym search matching. With the arrival of hybrid BM25 and dense embedding ranking (`SearchIndex`), manual search aliases are largely redundant, while the broader Living Spec document model lacks any formal alias/tombstone mechanism.

**Core Hypothesis:**
Introducing an optional `aliases: list[str]` frontmatter field across Living Spec documents (ADRs, Capabilities, Stories, Proposals) and indexing it as secondary identifiers in `DocumentIndex` will:
- Allow multiple historical ADRs to be consolidated and replaced by a unified record without breaking incoming references or triggering governance violations.
- Enable `RULE-document-reference` to validate alias references and optionally provide an automated fix (`devkit rules fix`) that migrates obsolete alias references to the canonical target ID.
- Establish a repeatable, governed **ADR Compaction Procedure** that resolves decision fragmentation while honoring architectural immutability.

## 2. Technical Spike Questions

- **Q1 (Identity & Resolution)**: How should `DocumentIndex.resolve(document_id)` resolve alias conflicts? If an alias collides with an existing canonical `id` or another document's alias, how should `DuplicateIdError` or resolution priority be enforced?
- **Q2 (Linter & Autofix Behavior)**: Should `RULE-document-reference` treat an alias reference as fully valid, or report it as a warning/notice encouraging canonical migration? How should `devkit rules fix` rewrite prose links (e.g., bracket form `[ADR-<slug>]` vs code-span `ADR-<slug>`)?
- **Q3 (Historical Boundary)**: How does compaction interact with completed spec history (`specs/`)? Can an old ADR file be safely deleted once referenced as an alias in a new consolidated ADR, or should a minimal tombstone header be preserved?
- **Q4 (Playbook Schema Alignment)**: Should playbook search aliases be harmonized with document ID aliases, or cleanly deprecated in favor of hybrid search over `name` and `description`?

## 3. Proposed Design & Impact

### 3.1 Document Model Extension (`CAP-DOCS-document-model`)
- Extend the `Document` dataclass and frontmatter schema to parse an optional `aliases` list:
  ```yaml
  ---
  id: ADR-consolidated-worktree-management
  title: Consolidated Worktree Management
  summary: "Unifies worktree creation, isolation levels, and close/discard lifecycle into a single authoritative record."
  status: accepted
  aliases:
    - ADR-worktree-and-pull-request-levels
    - ADR-branch-guards-and-close-discard
  supersedes:
    - ADR-worktree-and-pull-request-levels
    - ADR-branch-guards-and-close-discard
  ---
  ```
- `DocumentIndex` maintains a secondary index mapping alias IDs to their declaring documents.
- `DocumentIndex.resolve(id)` first attempts exact `id` lookup; if not found, it resolves against `by_alias`.
- Enforce uniqueness: an alias cannot duplicate an active document's primary `id` or an alias declared elsewhere.

### 3.2 Governance Integration (`RULE-document-reference`)
- References targeting a registered alias are considered resolved.
- During lint checks, referencing an alias can either pass cleanly or emit an informational hint (`ALIAS_REFERENCE`).
- Under `devkit rules fix`, references to an alias can be deterministically rewritten to the canonical `id` in targeted active files, while completed historical files remain untouched.

### 3.3 ADR Compaction Procedure
- **Scope Identification**: Group related micro-ADRs that represent incremental iterations or refinements of the same subsystem.
- **Consolidation**: Author a unified ADR summarizing the current coherent decision.
- **Context Synthesis**: In the unified ADR's `Context` and `Considered Options`, summarize why intermediate options were discarded or superseded, retaining essential historical rationale without requiring traversal of obsolete files.
- **Provenance Linkage**: Register old IDs in `aliases` and `supersedes`.
- **Tombstone vs Deletion**: Old ADR files may either be removed (relying on `aliases` resolution and git history) or retained with `status: superseded` pointing to the consolidated record.

## 4. Lifecycle & Retirement Criteria

- **PADR Candidate**: A preliminary decision (`PADR-document-id-aliases-and-compaction.md`) will evaluate whether old consolidated files should be physically deleted or kept as minimal tombstones.
- **Verification**:
  - Unit tests in `packages/devkit-spec/tests/unit/features/documents/` for frontmatter parsing, duplicate alias detection, and index resolution.
  - Governance tests in `packages/devkit-spec/tests/unit/features/governance/` verifying `RULE-document-reference` behavior against aliases.
  - An end-to-end fixture demonstrating compaction of two sample ADRs into a consolidated record with clean rules check and link resolution.
- **Acceptance Gate**: Normal proposal review and acceptance (`devkit spec proposal accept document-id-aliases-and-compaction`).
