---
id: PROP-rename-incubation-to-adaptive-dev
title: Rename incubation to adaptive-dev and disambiguate proposal terms
summary: "Rename the incubation bundle and development approach to adaptive-dev and the SDD proposal-incubation term to proposal Planning, so each development concept has one unambiguous name. No consumer uses incubation yet, so the old value and bundle become plain invalid names with no migration path."
status: accepted
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: high
size: L
planning_effort: medium
dev_effort: medium
depends_on: [PROP-deep-research-bundle]
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
    - .devkit/architecture.toml
    - specs/2026-10/20261015-orchestration-mode/feedback/
    - specs/2026-10/20261020-draft-direct-acceptance/feedback/
    - specs/2026-10/20261020-language-setting-coverage/feedback/
    - specs/2026-10/20261022-document-id-aliases-and-compaction/feedback/
    - specs/2026-10/20261026-feedback-guidance-and-scope/feedback/
    - specs/2026-10/20261026-handoff-modes-and-template-report/feedback/
    - specs/2026-10/20261026-living-spec-consistency-sweep/feedback/
    - specs/2026-10/20261026-merge-proposal-materials-at-handoff/feedback/
    - specs/2026-10/20261028-incubation-development-guidance/feedback/
    - specs/2026-10/feedback/
  excludes:
    - .devkit/managed/
    - handbook/
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

Planning answers each question below; `MAT-incubation-rename-inventory` lists every affected file,
`envelopes/scout-01.yaml` holds the evidence and `envelopes/answer-01.yaml` records the decisions.

- **Q1 Approach value** (q1): no consumer uses the incubation approach or bundle, so the rename keeps no
  compatibility. `"incubation"` becomes an ordinary invalid value:
  - Every parse of `[development] approach`, of the working configuration and of a committed snapshot alike,
    refuses it with `DEVELOPMENT_CONFIG_INVALID` (exit 2), as it refuses any unknown value
    (`CAP-DIST-sync-and-transactions`).
  - The `fix` names the valid values: `Use [development] approach = "sdd" or "adaptive-dev" in .devkit/config.toml`.
  - No deprecation period, legacy normalization or targeted rename hint is added.
- **Q2 Bundle** (q1): the `incubation` bundle name is removed with no alias or shim. A configuration that still
  selects it gets the existing `SELECTION_INVALID` refusal of a bundle no package provides. The guides describe only
  the `adaptive-dev` bundle and state no migration steps for the selection, overrides or role-policy keys.
- **Q3 Context file**: the file becomes `.devkit/adaptive-dev.md`. Only guidance reads or writes it, and sync never
  touches it. The entry and the `sdd-baseline` playbook read no legacy `.devkit/incubation.md` (q1). The file stays
  project-owned and never seeded (`CAP-DLV-idea-incubation` rules 14 and 15 keep their meaning).
- **Q4 Entry and role names** (q3): the entry `/incubate` becomes `/adaptive-dev`, the approach's main entry as
  `/spec` is SDD's; it is renamed, not added beside `/incubate`. The pointer guidance becomes `adaptive-dev-pointer`,
  and `incubation-researcher` becomes `product-researcher` beside `product-clarifier`. The researcher stays in
  adaptive-dev: `PROP-deep-research-bundle` ships its own `research-investigator`, and the two bundles share no role
  and declare no bundle or package dependency in either direction. adaptive-dev never invokes deep-research; it reads
  retained research only by its `MAT-<slug>` ID.
- **Q5 SDD term** (q2): the spec bundle already calls this activity Planning (`planning.md`, `plan-<slug>`,
  `plan-intent`, `plan-accept`, `planning-worker`, `planning_effort`). The term is "proposal Planning":
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
- **Q7 Sequencing** (q4, decided by the Host): `PROP-deep-research-bundle` lands first, and this proposal declares
  `depends_on: [PROP-deep-research-bundle]`. Both Plannings may run in parallel; no same-release constraint applies.
  Reasons:
  - The split moves the research entry, its references and roles; renaming them first would rename text the split
    then moves and rewrites.
  - The split's proposal cites `CAP-DLV-idea-incubation`; renaming first would make that citation an alias reference
    in a file this proposal does not own.

## 3. Proposed Design & Impact

### Approach and bundle

- `devkit-dist` accepts `adaptive-dev` beside `sdd` (`PADR-adaptive-dev-approach-name`) and refuses `"incubation"`
  like any unknown value (Q1). The commented config template lists `sdd or adaptive-dev`.
- `devkit-spec` and `devkit-agt` compare the renamed value. Refusing SDD lifecycle mutation under the non-SDD
  approach is unchanged.
- The `incubation` catalog bundle becomes `adaptive-dev` (Q4): entry `/adaptive-dev`, pointer
  `adaptive-dev-pointer`, context file `.devkit/adaptive-dev.md`, the current-context template and the roles
  `product-clarifier`, `product-researcher` (renamed from `incubation-researcher`) and `usage-reviewer`.
- The package moves to `devkit_catalog.adaptive_dev`, and `.devkit/architecture.toml` lists `adaptive_dev` among the
  `devkit_catalog` data roots.
- The spec bundle's constitution, pointer, `spec` skill and `sdd-baseline` playbook name `adaptive-dev`; the
  playbook ID `sdd-baseline` stays.
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
  `ADR-immutable-decisions-editable-records` this includes the ADRs and the feedback files under `specs/**/feedback/`
  that cite a renamed ID (15 files in 10 `feedback/` directories at `fb9b549a`, listed in `owns`).
- The ADR promoted from `PADR-adaptive-dev-approach-name` names the statements it replaces: the value set of
  `ADR-own-development-approach-policy-outside-sdd` and the bundle, entry and context-file names in
  `ADR-keep-incubation-guidance-opt-in-and-current-state-based`. Each such accepted ADR gets a one-line pointer to it.
- `ADR-extend-incubation-with-optional-discovery-teams` gets no pointer here: the ADR promoted from
  PADR-split-deep-research-bundle (on the split's Planning branch) supersedes it before this proposal starts (Q7).
- Development checks every other accepted, not superseded ADR, including those the split promotes, for an outcome
  that names the value, bundle or entry, and adds the same pointer. ADR IDs, titles and other decision text stay as
  history.
- `guides/install/incubation-sdd-adoption.md` becomes `guides/install/adaptive-dev-sdd-adoption.md`, and the
  `#idea-incubation` anchors are renamed. The guides gain no migration steps (Q1, Q2).
- Glossary: **Development approach** names `sdd` or `adaptive-dev`. A new **Adaptive development** row lists
  "incubation" under Avoid. **Incubation current context** becomes **Adaptive-dev current context**
  (`.devkit/adaptive-dev.md`). The proposal Planning row lists "proposal incubation" under Avoid.
  `glossary.yaml` maps "incubation" as a search synonym to both terms, so a search for the old word finds them.
- History keeps its wording: `docs/decisions/` decision text, `specs/` outside the listed `feedback/` directories,
  `docs/materials/`, `handbook/` and the done milestone `MS-idea-incubation`.

### Scope after `PROP-deep-research-bundle`

The split lands first (Q7), so this proposal renames the bundle as the split leaves it and excludes what the split
moves out:

- the `incubate-research` skill and its `orchestration`, `workspace` and `synthesis` references;
- the research-only roles `direction-explorer`, `discovery-critic` and `discovery-planner`, and the split's own
  `research-investigator`;
- `CAP-DLV-idea-incubation` rules 17 to 23, 25 and 26 and `UC-research-an-idea-and-shape-a-roadmap`, which move to
  the split's research capability.

The rename covers `/incubate` with its `current-context`, `delegation`, `discovery` and `evidence-and-iteration`
references, the three product roles, the pointer and template, and the product-iteration part of
`CAP-DLV-idea-incubation`. Any current name the split leaves that still contains incubation is renamed here wherever
it lives in `owns`. A path or key the split's documents name only to describe its own move away from the
incubation bundle, such as `.devkit/transient/incubation-research/`, stays: it names a legacy location, not a
current concept.

## Acceptance

- `rg --hidden -i incubat` over tracked files returns only allowlisted matches: history paths, `aliases` entries,
  ADR IDs and titles, glossary Avoid cells, `glossary.yaml` synonyms and the split's legacy-location mentions named
  above.
- `packages/devkit-dist/tests/integration/features/project/test_development.py` accepts `"sdd"` and
  `"adaptive-dev"` and refuses `"incubation"` with `DEVELOPMENT_CONFIG_INVALID` and the `fix` naming both valid
  values.
- The readiness and lifecycle tests in `packages/devkit-spec/tests/` and `packages/devkit/tests/` that set the
  non-SDD approach use `"adaptive-dev"` and assert the evidence `omitted:adaptive-dev`.
- `packages/devkit-catalog/tests/integration/bundles/` selects and projects the `adaptive-dev` bundle with the
  `/adaptive-dev` entry, the `adaptive-dev-pointer` guidance and the `product-researcher` role.
- `tests/e2e/smoke.sh` lists `adaptive-dev` in the catalog bundle set and asserts `.devkit/managed/adaptive-dev`.
- `just rules-check` passes over the whole workspace, with no alias reference left in a current document.

## Planning decisions

- `PADR-adaptive-dev-approach-name` records the user's naming decision, the rejected names and the no-compatibility
  rename (q1).
- `envelopes/answer-01.yaml` records the decisions on q1 to q4. Dropped with q1: the committed-snapshot legacy
  reading, the ordered guide migration steps, the legacy context-file fallback, the integration-readiness migration
  test and the remove-then-add catalog e2e migration test.
- The draft boundaries excluded `docs/decisions/` and `specs/`. `RULE-document-reference` reports alias references
  in ADRs and in feedback files under `specs/`, and `ADR-immutable-decisions-editable-records` makes canonical-ID
  rewrites and one-line pointers editorial ADR edits. Planning therefore owns `docs/decisions/` and the ten
  `feedback/` directories for those edits only.
- Planning also adds the package READMEs, `docs/development/`, `docs/README.md`, `docs/proposals/README.md`,
  `glossary.yaml`, `tests/e2e/smoke.sh`, `AGENTS.md`, `.devkit/installation.json` and `.devkit/architecture.toml`,
  which state the old names.
- `dev_effort` is `medium`: the change is a mechanical rename across several packages and documents with no
  consumer-contract migration, because no consumer uses the incubation approach or bundle (q1).

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-rename-incubation-to-adaptive-dev`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
