---
id: PROP-design-document-pilot
title: Pilot documentation ownership across domain, design and operations
summary: "Validates domain-model, design and operations documentation on bounded devkit topics, preserving authoritative ownership and testing discovery across the layers."
status: draft
created_at: 2026-11-16
target_area: documents/
priority: high
size: L
planning_effort: medium
dev_effort: medium
milestone: MS-documentation-system-evolution
boundaries:
  owns:
  - docs/
  - packages/devkit-docs/tests/
  excludes:
  - packages/devkit-viewer/
  - packages/devkit-spec/src/
  - packages/devkit-core/
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-design-document-foundation
- PROP-domain-model-documents
- PROP-operations-documents
- PROP-design-document-lifecycle
- PROP-design-document-viewer
---


# [PROP-design-document-pilot] Pilot documentation ownership across domain, design and operations

## 1. Background & Hypothesis

A new design layer needs evidence that authors can separate real documents without losing contracts or copying
content into another directory. A bounded pilot should test ownership clarity and navigation, rather than merely
reducing capability line counts.

## 2. Technical Spike Questions

- **Q1**: Which existing documents contain a cohesive current implementation design that is not already correctly
  owned by architecture, UX or a reference? `CAP-DIST-sync-and-transactions` is a candidate for inspection, not an
  instruction to relocate all its detailed content.
- **Q2**: Which representative example and datasheet can validate the split without inventing data or converting
  historical measurements into current requirements?
- **Q3**: Can an unfamiliar agent locate the governing contract, current design and needed supporting file through
  the documented CLI and viewer paths, with one authoritative owner for each statement?

## 3. Proposed Design & Impact

- Select and bound one or two existing design topics during Planning, applying the foundation's ownership matrix.
  Preserve architecture, UX, reference and contract content that already has the correct owner.
- Migrate only the selected current implementation design. Group its actual examples, diagrams or datasheets
  where justified, and repair links from source documents without duplicating their authoritative statements.
- If an existing datasource is unsuitable, use an explicitly illustrative fixture to verify datasheet support;
  never fabricate a current product requirement or relabel historical evidence as a maintained design.
- Verify discovery from capability or architecture to design entry and then detail/artifact through the CLI and
  viewer. Review preserved contract information, ambiguous ownership and maintenance steps alongside navigation.
- Record the pilot's evidence in materials. Put concrete remaining work in feedback or proposals without making
  repository-wide migration a condition for this pilot.

### Expected acceptance evidence

- A before/after ownership comparison accounts for every moved statement and confirms no required behavior was
  dropped, silently changed or duplicated as an authoritative rule.
- The retained entry documents identify the purpose of each split file and link related contracts. Document rules
  and link checks pass; representative discovery and viewer paths reach the intended artifacts.
- The pilot demonstrates a separate detail, example and datasheet path using real retained content or an explicitly
  illustrative fixture, and reports ownership ambiguities rather than hiding them behind shorter documents.

### Expanded documentation-layer scope

- Cover domain-model candidates for delivery (proposal/spec/milestone/decision relationships) and distribution
  (package/bundle/asset/preset/projection/override/receipt relationships). Select a bounded representative scope
  during Planning rather than require a complete repository model.
- Include a current implementation-design example with split supporting artifacts, and an operational diagnosis
  and recovery example such as interrupted synchronization or receipt mismatch. Verify actual supported commands;
  do not infer recovery permission or execute destructive procedures merely to author documentation.
- Account for the authoritative home of each extracted concept, rule and procedure. Preserve contract limits in
  capabilities, choice rationale in ADRs and historical evidence in materials. Link executable playbooks instead
  of maintaining duplicate recovery procedures.
- Demonstrate concept-to-contract-to-design navigation and symptom-to-diagnosis-to-recovery-to-normal-state
  navigation. Report gaps in the role boundaries as findings, not just changes in document length.

## 4. Lifecycle & Retirement Criteria

Start after foundation, domain-model, operations, authoring lifecycle and viewer support are delivered. Acceptance and handoff use the
proposal gates. Retirement requires a verified bounded pilot and explicit destinations for concrete follow-up;
this proposal does not migrate all existing documents.
