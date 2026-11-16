---
reconcile_id: REC-formal-document-kinds
status: pending
targets:
  - file: docs/README.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
    resolution: modified
  - file: docs/decisions/2026-11/20261116-formal-role-document-identities.md
    resolution: modified
  - file: docs/designs/DESIGN-distribution-file-directory-replacement.md
    resolution: modified
  - file: docs/designs/DESIGN-distribution-transactions.md
    resolution: modified
  - file: docs/designs/distribution-transactions.md
    resolution: modified
  - file: docs/designs/distribution-transactions/file-directory-replacement.md
    resolution: modified
  - file: docs/domain/DOMAIN-bundle-selection-and-installation.md
    resolution: modified
  - file: docs/domain/DOMAIN-delivery-relationships.md
    resolution: modified
  - file: docs/domain/bundle-selection-and-installation.md
    resolution: modified
  - file: docs/domain/delivery-relationships.md
    resolution: modified
  - file: docs/materials/2026-11/20261116-formal-document-kinds/development-evidence.md
    resolution: modified
  - file: docs/operations/OPS-distribution-sync.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: docs/usecases/documents/UC-find-the-right-documents.md
    resolution: modified
  - file: docs/usecases/governance/UC-keep-the-living-spec-consistent.md
    resolution: modified
  - file: packages/devkit-docs/README.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/AGENTS.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/architecture-writing.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/design-writing.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/document-writing.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/domain-writing.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/operations-writing.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/code_entrypoints/guide.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/guide.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_summary/guide.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/id_convention/guide.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/spec_format/guide.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/README.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/design-template.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/design.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/domain.md
    resolution: modified
  - file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/operations.md
    resolution: modified
---

# Reconciliation: formal design, domain and operations core

## Contracts and ownership

`CAP-DOCS-document-model` owns the appended public Kinds, flat IDs, exact role metadata/status schema, related_*
lists, aliases, retirement, artifact exception and shipped asset inventory. Lookup/search/namespace capabilities
state the corresponding applicable current interfaces. `CAP-GOV-spec-rules` catalogs their structural checks,
including typed metadata opt-in on indexed materials, without claiming validation of freeform evidence prose.
`CAP-TRACE-code-entrypoints` §§1,3.1–3.3 covers optional DESIGN declaration/liveness/reverse lookup only; derivation
and apply sections remain unchanged for the required lifecycle phase.

`CAP-DOCS-documentation-ownership` retains one normative owner per responsibility. DOMAIN conceptual knowledge,
DESIGN implementation explanation/datasheets and OPS evidence routing are equally formal but do not inherit
behavioral/recovery permission authority. Its selected navigation imposes no reciprocal registry or reading order.
The new ADR traces current restatements and confirmation; the earlier accepted ADRs already have exact matching
partial pointers from handoff, so their rationale and historical evidence remain untouched. Architecture retains
structure and the existing documents→governance dependency direction; there is no docs→spec import or new edge.

## Current content and neutral source assets

All five exact canonical role nodes are active. The four former ID-free paths are removed and mapped in the
[development evidence](../../../docs/materials/2026-11/20261116-formal-document-kinds/development-evidence.md).
Existing capability/glossary ingress uses full IDs. Ordinary relative source/artifact destinations were checked
separately. Completed specs/materials retain their source-history coordinates and bytes; archived operations and
the immutable core contract remain unchanged. No path-shaped aliases or live ID-free redirects were introduced.
The use cases fold formal lookup/retirement/artifact and authoring/snapshot outcomes into their steps/extensions
and acceptance examples. No distribution or delivery guarantee transferred.

The docs source bundle owns eleven instructions and nine template files, including the compatibility pointer.
Source AGENTS, living-spec/architecture/document-writing, per-kind guidance, seed README, rule guides and package
README agree. Source sync alone wrote the tracked .devkit/installation.json receipt; ignored managed/local-render
files were never edited by hand. Three explicitly Host-authorized spec/adaptive consumer tests changed only docs
instruction/template inventories; no sibling production behavior changed.

## Entrypoints and verification

The unit's entrypoint derivation is reviewed before apply. Existing document-model runtime doorways and the migrated
DESIGN detail's transaction source anchor already identify the right reading starts. Reject broad source/test/bundle
candidate cross products for owner documents touched only for schema text/navigation; those paths would misleadingly
claim implementation ownership. No new derived entrypoint is applied. The existing DESIGN path is explicit and
validated by declaration/liveness/reverse tests; derive/apply consumer extension belongs to the lifecycle phase.

HIGH independent code review round1 found five defects; all were fixed with reproducing regression cases.
Round2 passed34 formal tests, snapshot symlink replacement and22 governance rules independently. Developer checks
on frozen9f4b9f70108178bc72a77b880b59726c10341fa8 passed2625 affected tests, docs-only installed-wheel E2E1,
lint and Pyright0. Reconciliation remains pending until its separate independent reviewer verifies the full reflection.
The evidence measures formal identity coverage0→5 from exact baseline bytes, not performance.

## Required dependent work

`PROP-design-document-lifecycle` owns required L1–L4 workflow/adaptive maintenance and derive/apply consumers;
`PROP-design-document-viewer` owns required V1–V4 rendering/public frontend/handbook behavior. Both accepted
proposal destinations exist. Core F1–F6 does not claim their evidence or milestone completion. No required core
criterion or known implementation defect is deferred.
