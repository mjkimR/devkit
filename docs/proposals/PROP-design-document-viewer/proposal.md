---
id: PROP-design-document-viewer
title: First-class formal documentation in the repository viewer
summary: "Provides complete navigation, identity, references, metadata, artifact access and packaged viewer support for formal design, domain and operations kinds."
status: draft
created_at: 2026-11-16
target_area: viewer/
priority: high
size: L
planning_effort: high
dev_effort: high
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
  - scripts/handbook.py
  - tools/devkit-dev/tests/integration/test_handbook_script.py
  excludes:
  - packages/devkit-docs/src/devkit_docs/bundles/
  - packages/devkit-spec/
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-formal-document-kinds
---

# [PROP-design-document-viewer] First-class formal documentation in the repository viewer

## 1. Background & Hypothesis

`PROP-formal-document-kinds` establishes formal design, domain and operations identities and core contracts.
The repository viewer must expose these as first-class kinds throughout existing relevant supported surfaces.
Generic backend loading or Markdown rendering alone does not prove frontend navigation, ID recognition,
metadata, reference graph or packaged-static support.

The core proposal replaces the earlier operations prerequisite. `SPEC-design-document-foundation` and
`SPEC-domain-model-documents` remain historical context. This required phase and
`PROP-design-document-lifecycle` complete integration under `MS-documentation-system-evolution`.

## 2. Technical Spike Questions

- **Q1**: Which kind/prefix allowlists, group ordering and reference recognizers need extension in the frontend,
  public frontend library and static generation? Which backend paths already work and need verification?
- **Q2**: How should per-kind metadata and applicable relationships appear without assuming only
  related_capabilities/related_usecases or inventing a competing viewer schema?
- **Q3**: How do global and registered namespaces expose formal nodes, independent details and supporting
  artifacts, including empty, missing and unsupported states consistent with existing behavior?
- **Q4**: How must `scripts/handbook.py` recognize prefixes and locate sources? What deliberate inclusion policy
  governs handbook pages, separately from support for formal identity and source lookup?

## 3. Proposed Design & Impact

- Consume all three core Kind definitions and canonical schemas. Provide explicit navigation/group labels and
  ordering, list/search participation, IDs and deep links for global and registered namespace documents.
- Audit and support prose ID links, statement-level supersession recognition, applicable metadata and reference
  graph relationships. Extend hardcoded prefix/group/relationship lists where needed. Preserve current/provenance
  distinctions and alias behavior supplied by the document model.
- Support contract-to-design-to-detail/artifact, concept-to-contract and symptom-to-action-owner routes with real
  migrated documents. Users must reach the formal node and its supporting files without guessing filesystem paths.
- Verify rendering, relative links and artifact access for supported Markdown, examples, diagrams, CSV and images.
  Existing preview/download/link behavior governs unsupported formats. Empty lists, missing documents or artifacts
  and unresolved references use consistent existing states rather than disappearing silently.
- Cover viewer backend APIs, public frontend libraries, static generation, generated assets and package contents.
  A generic implementation may remain unchanged only with complete new-kind test and walkthrough proof.
- Extend `scripts/handbook.py` prefix/ID recognition and source lookup policy where applicable. State handbook
  inclusion/exclusion deliberately; an unrecognized prefix must not silently omit a supported source document.
  Update the owning reference/contract and focused script tests for the chosen inclusion policy.
- Draft screens before code and perform UX review when interactions change. Reconcile use cases and UX contracts
  and their object register. A shared renderer/navigation can serve multiple kinds; no custom editor per kind or
  proprietary-format editing engine is required.
- Declare any required cross-feature dependencies in Planning. Coordinate core schema changes with the core
  owner and avoid viewer-only identity or relation rules.

### Expected acceptance evidence

- **V1 — Kind parity**: Each real kind has navigation/groups, ID/deep-link access, prose references, applicable
  metadata, incoming/outgoing reference graph and statement supersession recognition. Positive and negative tests
  cover all prefix recognizers and relation handling, with existing-kind regressions.
- **V2 — Context and artifacts**: Global and registered namespace walkthroughs reach migrated entries, canonical
  details and supporting artifacts. Tests cover rendering, empty/missing/unresolved and unsupported-format
  behavior. Owner boundaries and existing recovery permissions remain unchanged.
- **V3 — Public and packaged output**: Backend/API and frontend-library tests cover formal kinds. Frontend lint,
  check, tests, packaging and build pass; generated-static consistency checks and packaged-asset inspection prove
  shipped output matches source. Run the repository's declared FRONTEND_CHECK command and required viewer checks.
- **V4 — Handbook and UX**: Handbook source recognition/lookup handles the three prefixes under an explicit
  inclusion policy, with focused regression evidence. Changed interactions have drafted screens, UX review and
  reconciled use case/UX contracts. Unchanged generic paths still have complete new-kind verification.

## 4. Lifecycle & Retirement Criteria

Plan against the required formal core contract and consume its delivered schemas before dependent implementation
verification. This remains one L feature proposal. Acceptance and handoff follow existing gates. Retirement
requires V1–V4, public/static package verification and complete support evidence for every formal kind.
Core loading, generic rendering or a small/no-code diff alone cannot establish completion. The milestone also
requires lifecycle integration and preserves its planned status until completion is reviewed.
