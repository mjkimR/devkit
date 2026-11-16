---
id: SPEC-design-document-foundation
title: Documentation ownership and minimal design foundation
summary: Uses the completed pilot to settle documentation ownership and linked ID-free design entries, without new indexed kinds or runtime support.
status: completed
created: 2026-11-16
depends_on:
  - SPEC-design-document-pilot
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
# [SPEC-design-document-foundation] Documentation ownership and minimal design foundation

## 1. Problem Statement & Motivation

The completed `SPEC-design-document-pilot` demonstrated a useful supplied mechanism entry but no direct
contract-to-detail discovery route. Clean ownership is the primary goal: separate domain meaning, current design
and operational composition alongside contracts and architecture. The accepted
`ADR-documentation-ownership-and-linked-design-entries` selects linked ID-free entries without runtime expansion.

## 2. User Stories

- **US-1**: As an author, I want one normative owner per statement so that architecture and mechanism explanations
  do not compete with contracts or recovery authority.
- **US-2**: As an agent investigating replacement, I want to discover a useful design explanation from the known
  transaction contract in global and package contexts.
- **US-3**: As a docs-bundle consumer, I want generic ownership guidance and an optional template without repository IDs.

## 3. Non-Goals

**Scope Excluded**: New Kind, ID grammar, registry, metadata, runtime or UI; domain/operations final homes;
lifecycle integration; recovery execution; unrelated architecture corrections; new package or feature dependency.
Existing pilot evidence and `FB-runtime-journal-ordering` remain unchanged. Domain, operations, lifecycle and viewer
work remain with `PROP-domain-model-documents`, `PROP-operations-documents`, `PROP-design-document-lifecycle`
and `PROP-design-document-viewer`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] F1: Unique ownership
- **Given** the routing and pilot cases in the preserved target-docs material,
- **When** the shared capability, architecture boundary and generic guidance are reviewed,
- **Then** each normative statement has one owner; domain/design/operations retain distinct roles; no normative
  transfer, duplicate recovery procedure, numeric routing threshold or authoring DAG is introduced.

### [AC-02] F2: Useful ID-free representation
- **Given** the maintained transaction entry and independently readable detail,
- **When** an agent opens either directly,
- **Then** it receives the question, useful explanation, authority boundary and next useful detail/source;
  source symbols and relative links agree with current implementation and no design ID is introduced.

### [AC-03] F3: Independent global discovery
- **Given** only the transaction capability and original file/directory replacement question, with entry names withheld,
- **When** an independent reader follows question-specific links,
- **Then** it reaches the maintained entry and necessary detail/source; the record names start information, sections
  opened, avoidable reads/returns and next-step clarity, with failures fixed or returned rather than waived.

### [AC-04] F4: Package discovery and namespace boundaries
- **Given** a disposable registered package fixture and unrelated package owner,
- **When** a reader starts from its package source cwd using existing list/search/resolve/refs and owner links,
- **Then** the analogous relative entry/detail/source route works; global selection filters package owners while
  retaining global owners; the unrelated owner is unaffected; no design index/search/resolve/refs coverage is claimed.

### [AC-05] F5: Consumer delivery
- **Given** the source bundle's existing templates asset and modified instructions,
- **When** a consuming-repository fixture installs/syncs the bundle,
- **Then** the optional ID-free template and generic guidance arrive without repository-specific IDs, required empty
  hierarchy, new asset declaration or hand-edited projections; source asset and sync checks pass.

### [AC-06] F6: Current-state verification
- **Given** the completed documentation and source-asset diff,
- **When** scoped and CI rules, source/link/index checks, affected tests, independent review and reconciliation run,
- **Then** required checks pass and their actual scope and limitations are retained without runtime/viewer/recovery claims.

## 5. Evidence and Assumptions

Preserved [direction](../../../docs/materials/2026-11/20261116-design-document-foundation/direction.md) and
[target documents](../../../docs/materials/2026-11/20261116-design-document-foundation/target-docs.md) bind F1–F6.
Planning measured contract-only R1/V1 discovery gaps; Development compares observed routes qualitatively, without
elapsed-time or whole-corpus claims. Package fixtures prove format/discovery, not real demand. Current base retains
the accepted premises; the handoff skeletons require specification promotion, not a changed agreement.
