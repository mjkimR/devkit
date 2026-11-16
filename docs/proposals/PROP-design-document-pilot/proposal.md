---
id: PROP-design-document-pilot
title: Pilot implementation-design separation on existing documents
summary: "Applies design bundles to a bounded sample of existing documents and verifies ownership boundaries, preserved contracts and artifact discoverability."
status: draft
created_at: 2026-11-16
target_area: documents/
priority: high
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-implementation-design-documents
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
- PROP-design-document-lifecycle
- PROP-design-document-viewer
---

# [PROP-design-document-pilot] Pilot implementation-design separation on existing documents

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

## 4. Lifecycle & Retirement Criteria

Start after the foundation, authoring lifecycle and viewer support are delivered. Acceptance and handoff use the
proposal gates. Retirement requires a verified bounded pilot and explicit destinations for concrete follow-up;
this proposal does not migrate all existing documents.
