---
id: PROP-domain-model-documents
title: Domain-model documentation
summary: "Establishes maintained conceptual domain views with clear authoritative sources, reusing document discovery unless the early pilot demonstrates a gap."
status: draft
created_at: 2026-11-16
target_area: documents/
priority: high
size: L
planning_effort: high
dev_effort: high
milestone: MS-documentation-system-evolution
boundaries:
  owns:
  - packages/devkit-docs/
  - packages/devkit-core/
  - packages/devkit-cli/
  - packages/devkit-mcp/
  - docs/capabilities/documents/
  - docs/architecture/
  - docs/decisions/
  - docs/steering/
  - docs/development/reference/
  - docs/proposals/PROP-domain-model-documents/
  excludes:
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

- Apply `SPEC-design-document-foundation`'s matrix and early content evidence. Choose the domain home during
  Planning; `docs/domain/` is a candidate. Keep readable entry documents and split details only where useful.
- Default to an integrated conceptual view citing existing authoritative validity and transformation contracts.
  Clarify term usage and relationship meaning without creating an independent copy of the same normative fact.
- Permit explicit transfer of selected definitions or invariants when it improves ownership. Demonstrate one
  complete transfer first: identify the old owner, replace its authoritative restatement with a reference, and
  retain observable enforcement behavior in the appropriate capability. Broad normative migration is not a default.
- Use milestone/proposal/spec relationships to distinguish membership, prerequisite and provenance, and
  bundle/asset/projection relationships to distinguish conceptual identity from deployed file paths.
- Link schemas, algorithms and storage mappings to their existing contract or design owners. Keep the glossary
  concise and avoid duplicating full definitions there and in the domain model.
- Deliver the chosen authoring convention and minimal representation. Decide location, indexed kind/ID and
  tooling independently using pilot evidence. Reuse lookup/search/reference and namespace support where adequate;
  add runtime behavior only for a named unmet need, with focused tests and declared feature edges if required.
- Leave cross-layer lifecycle and viewer integration to their proposals. Their completion may demonstrate reuse
  of existing facilities; no dedicated domain editor or new classification platform is assumed.

### Expected acceptance evidence

- The selected examples explain identity, relationships and lifecycles without depending on Python or DB layout.
  Each statement's normative owner is identifiable; glossary and capability references reach the correct source.
- A milestone-membership change walkthrough distinguishes domain explanation from relation validity and handoff
  behavior. No unchanged fact acquires two authoritative owners under different labels.
- The representation decision names the early pilot evidence. Agreed entry and reference paths work in global
  and package namespaces; runtime tests cover actual changes and walkthroughs cover reused behavior.

## 4. Lifecycle & Retirement Criteria

Start after the common foundation. Planning settles representation and any selected ownership transfer;
acceptance and handoff use the proposal gates. Retirement requires usable maintained domain documentation and
verified discovery, not a mandatory new kind or broad migration. Later integration checks use the retained examples.
