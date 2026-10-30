---
id: PROP-rename-incubation-to-adaptive-dev
title: Rename incubation to adaptive-dev and disambiguate proposal terms
summary: "Rename the incubation bundle and development approach to adaptive-dev and rename the SDD proposal-incubation term, so each development concept has one unambiguous name. The approach value and bundle name are consumer-facing contracts, so the change settles their migration path."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: high
size: L
planning_effort: medium
dev_effort: high
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/features/
    - packages/devkit-dist/tests/
    - packages/devkit-dist/README.md
    - packages/devkit-spec/src/devkit_spec/
    - packages/devkit-spec/tests/
    - packages/devkit-spec/README.md
    - packages/devkit/src/devkit_agt/features/integration/
    - packages/devkit/tests/
    - packages/devkit/README.md
    - packages/devkit-catalog/src/devkit_catalog/
    - packages/devkit-catalog/tests/
    - packages/devkit-catalog/README.md
    - packages/devkit-catalog/pyproject.toml
    - packages/devkit-docs/tests/
    - docs/capabilities/
    - docs/usecases/
    - docs/architecture/
    - docs/development/
    - docs/README.md
    - docs/proposals/README.md
    - docs/decisions/
    - docs/steering/glossary.md
    - docs/steering/glossary.yaml
    - guides/
    - tests/e2e/smoke.sh
    - AGENTS.md
    - .devkit/installation.json
  excludes:
    - .devkit/managed/
    - handbook/
    - specs/
    - docs/materials/
    - docs/roadmap/_archive/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-rename-incubation-to-adaptive-dev] Rename incubation to adaptive-dev and disambiguate proposal terms

## 1. Background & Hypothesis

"Incubation" names two unrelated concepts in this repository:

- The SDD proposal lifecycle: `CAP-DLV-proposal-incubation` and `UC-incubate-and-hand-off-a-proposal` (draft,
  Planning, acceptance and handoff of a proposal).
- The development approach that iterates without per-change SDD records: `[development] approach = "incubation"`,
  the `incubation` catalog bundle, `/incubate`, `get-context incubation` and `.devkit/incubation.md`
  (`CAP-DLV-idea-incubation`, `CAP-DLV-incubation-sdd-baseline`).

With both installed, a request to "incubate" an idea does not identify which one the user means.
The hypothesis: one distinct name per concept removes the ambiguity at every entry, setting and document.

### Settled direction

- The approach and bundle become `adaptive-dev`: `[development] approach = "adaptive-dev"` beside `"sdd"`, and the
  catalog bundle `adaptive-dev`. The name pairs with spec-driven development as "adaptive development".
- Rejected names: `incubation` and `project-incubation` keep the ambiguous word; `project-bootstrap` reads as a
  temporary phase, while the approach may remain a project's approach indefinitely (`CAP-DLV-idea-incubation`).
- The SDD proposal term is renamed as well, so "incubation" names no current concept.
- The approach keeps its contract: a product may stay in it, and SDD adoption stays the explicit `sdd-baseline`
  procedure.

## 2. Technical Spike Questions

Planning answers each question below; `MAT-incubation-rename-inventory` lists every affected file and
`envelopes/scout-01.yaml` holds the migration evidence. "Open" marks an answer the user's decision completes.

- **Q1 Approach migration** (open: q1): no deprecation-notice mechanism exists, and `CAP-DIST-sync-and-transactions`
  requires `DEVELOPMENT_CONFIG_INVALID` for any unknown value. Recommended: rename in place in one minor release, as
  the `devkit:run` to `harness:run` precedent did. `"incubation"` is refused with `DEVELOPMENT_CONFIG_INVALID`
  (exit 2), and its `fix` names the exact edit: `Rename [development] approach = "incubation" to "adaptive-dev"`.
  No release window is kept.
- **Q2 Bundle migration** (open: q1): no bundle alias exists, a shim bundle cannot reuse the entry-point name, and
  sync refuses a selected bundle that no package provides (`SELECTION_INVALID`, fix `devkit remove incubation`).
  Recommended: the install guides document the steps `devkit remove incubation`, then `devkit add adaptive-dev`. Sync
  removes the unedited `incubation` copies and projections and reports edited ones as `ORPHAN_LEFT`. An override
  directory `.devkit/overrides/incubation/` stays (`OVERRIDE_RETAINED`); the guide names its manual move.
- **Q3 Context file**: the file becomes `.devkit/adaptive-dev.md`. Only the entry's guidance reads or writes it, and
  sync never touches it. When `.devkit/adaptive-dev.md` is absent and `.devkit/incubation.md` exists, the entry
  renames the file (`git mv` when tracked) before its first update and reports the move. The file stays
  project-owned and never seeded (`CAP-DLV-idea-incubation` rules 14 and 15 keep their meaning).
- **Q4 Entry name** (open: q3): recommended `/adaptive-dev`, matching the bundle name as `/spec` matches `spec`.
  The pointer guidance becomes `adaptive-dev-pointer`. `incubation-researcher` becomes `product-researcher` if it
  stays in this bundle after `PROP-deep-research-bundle` settles its owner.
- **Q5 SDD term** (open: q2): the spec bundle already calls this activity Planning (`planning.md`, `plan-<slug>`,
  `plan-intent`, `plan-accept`, `planning-worker`, `planning_effort`). Recommended term "proposal Planning":
  `CAP-DLV-proposal-incubation` becomes CAP-DLV-proposal-planning ("Proposal Planning and Handoff"), and
  `UC-incubate-and-hand-off-a-proposal` becomes UC-plan-and-hand-off-a-proposal. The `devkit spec proposal` help
  text ("Incubate proposals ...") and prose in `ARCH-04-1-ecosystem-boundaries`, `ARCH-04-2-delivery-policy`,
  `docs/development/workflow.md`, `docs/README.md` and `docs/proposals/README.md` use the same term.
- **Q6 Code identifiers**: `development_approach` in `devkit_dist.features.project` is the only parser; its
  `Literal`, check, message and `fix` change. Readers that compare the literal change from `"incubation"` to
  `"adaptive-dev"`: `devkit_spec.features.delivery.usecases.{attach,integration,cleanup}`,
  `devkit_spec.features.governance.services.applicability`, `devkit_spec.features.governance.usecases.hygiene`,
  `devkit_spec.features.policy.services.lifecycle` and `devkit_agt.features.integration.usecases.project`. Output
  text that names the approach changes with it: the readiness evidence `omitted:incubation` becomes
  `omitted:adaptive-dev`, plus the omission reason and refusal messages. The codes `DEVELOPMENT_CONFIG_INVALID` and
  `SDD_LIFECYCLE_INACTIVE` keep their names. The package `devkit_catalog.incubation` becomes
  `devkit_catalog.adaptive_dev`, and its tests move to `tests/{integration,e2e}/bundles/` names using
  `adaptive_dev`. Test fixtures named after the SDD term (`INCUBATED`, the `incubate` workflow fixture ID) are
  renamed.
- **Q7 Sequencing** (open: q5, a Host scheduling question): both proposals edit the same bundle and
  `CAP-DLV-idea-incubation`. Recommended: `PROP-deep-research-bundle` reaches Development first, and this proposal's
  handoff waits for its integration and declares `depends_on: [PROP-deep-research-bundle]`. Planning of both runs
  in parallel.

## 3. Proposed Design & Impact

### Approach and bundle

- `devkit-dist` accepts `adaptive-dev` beside `sdd` (`PADR-adaptive-dev-approach-name`), with the migration q1
  settles. The commented config template lists `sdd or adaptive-dev`.
- `devkit-spec` and `devkit-agt` compare the renamed value. Refusing SDD lifecycle mutation under the non-SDD
  approach is unchanged.
- The `incubation` catalog bundle becomes `adaptive-dev`: entry `/adaptive-dev`, pointer `adaptive-dev-pointer`,
  context file `.devkit/adaptive-dev.md`, the template and the remaining roles. The spec bundle's constitution,
  pointer, `spec` skill and `sdd-baseline` playbook name `adaptive-dev`; the playbook ID `sdd-baseline` stays.
- This repository's `AGENTS.md` managed block and `.devkit/installation.json` change only through `devkit sync`
  after the spec bundle source changes; `.devkit/managed/` stays untracked and unedited.

### Documents

Each renamed document moves to its new path, takes the new ID and keeps the old ID in `aliases`
(`ADR-document-id-aliases`). New IDs are written without backticks until their documents exist:

| Old ID | New ID | New title |
| --- | --- | --- |
| `CAP-DLV-idea-incubation` | CAP-DLV-adaptive-development | Adaptive Development |
| `CAP-DLV-incubation-sdd-baseline` | CAP-DLV-sdd-baseline-adoption | SDD baseline adoption |
| `UC-incubate-an-idea` | UC-advance-an-idea | Advance an idea and leave resumable current context |
| `UC-adopt-sdd-from-incubation` | UC-adopt-sdd-from-adaptive-development | Adopt SDD from an adaptive-development product |
| `CAP-DLV-proposal-incubation` | CAP-DLV-proposal-planning (q2) | Proposal Planning and Handoff |
| `UC-incubate-and-hand-off-a-proposal` | UC-plan-and-hand-off-a-proposal (q2) | Plan a Proposal and Hand It Off to a Spec |

- `devkit rules fix` rewrites every alias reference in current documents to the canonical ID. Under
  `ADR-immutable-decisions-editable-records` this includes the seven ADRs that cite a renamed ID (q4). ADR IDs,
  titles and decision text that name incubation stay as history.
- `guides/install/incubation-sdd-adoption.md` becomes `guides/install/adaptive-dev-sdd-adoption.md`, and the
  `#idea-incubation` anchors are renamed. The install guides gain the migration steps from Q1 and Q2.
- Glossary: **Development approach** names `sdd` or `adaptive-dev`. A new **Adaptive development** row lists
  "incubation" under Avoid. **Incubation current context** becomes **Adaptive-dev current context**
  (`.devkit/adaptive-dev.md`). The proposal Planning row lists "proposal incubation" under Avoid.
  `glossary.yaml` maps "incubation" as a search synonym to both terms, so a search for the old word finds them.
- History keeps its wording: `docs/decisions/` decision text, `specs/`, `docs/materials/`, `handbook/` and the
  done milestone `MS-idea-incubation`.

### Scope after `PROP-deep-research-bundle`

If that split lands first (q5), this proposal no longer renames the parts the split moves out:

- the `incubate-research` skill and its `orchestration`, `workspace` and `synthesis` references;
- the research-only roles `direction-explorer`, `discovery-critic` and `discovery-planner`, and the
  `incubation-researcher` role if the split takes it;
- `.devkit/transient/incubation-research/`, `CAP-DLV-idea-incubation` rules 17 to 26 and
  `UC-research-an-idea-and-shape-a-roadmap`.

The rename then covers `/incubate` with its `current-context`, `delegation`, `discovery` and
`evidence-and-iteration` references, the product roles, the pointer and template, and the product-iteration part
of `CAP-DLV-idea-incubation`. If this proposal lands first, it renames the whole bundle, and the split re-plans
against the new names.

## Planning decisions

- `PADR-adaptive-dev-approach-name` records the user's naming decision and rejected names.
- The draft boundaries excluded `docs/decisions/`. Planning moves it to `owns`, for canonical-ID reference
  rewrites only, because `RULE-document-reference` reports alias references in ADRs (q4). Planning also adds the
  package READMEs, `docs/development/`, `docs/README.md`, `docs/proposals/README.md`, `glossary.yaml`,
  `tests/e2e/smoke.sh`, `AGENTS.md` and `.devkit/installation.json`, which state the old names.
- `dev_effort` stays `high`: the approach value and bundle name are contracts that consumer repositories write,
  and the change spans four packages and about 110 files.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-rename-incubation-to-adaptive-dev`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
