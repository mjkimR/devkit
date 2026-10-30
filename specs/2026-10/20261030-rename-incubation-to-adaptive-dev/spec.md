---
id: SPEC-rename-incubation-to-adaptive-dev
title: Rename incubation to adaptive-dev and disambiguate proposal terms
summary: Rename the incubation bundle and development approach to adaptive-dev and the SDD proposal-incubation term to proposal Planning, so each development concept has one unambiguous name. No consumer uses incubation yet, so the old value and bundle become plain invalid names with no migration path.
status: completed
created: 2026-10-30
depends_on:
  - SPEC-deep-research-bundle
related_capabilities:
  - CAP-DLV-adaptive-development
  - CAP-DLV-sdd-baseline-adoption
  - CAP-DLV-proposal-planning
  - CAP-DIST-sync-and-transactions
  - CAP-DLV-project-policy
related_usecases:
  - UC-advance-an-idea
  - UC-adopt-sdd-from-adaptive-development
  - UC-plan-and-hand-off-a-proposal
workflow: sdd-spec-feature
---

# [SPEC-rename-incubation-to-adaptive-dev] Rename incubation to adaptive-dev and disambiguate proposal terms

## 1. Problem Statement & Motivation

Handed off from proposal PROP-rename-incubation-to-adaptive-dev (accepted at historical Git
`b27116846db71a45feacbaa7e60b05ac4d2c4d5e:docs/proposals/PROP-rename-incubation-to-adaptive-dev/proposal.md`). The
decision is `ADR-adaptive-dev-approach-name`; the inventory is `MAT-incubation-rename-inventory`, measured at
`fb9b549a` before `SPEC-deep-research-bundle` landed.

"Incubation" names two unrelated concepts in this repository:

- The SDD proposal lifecycle: CAP-DLV-proposal-incubation and UC-incubate-and-hand-off-a-proposal (draft,
  Planning, acceptance and handoff of a proposal).
- The development approach that iterates without per-change SDD records: `[development] approach = "incubation"`,
  the `incubation` catalog bundle, `/incubate`, `get-context incubation` and `.devkit/incubation.md`
  (CAP-DLV-idea-incubation, CAP-DLV-incubation-sdd-baseline).

With both installed, a request to "incubate" an idea does not identify which one the user means. One distinct name
per concept removes the ambiguity at every entry, setting and document.

Settled direction (user, `ADR-adaptive-dev-approach-name`):

- The approach and bundle become `adaptive-dev`; documents call the approach "adaptive development". Rejected:
  `incubation`, `project-incubation`, `project-bootstrap`, `project-adaptive`, `adaptive`.
- No consumer uses the incubation approach or bundle, so no compatibility is kept: `"incubation"` is an ordinary
  invalid approach value, the `incubation` bundle name gets no alias and `.devkit/incubation.md` gets no fallback
  read. The guides state no migration steps.
- The SDD proposal term becomes "proposal Planning", the name the spec bundle already uses for that activity.
- The approach contract is unchanged: a product may stay in adaptive development, and SDD adoption stays the
  explicit `sdd-baseline` procedure.

### Premises checked against the current base

The proposal was planned before `SPEC-deep-research-bundle` landed (b2711684). Checked on this branch:

- The split moved `incubate-research`, its references and the roles `direction-explorer`, `discovery-critic` and
  `discovery-planner` into the `deep-research` bundle, and added `CAP-DLV-deep-research`. The remaining incubation
  bundle holds exactly `incubate`, `incubation-pointer`, `product-clarifier`, `incubation-researcher`,
  `usage-reviewer` and `current-context-template`, as the proposal's "Scope after" section expects.
- The split added current text that names the incubation bundle: `CAP-DLV-deep-research`,
  `UC-research-an-idea-and-shape-a-roadmap`, `ADR-split-deep-research-bundle`,
  `ADR-retain-research-as-cited-materials`, the deep-research tests, the catalog README and three guides. Mentions
  that describe the split's own move away from the old bundle (`.devkit/transient/incubation-research/`,
  `incubation:<role>`, `.devkit/overrides/incubation/subagents/`) name a legacy location and stay; mentions of the
  bundle as a current concept are renamed. Both readings are inside the proposal's scope.
- `ADR-extend-incubation-with-optional-discovery-teams` is superseded by `ADR-split-deep-research-bundle`, as Q7
  assumed.

## 2. User Stories

- **US-1**: As a user with both the spec and the adaptive-dev bundles installed, I want each development concept to
  have its own name, so that asking for adaptive development or for proposal Planning identifies one procedure.
- **US-2**: As a consumer configuring a project, I want `[development] approach` to accept `"sdd"` or
  `"adaptive-dev"` and to name both when it refuses a value, so that I set the approach without reading history.
- **US-3**: As a reader of the Living Spec, I want the renamed documents to resolve by their old IDs, so that
  history that cites CAP-DLV-idea-incubation or CAP-DLV-proposal-incubation still finds the current contract.

## 3. Non-Goals

1. **Scope Excluded**: no compatibility for the old names: no legacy reading of `"incubation"` in the working
   configuration or a committed snapshot, no deprecation period or rename hint, no `incubation` bundle alias, no
   `.devkit/incubation.md` fallback read and no migration steps in the guides.
2. **Scope Excluded**: no behavior change of the approach, the bundle, the readiness checks or the SDD lifecycle
   refusal; the codes `DEVELOPMENT_CONFIG_INVALID`, `SDD_LIFECYCLE_INACTIVE`, `SPEC_LIFECYCLE_INACTIVE` and
   `SELECTION_INVALID` keep their names.
3. **Scope Excluded**: no rewording of history: decision text in `docs/decisions/` (only canonical-ID rewrites and
   the one-line pointers), `specs/` outside the listed `feedback/` directories, `docs/materials/`, `handbook/` and
   the done milestone `MS-idea-incubation` keep their wording.
4. **Scope Excluded**: no change to the split's legacy-location mentions or to the deep-research bundle text.
5. **Scope Excluded**: no rename of the playbook ID `sdd-baseline` or of the ADR IDs and titles that contain
   incubation.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] "incubation" names no current concept

- **Given** the committed head of this branch
- **When** `git ls-files -z | xargs -0 rg --hidden -i -n incubat` runs from the repository root
- **Then** every matching line falls in one allowlisted class: a history path (`docs/decisions/` decision text,
  `specs/` outside the listed `feedback/` directories, `docs/materials/`, `handbook/`, `docs/roadmap/_archive/`); an
  `aliases` entry; an ADR ID or title; a glossary Avoid cell or `glossary.yaml` synonym; a legacy-location mention
  of the deep-research split; a test line that asserts the old name is refused or absent; or a line of the listed
  `feedback/` files that names no renamed ID outside fenced evidence and past file paths (their observation prose,
  fenced evidence and past file paths, which this change owns only for canonical-ID rewrites); the check reports zero
  lines outside these classes

### [AC-02] The approach accepts sdd and adaptive-dev and refuses incubation

- **Given** `.devkit/config.toml` with `[development] approach` set to `"sdd"`, `"adaptive-dev"` or `"incubation"`
- **When** `development_approach` parses the working configuration or a committed snapshot
- **Then** `"sdd"` and `"adaptive-dev"` parse to that value; `"incubation"` raises `DEVELOPMENT_CONFIG_INVALID`
  (exit 2) whose `fix` is exactly `Use [development] approach = "sdd" or "adaptive-dev" in .devkit/config.toml`, as
  `packages/devkit-dist/tests/integration/features/project/test_development.py` asserts

### [AC-03] Readers of the approach compare the renamed value

- **Given** a project whose committed and working configuration set `approach = "adaptive-dev"`
- **When** the readiness, attach, integration, cleanup, hygiene, rule-applicability and lifecycle tests in
  `packages/devkit-spec/tests/` and `packages/devkit/tests/` run
- **Then** they pass with the behavior of the old value: project readiness records the evidence
  `LIFECYCLE omitted:adaptive-dev`, the rule omission reason reads `adaptive-dev: no targeted retained SDD unit`
  and SDD lifecycle mutation is refused with `SPEC_LIFECYCLE_INACTIVE` naming the adaptive-dev development approach

### [AC-04] The catalog ships the adaptive-dev bundle

- **Given** devkit-catalog registers the entry point `adaptive-dev = "devkit_catalog.adaptive_dev"` and no
  `incubation` entry point
- **When** `packages/devkit-catalog/tests/integration/bundles/` selects `adaptive-dev:core` and syncs
- **Then** the preset holds exactly `adaptive-dev`, `adaptive-dev-pointer`, `product-clarifier`,
  `product-researcher`, `usage-reviewer` and `current-context-template`; the `/adaptive-dev` skill, the pointer
  guidance and the three roles are projected; no file of the bundle contains `incubat`; the entry and its references
  name `.devkit/adaptive-dev.md`, `get-context adaptive-dev` and `approach = "adaptive-dev"`; sync seeds no
  `.devkit/adaptive-dev.md`; selecting `incubation:core` fails with `SELECTION_INVALID`

### [AC-05] The consumer smoke test sees the renamed bundle

- **Given** `just smoke` installs the built wheels into a scratch consumer
- **When** it lists the catalog bundles and runs the default sync
- **Then** the catalog bundle set is exactly `response-style`, `maintenance`, `cli-tool`, `adaptive-dev` and
  `deep-research`, and `.devkit/managed/adaptive-dev` does not exist

### [AC-06] The renamed documents resolve and no current document cites an alias

- **Given** the six renamed documents of section 5
- **When** `devkit docs resolve <old ID>` runs for each old ID and `just rules-check` runs over the workspace
- **Then** each old ID resolves to the new document, which keeps the old ID in `aliases`; `just rules-check` exits 0
  with no alias reference left in a current document

### [AC-07] The spec bundle and its CLI use the new names

- **Given** the spec bundle source and `devkit spec proposal --help`
- **When** this repository runs `devkit sync` and an agent reads the constitution, pointer, `spec` skill and
  `sdd-baseline` playbook
- **Then** they name `adaptive-dev` for the approach and `/adaptive-dev` for its entry; the help's first line reads
  "Plan proposals in docs/proposals/ and hand approved ones off to spec bundles."; the `AGENTS.md` managed block and
  `.devkit/installation.json` change only through that sync, and `devkit sync --check` exits 0 afterwards

## 5. Design

### Approach value

`devkit_dist.features.project.models.development` is the only parser: its `Literal`, check, message and `fix` name
`"sdd"` and `"adaptive-dev"`. The commented config template lists `sdd or adaptive-dev`. Readers that compare the
literal change from `"incubation"` to `"adaptive-dev"`, with the output text that names the approach:
`devkit_spec.features.delivery.usecases.attach`, `.integration` and `.cleanup`,
`devkit_spec.features.governance.services.applicability`, `devkit_spec.features.governance.usecases.hygiene`,
`devkit_spec.features.policy.services.lifecycle` and `devkit_agt.features.integration.usecases.project`.

### Catalog bundle

| Old | New |
| --- | --- |
| package `devkit_catalog.incubation`, entry point `incubation` | `devkit_catalog.adaptive_dev`, entry point `adaptive-dev` |
| skill `incubate` (`/incubate`) | `adaptive-dev` (`/adaptive-dev`), with its `current-context`, `delegation`, `discovery` and `evidence-and-iteration` references |
| guidance `incubation-pointer` | `adaptive-dev-pointer` |
| role `incubation-researcher` | `product-researcher` |
| context file `.devkit/incubation.md` | `.devkit/adaptive-dev.md` |

`product-clarifier`, `usage-reviewer` and `current-context-template` keep their IDs. `.devkit/architecture.toml`
lists `adaptive_dev` among the `devkit_catalog` data roots. Tests move to
`tests/integration/bundles/test_adaptive_dev.py` and `tests/e2e/bundles/adaptive_dev/`.

### Documents

Each renamed document moves to its new path, takes the new ID and keeps the old ID in `aliases`
(`ADR-document-id-aliases`); `devkit rules fix` rewrites alias references in current documents, ADRs and the listed
`feedback/` files:

| Old ID | New ID | New title |
| --- | --- | --- |
| CAP-DLV-idea-incubation | `CAP-DLV-adaptive-development` | Adaptive Development |
| CAP-DLV-incubation-sdd-baseline | `CAP-DLV-sdd-baseline-adoption` | SDD baseline adoption |
| UC-incubate-an-idea | `UC-advance-an-idea` | Advance an idea and leave resumable current context |
| UC-adopt-sdd-from-incubation | `UC-adopt-sdd-from-adaptive-development` | Adopt SDD from an adaptive-development product |
| CAP-DLV-proposal-incubation | `CAP-DLV-proposal-planning` | Proposal Planning and Handoff |
| UC-incubate-and-hand-off-a-proposal | `UC-plan-and-hand-off-a-proposal` | Plan a Proposal and Hand It Off to a Spec |

- `ADR-own-development-approach-policy-outside-sdd`, `ADR-keep-incubation-guidance-opt-in-and-current-state-based`
  and every other accepted, not superseded ADR whose outcome names the value, bundle or entry as current get a
  one-line pointer to `ADR-adaptive-dev-approach-name`.
- `guides/install/incubation-sdd-adoption.md` becomes `guides/install/adaptive-dev-sdd-adoption.md`; the
  `#idea-incubation` anchors become `#adaptive-development`.
- Glossary: **Development approach** names `sdd` or `adaptive-dev`; a new **Adaptive development** row lists
  "incubation" under Avoid; **Incubation current context** becomes **Adaptive-dev current context**; a new
  **Proposal Planning** row lists "proposal incubation" under Avoid. `glossary.yaml` maps "incubation" as a search
  synonym to both terms.

## 6. Assumptions

- The CLI help sentence of AC-07 replaces "Incubate" with "Plan", the verb of the term the proposal chose.
- The guide anchor `#idea-incubation` becomes `#adaptive-development`, from the renamed heading "Adaptive
  development".
- Test lines that assert an old name is refused (`"incubation"` in AC-02, `incubation:core` in AC-04) or absent
  from a projection are an AC-01 allowlist class: they are the evidence that the old name is no current concept.
- The listed `feedback/` files are observation records: plain-text old IDs in their prose and frontmatter `target`
  are rewritten to the canonical ID like the references `devkit rules fix` rewrites, while their other observation
  prose, fenced evidence and past file paths keep their recorded wording. This AC-01 class follows from Non-Goal 3
  and the proposal's ownership of those directories for ID rewrites only.
- The split's migration sections in the guides and the catalog README keep their legacy keys and paths; their lead
  sentence names "the former `incubation` bundle" so it reads as a legacy location.
- The catalog bundle version stays `0.1.5`; a release bumps it.
