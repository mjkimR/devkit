---
id: PROP-design-document-lifecycle
title: Formal documentation authoring and reconciliation lifecycle
summary: "Integrates complete authoring, Planning, review, reconciliation and maintenance for formal design, domain and operations kinds under SDD and adaptive-dev."
status: accepted
created_at: 2026-11-16
target_area: delivery/
priority: high
size: L
planning_effort: high
dev_effort: high
milestone: MS-documentation-system-evolution
boundaries:
  owns:
  - packages/devkit-spec/
  - packages/devkit-adaptive/
  - docs/capabilities/delivery/
  - docs/capabilities/traceability/
  - docs/usecases/governance/
  - docs/usecases/delivery/
  - docs/usecases/harness/
  - docs/decisions/
  - docs/proposals/PROP-design-document-lifecycle/
  excludes:
  - packages/devkit-docs/
  - packages/devkit-viewer/
task_kind: feature
workflow: sdd-proposal
depends_on:
- SPEC-formal-document-kinds
---

# [PROP-design-document-lifecycle] Formal documentation authoring and reconciliation lifecycle

## 1. Background & Hypothesis

`SPEC-formal-document-kinds` supplies formal identity, core governance, neutral authoring assets and migration.
Delivery integration must treat design, domain and operations as first-class impact targets throughout their
lifecycle. Existing SDD and adaptive-dev mechanisms own delivery authority; extend their concrete integration
points so every supported formal kind participates completely without an unrelated workflow engine.

The core proposal replaces the earlier operations prerequisite. `SPEC-design-document-foundation` and
`SPEC-domain-model-documents` are historical context, not substitutes for the formal core prerequisite.
This phase and `PROP-design-document-viewer` are required to complete `MS-documentation-system-evolution`.

## 2. Technical Spike Questions

- **Q1**: Which Planning, review and reconciliation boundaries must consult each formal kind, and how does impact
  assessment select affected statements without requiring unaffected layers for every change?
- **Q2**: How do create, update, split, rename and retire preserve canonical identity, aliases, references and
  source/detail/artifact relationships under the core schema?
- **Q3**: Which kinds and role-specific rows permit source entrypoints? How do spec-plan, spec-sync and
  spec-entrypoints consume that policy without extending CAP/UC reciprocity to every kind?
- **Q4**: How do proposal target-docs scaffolds, brownfield adoption and SDD baseline coverage expose the formal
  roles? How does adaptive-dev maintain the same documents without implicit SDD Units, envelopes or gates?

## 3. Proposed Design & Impact

- Use the formal core schemas and Kind definitions. Document when an agent reads or creates each role, identifies
  its authoritative owner, and selects affected formal documents as required impact/reconciliation targets.
  Preserve concise question-directed traversal and useful independent details.
- Cover create, update, split, rename and retire explicitly. Define how ID/alias/reference maintenance and
  applicable supersession work for each kind, including independently identified details and parent-owned
  supporting Markdown or non-Markdown artifacts. Keep artifact regeneration tied to its actual source.
- Update `packages/devkit-spec` source assets for spec-plan, spec-sync and spec-entrypoints, bundle AGENTS
  guidance and pointers. Update proposal `target-docs.md` scaffold sections in
  `features/proposals/usecases/scaffold.py` so Planning records prospective formal docs, migrations and impacts.
  Update brownfield-adoption and sdd-baseline guidance/coverage for these canonical kinds.
- Extend Planning, implementation review and reconciliation checks at their existing boundaries. Affected formal
  documents must be accounted for alongside existing contracts. A mechanism-only change may affect design while
  leaving domain/operations unchanged; an explicit applicability assessment records that result without empty work.
- Update adaptive-dev `references/documents.md`, `roles/documenter.md` and related source pointers so the same
  authoring and maintenance paths work without SDD change records. Docs bundle neutral guidance remains neutral.
- Coordinate neutral docs asset adjustments with the core owner. Keep source assets, seed/pointers, guides and
  exact distribution/integration inventories consistent. Declare cross-feature dependencies in Planning.
- Preserve materials as historical evidence and decisions under the selected approach. Do not create a parallel
  registry, fixed whole-layer reading order or additional approval/recovery engine.

### Planning decisions

1. Extend existing delivery boundaries, consuming the shared ownership and Kind policy from
   `SPEC-formal-document-kinds`. The comparison and source evidence are in
   [integration contract](materials/integration-contract.md); the lasting choice is
   `PADR-formal-document-delivery-integration`. No parallel applicability registry or workflow engine is added.
2. Planning, implementation review and reconciliation assess all three formal responsibilities against the actual
   change. Record affected IDs, source evidence and required actions in existing proposal/plan/reconcile or review
   bodies. Record a bounded reason for an unaffected responsibility; do not manufacture empty documents or edits.
3. Canonical IDs, aliases, relation fields, detail identity, status and entrypoint eligibility are supplied by the
   core. Delivery consumes them; it does not extend CAP↔UC reciprocity, doorway restrictions or ADR supersession
   automatically to formal roles. The selected interface is pinned in [core interface](materials/core-interface-pin.md); delivered runtime/assets
   and their evidence are required before Development handoff.
4. The lifecycle phase owns spec/adaptive consumers and `CAP-TRACE-code-entrypoints` derivation/review/apply
   integration. Core owns neutral docs assets, canonical migration and shared schema/policy contracts. Viewer owns
   presentation and handbook. These are required milestone owners; no phase may claim the others' completion.
5. This remains one L spec: one integration contract, two existing delivery approaches, one runtime scaffold and
   reused entrypoint flow. No independent engine or migration platform is introduced. Development effort remains
   high because shipped agent-facing guidance and cross-package semantics change.

### Expected acceptance evidence

`PROP-design-document-lifecycle-target` and [verification matrix](materials/integration-contract.md#5-verification-matrix)
name exact source/test owners and the required per-kind scenario cross-product. Planning records no passing code tests.

- **L1 — Authoring and maintenance**: All three kinds have verified create/update/split/rename/reclassify/retire paths using
  the formal schemas. Real migrated documents and supporting artifacts retain correct IDs, aliases, references,
  owner boundaries and source agreement. Lifecycle applicability is explicit for every kind.
- **L2 — SDD integration**: A multi-role change and a single-role change traverse proposal target-docs, Planning,
  review and reconciliation. Required affected documents appear in impact targets; unaffected layers need no
  edits. Tests verify scaffold sections and changed workflow/runtime integration, including source-entrypoint
  policy and appropriate spec-entrypoints rows.
- **L3 — Adoption and adaptive-dev**: Brownfield adoption and SDD baseline account for formal role documents.
  An adaptive-dev walkthrough maintains the same kinds without acquiring SDD Units, envelopes or approvals.
  Applicable integration tests verify documenter guidance and source-asset delivery.
- **L4 — Distribution and regression**: Source guidance, seed/pointers and installed assets agree. Sync,
  `get-context` and affected bundle/integration tests pass with existing lifecycle and CAP/UC behavior preserved.
  Reused mechanisms have complete new-kind evidence; their existence alone does not establish support.

## 4. Lifecycle & Retirement Criteria

Start Planning against the required formal core contract; handoff ordering must make its delivered schemas
available before integration depends on them. This remains one L feature proposal covering delivery integration.
Acceptance and handoff follow existing gates. Retirement requires L1–L4, current contract reconciliation and
verified SDD/adaptive authoring and maintenance paths for every formal kind. Core completion alone does not retire
this phase or complete the milestone.


### Dependency readiness

The selected future core interface is pinned at 504e2e12006ab3e2aad2b8ce470607646ad4c4ac with verified artifact hash
in [core interface](materials/core-interface-pin.md). It settles schema consumption for Planning. Handoff still
requires delivered core definitions, templates, writing instructions, migration ledger and entrypoint policy at an
identified implementation revision; the selected contract is not runtime evidence.
L1–L4 remain mandatory if any interface value changes. No unverified generic path counts as support.
