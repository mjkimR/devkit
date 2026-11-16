---
id: PROP-design-document-lifecycle
title: Documentation-layer authoring and reconciliation lifecycle
summary: "Integrates domain models, implementation designs and operational guidance into authoring, review and reconciliation with clear document ownership."
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
- PROP-design-document-foundation
- PROP-domain-model-documents
- PROP-operations-documents
---


# [PROP-design-document-lifecycle] Documentation-layer authoring and reconciliation lifecycle

## 1. Background & Hypothesis

A document-system kind does not tell an agent when to create a design, how to split its details or which files
must change with an implementation. Without explicit authoring and reconciliation guidance, the design layer
can duplicate existing contracts or become stale reference material.

## 2. Technical Spike Questions

- **Q1**: At what point should an agent consult or draft a current design, and when is an existing capability,
  architecture, UX document, reference or guide sufficient?
- **Q2**: How do draft designs and supporting artifacts become maintained current documents under SDD and
  adaptive-dev without imposing one approach's approval lifecycle on the other?
- **Q3**: How do review and reconciliation cover split details, examples, datasheets and generated artifacts while
  preserving their authoritative sources and avoiding unnecessary context loading?

## 3. Proposed Design & Impact

- Apply the ownership matrix and bundle model from `PROP-design-document-foundation` in source-bundle templates
  and instructions. Teach content routing and cross-referencing before giving a folder layout.
- Make small designs single-file by default. Explain when an independently readable or maintained detail needs
  separation, how the entry document guides readers, and when a shared design should remain independently owned.
- Cover current implementation strategies and detailed specifications. Route general coding, testing and delivery
  procedures to existing guides or playbooks instead of making design a process-methodology repository.
- Integrate design impact into implementation review and Living Spec reconciliation, including supporting files
  with no document ID. Specify preservation or regeneration of generated artifacts from their existing source.
- Keep historical research in materials and choice rationale in ADRs. Define how a draft design becomes current
  without carrying temporary plans or unresolved alternatives into the retained implementation design.
- Update the SDD and adaptive-dev guidance at their existing ownership boundaries. Document any new feature
  dependency during Planning instead of adding a cross-package lifecycle import implicitly.

### Expected acceptance evidence

- Authoring examples consistently route ambiguous content to the same owner as the foundation matrix.
- Guidance covers create, update, split and retirement of a design and its supporting artifacts, with no mandatory
  empty hierarchy and no duplicate source of truth.
- A reviewed implementation change identifies affected design details and supporting files in reconciliation;
  an adaptive-dev example keeps the same document semantics without acquiring SDD records or approval gates.

### Expanded documentation-layer scope

- Apply the foundation ownership matrix to domain models, designs and operations, using the conventions delivered
  by `PROP-domain-model-documents` and `PROP-operations-documents`. Preserve domain meaning, behavioral contracts,
  implementation mechanisms and executable procedures in their respective authoritative sources.
- Cover changes to concepts and relationships as well as runtime behavior. Review whether affected domain models,
  design details and diagnosis/recovery instructions need updates; supporting files without IDs remain visible
  in reconciliation. Keep the SDD and adaptive-dev lifecycle distinction.
- Demonstrate one change that affects all three views and a change that affects only one. Do not require touching
  every layer for every feature or copying the same statement into multiple documents.

## 4. Lifecycle & Retirement Criteria

Start after the foundation, domain-model and operations conventions are delivered. Acceptance and handoff use the proposal gates.
Retirement requires deployed authoring guidance and verified review/reconciliation behavior, not pilot migration
or viewer implementation.
