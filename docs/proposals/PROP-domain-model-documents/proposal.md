---
id: PROP-domain-model-documents
title: Domain-model documentation
summary: "Establishes maintained conceptual domain views with clear authoritative sources, reusing document discovery unless the early pilot demonstrates a gap."
status: reviewing
created_at: 2026-11-16
target_area: documents/
priority: high
size: L
planning_effort: high
dev_effort: medium
milestone: MS-documentation-system-evolution
boundaries:
  owns:
  - docs/ # Create only the two domain entries named in target-docs.md
  - docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
  - docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
  - docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
  - docs/steering/glossary.md
  - docs/decisions/
  - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md
  excludes:
  - packages/devkit-core/
  - packages/devkit-cli/
  - packages/devkit-mcp/
  - packages/devkit-viewer/
  - packages/devkit-spec/
task_kind: feature
workflow: sdd-proposal
depends_on:
- SPEC-design-document-foundation
---

# [PROP-domain-model-documents] Domain-model documentation

## 1. Background & Hypothesis

Domain documentation makes concepts, identity, relationships and lifecycles understandable together. The early
pilot identifies useful views without assuming that every conceptual rule should move out of its existing owner.
The domain role is retained whether it needs a new indexed kind or existing document facilities are sufficient.

## 2. Technical Spike Questions

- **Q1**: What document boundaries make the pilot's concepts and relationships understandable without becoming a
  class catalog, database schema or implementation-algorithm reference?
- **Q2**: Which definitions already have authoritative owners, and does a selected invariant justify an explicit
  ownership transfer rather than a reference/composition view?
- **Q3**: Which location, identity and tooling choices meet discovery needs using the smallest supported representation?

## 3. Proposed Design & Impact

Recommend linked ID-free `docs/domain/<slug>.md` relationship entries, with analogous `domain/` under a registered
package docs root. Location, identity and tooling are independent choices: the domain home is selected; indexed
identity and runtime changes are not required by the agreed outcomes. `PADR-linked-domain-relationship-views`
records alternatives and the conditional discovery evidence. This direction awaits the Host's plan-accept gate.

Maintain exactly two initial entries: `docs/domain/delivery-relationships.md` and
`docs/domain/bundle-selection-and-installation.md`. Each gives its reader question, useful relationship overview,
authority boundary and next useful owner/detail. A small entry needs no hierarchy or separate detail file.
`target-docs.md` is the canonical exact implementation scope and acceptance blueprint.

The delivery view explains proposal/spec identity and the distinct meanings of milestone membership, unit
prerequisite and provenance. The distribution view adapts the supplied pilot into availability, requested
selection, bundle/asset identity, projection destinations and recorded receipt evidence. They are conceptual
compositions, neither class catalogs nor schema/algorithm references. Glossary term definitions remain concise.
No normative statement transfers: validity, relation grammar, handoff transformations and receipt/projection
contracts retain their existing owners. Concise explanatory summaries cite the owner rather than creating an
independent obligation. Domain supplies a conceptual basis alongside structure and contracts without an authoring DAG.

Selected question-specific ordinary links from the lifecycle and transaction capabilities, plus glossary links,
provide discovery. Entries cite indexed owners by full ID and ID-free destinations by ordinary Markdown links.
Existing search may find an indexed owner; it does not index the domain entry. No all-pairs links, reciprocal
registry, whole-layer prerequisites or fixed hop count is required.

Extend the existing shared ownership capability only with domain representation/discovery clauses. Add concise
consumer-generic guidance to the docs bundle's source living-spec instruction; it implements that shared contract
without a second responsibility matrix or repository IDs. No new template, Kind, ID grammar, namespace setting,
relation, runtime, editor, viewer or production feature edge is selected. Shared source implementation must be
scheduled sequentially by the Host after collecting overlapping future scope with the operations proposal.

### Planning decisions and evidence

- Planning effort remains high as assigned; content-only Development uses medium effort with independent review.
- `materials/options-and-evidence.md` compares viable representations and records evidence limits. The supplied
  domain pilot proves useful explanation, not unsupplied-entry discovery. Foundation proves DESIGN routes only.
- No accepted ADR is superseded. The new home extends the deferred domain decision in the Foundation.
- If independent global/package routes fail, first correct entry wording or selected links. If the agreed outcome
  still cannot be met, return the named unmet outcome to the Host for scope review before runtime work.
- No unresolved business question remains within the supplied goal and constraints. Direction approval and
  Development handoff remain the Host's separate gates.

## 4. Lifecycle & Retirement Criteria

Start after completed `SPEC-design-document-foundation`. Retirement requires the maintained conceptual entries,
unique authority, source guidance and independently demonstrated domain discovery in both global and registered
package contexts. Later lifecycle/viewer proposals may reuse the entries; their work is excluded here.
