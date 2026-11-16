---
id: SPEC-formal-document-kinds
title: First-class design, domain and operations document kinds
summary: Registers design, domain and operations as formal document kinds with complete identity, governance, authoring, discovery and migration support, replacing the ID-free direction.
status: planned
created: 2026-11-16
supersedes: PROP-operations-documents
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-formal-document-kinds] First-class design, domain and operations document kinds

## 1. Problem Statement & Motivation

Design, domain and operations need formal identity, discovery, governance and neutral authoring support.
The selected [core contract](../../../docs/materials/2026-11/20261116-formal-document-kinds/core-contract.md)
F1–F6 and `PROP-formal-document-kinds-target` define the accepted schema and migration. The previous ID-free
entries retain useful content but do not satisfy formal standing. `ADR-formal-role-document-identities` records
the partial supersession of the earlier identity restrictions while preserving responsibility boundaries.

## 2. User Stories

- **US-1**: As an agent, I can identify, search, resolve and reference each formal role directly in global and package roots.
- **US-2**: As an author, I can maintain independent detail and parent-owned supporting artifacts using shipped neutral templates and checks.
- **US-3**: As a maintainer, I can migrate existing content without losing incoming navigation or changing behavioral authority.

## 3. Non-Goals

1. **Scope Excluded**: Lifecycle derivation/apply and adaptive/SDD workflow integration belong to `PROP-design-document-lifecycle`.
2. **Scope Excluded**: Viewer rendering and handbook policy belong to `PROP-design-document-viewer`; both phases remain required for milestone completion.
3. **Scope Excluded**: New packages, feature edges, MCP services, recovery commands, reciprocal reference obligations or transfers of existing behavioral guarantees.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Formal identities and schema
- **Given** each role in global and registered namespace roots
- **When** documents are parsed and their identity/format/summary rules run
- **Then** DESIGN/design, DOMAIN/domain and OPS/operations use the exact flat prefixed grammar and required nonempty string metadata; draft/active/retired are the only statuses; invalid path/H1/status/reserved fields fail existing rules.

### [AC-02] Discovery, aliases and typed references
- **Given** real nodes of all three kinds, same-prefix aliases and related_designs/related_domains/related_operations fields
- **When** list, search, resolve, refs and canonical rewriting run
- **Then** all kinds are directly reachable; retired nodes require history/status for browsing but still resolve; namespace selection and repository-wide identity work; malformed, duplicate and unresolved relations fail; existing JSON keys and kind ordering remain compatible.

### [AC-03] Detail and artifact governance
- **Given** independent detail and parent-owned Markdown/non-Markdown support artifacts
- **When** identity and format rules run
- **Then** independent details require formal peer IDs; only an ID-free artifact under a same-root same-kind canonical parent's artifacts subtree is exempt; orphan, ID-bearing and stray nested Markdown fail. Rename/root-move/split/reclassification retain one artifact owner and repaired ordinary links in maintenance fixtures.

### [AC-04] Applicable source entrypoints
- **Given** canonical DESIGN, DOMAIN and OPS documents and source changes
- **When** entrypoint applicability, liveness and reverse file lookup run
- **Then** optional safe workspace-relative DESIGN paths participate; artifact/README paths do not; DOMAIN/OPS reject the field; deletion/escape controls fail, and retirement with removed source clears obsolete declarations.

### [AC-05] Neutral authoring and installed delivery
- **Given** the selected docs core bundle
- **When** it is synchronized and consumed from built wheels without devkit-spec
- **Then** eleven instructions and nine template files include the three formal templates/instructions and a compatibility pointer; get-context exposes the instructions; authored examples pass applicable rules without imposing SDD records or gates.

### [AC-06] Canonical migration and authoritative navigation
- **Given** four existing role documents and the archived operations input
- **When** migration completes
- **Then** all five exact active IDs in core-contract §7 exist, old canonical paths are absent, current ingress and source/detail links work, historical bytes remain intact, and current role boundaries/architecture/public references agree with implementation.

### [AC-07] Complete support and regression evidence
- **Given** the accepted F1–F6 support matrix
- **When** owned unit/integration/rule and installed-consumer checks run
- **Then** every applicable surface has real new-kind proof and existing-kind compatibility; lint/type/affected checks pass, the matrix records actual evidence, and required lifecycle/viewer phases remain explicitly pending.

## 5. Assumptions and measurement

The handoff base already includes the two dependent accepted plans. No new feature edge is needed. There is no
performance claim. Measure coverage as formal nodes recognized before/after (baseline: zero recognized role nodes;
head: all five migrated nodes) and record exact commands/results in development evidence. Preserve pinned contract bytes.
