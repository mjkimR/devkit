---
id: PROP-design-document-viewer
title: Documentation-layer navigation in the repository viewer
summary: "Exposes domain models, design bundles and operational guidance with their contract links and supporting artifacts in the repository viewer."
status: draft
created_at: 2026-11-16
target_area: viewer/
priority: high
size: L
planning_effort: medium
dev_effort: medium
milestone: MS-documentation-system-evolution
boundaries:
  owns:
  - packages/devkit-viewer/
  - docs/capabilities/viewer/
  - docs/usecases/
  - docs/ux/
  - docs/architecture/
  - docs/decisions/
  - docs/development/reference/
  - docs/proposals/PROP-design-document-viewer/
  excludes:
  - packages/devkit-docs/src/devkit_docs/bundles/
  - packages/devkit-spec/
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-design-document-foundation
- PROP-domain-model-documents
- PROP-operations-documents
---


# [PROP-design-document-viewer] Documentation-layer navigation in the repository viewer

## 1. Background & Hypothesis

Design bundles can group details and non-Markdown artifacts, but a document list alone does not show their
relationship to contracts or explain which supporting file a reader needs. The repository viewer should expose
that structure without treating designs as replacements for capability, architecture or UX documents.

## 2. Technical Spike Questions

- **Q1**: How should design entries appear in existing browsing and detail views, and how should related contracts
  and independently indexed details be distinguished from supporting files?
- **Q2**: Which artifact types can use existing viewing or download behavior, and how should unsupported formats,
  missing files and stale references be represented?

## 3. Proposed Design & Impact

- Consume the identity, ownership relationships and bundle conventions delivered by
  `PROP-design-document-foundation`; avoid defining a competing viewer-only schema.
- Expose navigation from relevant contracts to designs, from a design to its contracts, and from its entry
  document to the details, examples, diagrams and datasheets it cites.
- Reuse existing artifact handling. Provide usable links or downloads for unsupported formats rather than adding
  spreadsheet editing or proprietary-format rendering.
- Draft the affected screens and interactions before code, within `CAP-VIEW-repository-viewer` and the existing
  use case and UX document structure. Keep the design's implementation content out of those UX contracts.

### Expected acceptance evidence

- A reader can navigate a related contract, a design entry, a separate detail and a datasheet without guessing
  filesystem paths. Existing document kinds retain their navigation and labels.
- Missing artifacts and unsupported formats have explicit usable states; the implementation passes the viewer's
  required frontend checks and focused backend checks for changed artifact/navigation behavior.

### Expanded documentation-layer scope

- Expose domain models and operational guidance alongside designs using their delivered identities and
  relationships. Keep conceptual relationships, implementation details and operational procedures distinguishable.
- Verify navigation from a domain concept to its contracts and designs, and from an operational symptom to the
  applicable procedure or reference. Support non-indexed artifacts through the chosen entry documents.
- Reuse generic document navigation where possible. Do not create a separate schema or document editor per layer;
  apply required viewer frontend checks to changed surfaces.

## 4. Lifecycle & Retirement Criteria

Start after the foundation, domain-model and operations conventions are delivered. Acceptance and handoff use the proposal gates. Retirement requires
verified navigation and matching UX documentation. Repository-wide content migration is outside this proposal.
