---
id: PROP-design-document-lifecycle
title: Documentation-layer authoring and reconciliation lifecycle
summary: "Integrates impact-based authoring and reconciliation for domain, design and operations, reusing existing lifecycle mechanisms and avoiding mandatory updates to unaffected layers."
status: draft
created_at: 2026-11-16
target_area: delivery/
priority: high
size: L
planning_effort: high
dev_effort: medium
milestone: MS-documentation-system-evolution
boundaries:
  owns:
  - packages/devkit-docs/src/devkit_docs/bundles/
  - packages/devkit-spec/
  - packages/devkit-adaptive/
  - docs/capabilities/delivery/
  - docs/capabilities/documents/
  - docs/architecture/
  - docs/decisions/
  - docs/development/
  - docs/proposals/PROP-design-document-lifecycle/
  excludes:
  - packages/devkit-viewer/
task_kind: feature
workflow: sdd-proposal
depends_on:
- SPEC-design-document-foundation
- SPEC-domain-model-documents
- PROP-operations-documents
---

# [PROP-design-document-lifecycle] Documentation-layer authoring and reconciliation lifecycle

## 1. Background & Hypothesis

Maintained domain, design and operational views need clear create/update/split/retire decisions. Existing SDD
and adaptive-dev guidance already owns delivery lifecycle. Extend it only where the early examples reveal an
unhandled impact or discovery path, without creating parallel records or requiring every layer for every feature.

## 2. Technical Spike Questions

- **Q1**: When should an agent consult or maintain each role, and when is the existing authoritative source enough?
- **Q2**: Which current review and reconciliation mechanisms already cover entry documents and supporting files?
- **Q3**: How can the same document semantics work under SDD and adaptive-dev without imposing SDD records on the latter?

## 3. Proposed Design & Impact

- Use the foundation matrix and conventions delivered by domain and operations proposals. Provide concise
  routing guidance: read conditions, authoritative owner, affected statements and supporting-file dependencies.
- Reuse existing review, reconciliation and metadata. Add guidance or deterministic checks only for an observed
  failure; do not add a parallel registry, approval cycle or always-loaded inventory of all documents.
- Keep one entry document for small topics. Split independently readable or maintained detail when needed and
  state when a reader needs it. Non-indexed examples, diagrams and datasheets remain reachable through the entry.
- Review changes by their owned content: a rendering algorithm change may affect design without changing domain;
  a relationship policy change may affect domain explanation and capability enforcement without requiring ops.
- Keep generation source relationships explicit. Update or regenerate supporting artifacts from their source;
  retain historical measurements in materials and unresolved alternatives in proposal records.
- Integrate impact assessment into SDD and adaptive-dev at their existing boundaries. Preserve each approach's
  lifecycle and authority. Declare any necessary cross-feature dependency during Planning.

### Expected acceptance evidence

- Retained early examples demonstrate create, update, split and retirement routing. Every affected statement and
  support artifact has one source; unchanged layers need no edits or new records.
- Walkthroughs cover one multi-view change and one single-view change, including source-to-detail navigation and
  uncertainty/evidence handling. SDD reconciliation accounts for supporting files without IDs where affected.
- An adaptive-dev walkthrough uses the same roles without acquiring SDD envelopes or gates. Existing mechanisms
  that already satisfy these outcomes pass unchanged; test only changed runtime behavior where applicable.

## 4. Lifecycle & Retirement Criteria

Start after the three role conventions are delivered. Acceptance and handoff use the proposal gates. Retirement
requires verified authoring and maintenance paths using retained examples; new lifecycle mechanics are conditional
on a concrete gap. This supplies post-implementation integration evidence alongside the viewer proposal.
