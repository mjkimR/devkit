---
id: SPEC-design-document-lifecycle
title: Formal documentation authoring and reconciliation lifecycle
summary: "Integrates formal design, domain and operations impact, maintenance and source agreement into existing SDD and adaptive development."
status: completed
created: 2026-11-16
depends_on:
  - SPEC-formal-document-kinds
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-design-document-lifecycle] Formal documentation authoring and reconciliation lifecycle

## 1. Problem Statement & Motivation

The delivered core gives DESIGN, DOMAIN and OPS formal standing. Delivery guidance still centers CAP/UC and
omits change-specific role impact and composed support-file maintenance. Existing delivery boundaries must consume
core policy and preserve one owner per statement. `ADR-formal-document-delivery-integration` selects this approach.
The accepted blueprint is `PROP-design-document-lifecycle-target`; its [integration contract](../../../docs/materials/2026-11/20261116-design-document-lifecycle/integration-contract.md)
L1–L4 remains binding. Core delivered at 5d1cb2661871cd3fe12cf806b58ac2515a3ffaf4 matches the selected interface.

## 2. User Stories

- **US-1**: As an agent, I identify affected formal responsibilities and maintain only warranted documents and artifacts.
- **US-2**: As an SDD author, I plan, review and reconcile formal statements and eligible source anchors using existing records.
- **US-3**: As an adaptive author, I maintain the same formal documents with source evidence and no implicit SDD lifecycle.

## 3. Non-Goals

1. **Scope Excluded**: Core schema/governance and Viewer/handbook implementation belong to their separate owners.
2. **Scope Excluded**: New registries, file movers, workflow stages, approvals, feature edges or recovery authority.
3. **Scope Excluded**: Whole-layer reading/update prerequisites and retrospective records for adaptive experiments.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Change-specific formal impact and maintenance
- **Given** each formal kind in global and registered package roots under SDD and adaptive development
- **When** read/create/update/split/rename/root-move/reclassify/retire procedures run
- **Then** canonical identities, aliases, relations, source and ordinary links remain valid; every artifact has one canonical parent; composed moves/transfers leave no stale duplicate; retirement preserves history access and removes obsolete DESIGN entrypoints in the source-deleting change.

### [AC-02] SDD Planning, review and reconciliation
- **Given** multi-role and mechanism-only changes
- **When** generated target-docs and existing plan/review/reconcile guidance are consumed
- **Then** affected formal IDs, source identity, statement owner, maintenance and verification are recorded; unaffected responsibilities have bounded reasons without empty edits; modified and deleted documents/support files are reconciliation targets.

### [AC-03] Core-eligible entrypoint derivation and application
- **Given** canonical DESIGN nodes, aliases, namespace roots and ineligible DOMAIN/OPS/README/artifact controls
- **When** actual derivation, explicit ID/alias/code selection and apply run
- **Then** core applicability controls candidates, DESIGN anchors suit their mechanism, apply preserves body bytes and is idempotent, ineligible paths produce no pairs, and CAP/UC behavior and CLI contracts remain compatible.

### [AC-04] Adoption and adaptive maintenance
- **Given** retained subjects and existing SDD history in an adaptive repository
- **When** brownfield/baseline/documenter guidance maintains warranted formal coverage
- **Then** source evidence and missing required documents are accounted for; stale evidence is invalidated; current context maps IDs or undocumented; adaptive approach and historical bytes remain unchanged with no implicit Unit/envelope/gate.

### [AC-05] Source assets, installed delivery and regression
- **Given** the spec and adaptive bundles
- **When** source, sync/get-context, installed-consumer and affected checks run
- **Then** role routing and maintenance guidance agree across selected assets and pointers, L1–L4 has actual new-kind evidence, lint/type/rules/tests pass, and required Viewer work remains pending.

## 5. Assumptions and measurement

Core F1–F6 is delivered, not a future-interface assumption. Existing entrypoint derivation consumes
entrypoint_bearing; no new Kind registry or feature edge is needed. Measure generated blueprint formal impact prompts
before/after and execute the kind × approach × root maintenance matrix. Scripted procedures prove observable
maintenance, not autonomous semantic judgment; record source-identified comparison separately.
