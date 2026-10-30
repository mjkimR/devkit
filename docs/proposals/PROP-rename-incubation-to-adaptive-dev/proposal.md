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

Planning answers each question below; `MAT-incubation-rename-inventory` lists every affected file and
`envelopes/scout-01.yaml` holds the migration evidence. "Open" marks an answer the user's decision completes.

- **Q1 Approach migration** (open: q1): no deprecation-notice mechanism exists, and `CAP-DIST-sync-and-transactions`
  requires `DEVELOPMENT_CONFIG_INVALID` for any unknown value. A plain in-place refusal, as the `devkit:run` to
  `harness:run` precedent did, blocks one path: integration readiness parses the committed target config and the
  proposed result (`devkit_agt.features.integration.usecases.project`,
  `devkit_spec.features.delivery.usecases.integration`). An adaptive-dev consumer's migration branch therefore
  fails readiness, because the new parser refuses `"incubation"` on the target and an old parser refuses
  `"adaptive-dev"` on the result. Recommended (q1 option b):
  - The working configuration refuses `"incubation"` with `DEVELOPMENT_CONFIG_INVALID` (exit 2), and its `fix`
    names the exact edit: `Rename [development] approach = "incubation" to "adaptive-dev"`.
  - Parsing a committed snapshot reads a legacy `"incubation"` as `adaptive-dev`, so the migration commit
    integrates through devkit. This applies only to the target side of readiness and other committed-base reads.
  - No release window is kept for the working configuration.
- **Q2 Bundle migration** (open: q1): no bundle alias exists, a shim bundle cannot reuse the entry-point name, and
  sync refuses a selected bundle that no package provides (`SELECTION_INVALID`, fix `devkit remove incubation`).
  devkit-catalog pins no devkit-dist version. The install guides therefore state ordered migration steps:
  1. Upgrade every declared devkit package to the same release.
  2. Edit `[development] approach` to `"adaptive-dev"`.
  3. Run `devkit remove incubation`; sync removes the unedited copies and projections and reports edited ones as
     `ORPHAN_LEFT`.
  4. Run `devkit add adaptive-dev`.
  5. Move `.devkit/overrides/incubation/` to `.devkit/overrides/adaptive-dev/` and rename the asset paths inside it
     (`skills/incubate/` to `skills/adaptive-dev/`); sync reports the old directory as `OVERRIDE_RETAINED` until
     then.
  6. Move `.devkit/incubation.md` to `.devkit/adaptive-dev.md` (`git mv` when tracked).
- **Q3 Context file**: the file becomes `.devkit/adaptive-dev.md`. Only guidance reads or writes it, and sync never
  touches it. When `.devkit/adaptive-dev.md` is absent and `.devkit/incubation.md` exists, the entry and the
  `sdd-baseline` playbook read the legacy file, and the entry moves it on its first write and reports the move. The
  file stays project-owned and never seeded (`CAP-DLV-idea-incubation` rules 14 and 15 keep their meaning).
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
- **Q7 Sequencing** (open: q4, for the Host and the user): both proposals edit the same bundle and
  `CAP-DLV-idea-incubation`. Recommended: `PROP-deep-research-bundle` reaches Development first, and this proposal's
  handoff waits for its integration and declares `depends_on: [PROP-deep-research-bundle]`. Planning of both runs
  in parallel. Reasons:
  - The split moves the research entry, its references and roles; renaming them first would rename text the split
    then moves and rewrites.
  - The split's proposal cites `CAP-DLV-idea-incubation`; renaming first makes that citation an alias reference in a
    file this proposal does not own.
  - Both integrations ship in the same minor release, so a consumer migrates its selection and overrides once (q4).

## 3. Proposed Design & Impact

### Approach and bundle

- `devkit-dist` accepts `adaptive-dev` beside `sdd` (`PADR-adaptive-dev-approach-name`), with the migration q1
  settles. The commented config template lists `sdd or adaptive-dev`.
- `devkit-spec` and `devkit-agt` compare the renamed value. Refusing SDD lifecycle mutation under the non-SDD
  approach is unchanged.
- The `incubation` catalog bundle becomes `adaptive-dev`: entry `/adaptive-dev`, pointer `adaptive-dev-pointer`,
  context file `.devkit/adaptive-dev.md`, the template and the remaining roles. The package moves to
  `devkit_catalog.adaptive_dev`, and `.devkit/architecture.toml` lists `adaptive_dev` among the `devkit_catalog`
  data roots. The spec bundle's constitution,
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
  `ADR-immutable-decisions-editable-records` this includes the ADRs and the feedback files under `specs/**/feedback/`
  that cite a renamed ID (15 files in 10 `feedback/` directories at `fb9b549a`, listed in `owns`).
- The ADR promoted from `PADR-adaptive-dev-approach-name` names the statements it replaces: the value set of
  `ADR-own-development-approach-policy-outside-sdd` and the bundle and entry names in
  `ADR-keep-incubation-guidance-opt-in-and-current-state-based` and
  `ADR-extend-incubation-with-optional-discovery-teams`. Each such accepted ADR gets a one-line pointer to it.
  Development checks the remaining ADRs for an outcome that names the value, bundle or entry. ADR IDs, titles and
  other decision text stay as history.
- `guides/install/incubation-sdd-adoption.md` becomes `guides/install/adaptive-dev-sdd-adoption.md`, and the
  `#idea-incubation` anchors are renamed. The install guides gain the migration steps from Q1 and Q2.
- Glossary: **Development approach** names `sdd` or `adaptive-dev`. A new **Adaptive development** row lists
  "incubation" under Avoid. **Incubation current context** becomes **Adaptive-dev current context**
  (`.devkit/adaptive-dev.md`). The proposal Planning row lists "proposal incubation" under Avoid.
  `glossary.yaml` maps "incubation" as a search synonym to both terms, so a search for the old word finds them.
- History keeps its wording: `docs/decisions/` decision text, `specs/` outside the listed `feedback/` directories,
  `docs/materials/`, `handbook/` and the done milestone `MS-idea-incubation`.

### Scope after `PROP-deep-research-bundle`

If that split lands first (q4), this proposal no longer renames the parts the split moves out:

- the `incubate-research` skill and its `orchestration`, `workspace` and `synthesis` references;
- the research-only roles `direction-explorer`, `discovery-critic` and `discovery-planner`, and the
  `incubation-researcher` role if the split takes it;
- `CAP-DLV-idea-incubation` rules 17 to 26 and `UC-research-an-idea-and-shape-a-roadmap`.

The rename then covers `/incubate` with its `current-context`, `delegation`, `discovery` and
`evidence-and-iteration` references, the product roles, the pointer and template, and the product-iteration part
of `CAP-DLV-idea-incubation`. Any current name that still carries incubation after the split, such as
`.devkit/transient/incubation-research/` or `incubation-researcher`, is renamed here wherever it lives in `owns`.
If this proposal lands first, it renames the whole bundle, and the research entry and roles take the names that
`PROP-deep-research-bundle` Planning chooses, so the split only moves them.

## Acceptance

- `rg --hidden -i incubat` over tracked files returns only allowlisted matches: history paths, `aliases` entries,
  ADR IDs and titles, the targeted `fix` text and legacy-value reading, the legacy context-file fallback and guide
  migration steps, glossary Avoid cells and `glossary.yaml` synonyms.
- `packages/devkit-dist/tests/integration/features/project/test_development.py` checks that the working config
  refuses `"incubation"` with the rename `fix` and that a committed snapshot reads it as `adaptive-dev`.
- An integration-readiness test integrates a branch that changes `approach = "incubation"` to `"adaptive-dev"`.
- A catalog e2e test simulates a consumer whose receipt records `incubation` with no providing package: it runs
  `devkit remove incubation`, then `devkit add adaptive-dev`, and checks the receipt, orphans and the preserved
  context file.
- `just rules-check` passes over the whole workspace, with no alias reference left in a current document.

## Planning decisions

- `PADR-adaptive-dev-approach-name` records the user's naming decision and rejected names.
- The draft boundaries excluded `docs/decisions/` and `specs/`. `RULE-document-reference` reports alias references
  in ADRs and in feedback files under `specs/`, and `ADR-immutable-decisions-editable-records` makes canonical-ID
  rewrites and one-line pointers editorial ADR edits. Planning therefore owns `docs/decisions/` and the ten
  `feedback/` directories for those edits only.
- Planning also adds the package READMEs, `docs/development/`, `docs/README.md`, `docs/proposals/README.md`,
  `glossary.yaml`, `tests/e2e/smoke.sh`, `AGENTS.md`, `.devkit/installation.json` and `.devkit/architecture.toml`,
  which state the old names.
- `dev_effort` stays `high`: the approach value and bundle name are written by consumer repositories that install
  devkit from pushed Git refs (`MAT-git-operator-consumer-pilot` records the `resource-indexer` consumer), and the
  rename breaks that configuration contract and the migration commit's integration path (Q1).

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-rename-incubation-to-adaptive-dev`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
