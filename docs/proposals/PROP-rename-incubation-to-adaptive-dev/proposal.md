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
    - packages/devkit-spec/src/devkit_spec/
    - packages/devkit-spec/tests/
    - packages/devkit/src/devkit_agt/features/integration/
    - packages/devkit/tests/
    - packages/devkit-catalog/src/devkit_catalog/
    - packages/devkit-catalog/tests/
    - packages/devkit-catalog/README.md
    - packages/devkit-catalog/pyproject.toml
    - packages/devkit-docs/tests/
    - docs/capabilities/
    - docs/usecases/
    - docs/architecture/
    - docs/steering/glossary.md
    - guides/
  excludes:
    - .devkit/managed/
    - handbook/
    - specs/
    - docs/materials/
    - docs/decisions/
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

- **Q1 Approach migration**: `development.py` accepts only `"sdd"` and `"incubation"`. Does a consumer config with
  `approach = "incubation"` keep working with a deprecation notice that names the replacement, or fail with
  `DEVELOPMENT_CONFIG_INVALID`? For how many releases?
- **Q2 Bundle migration**: How does a consumer with `[presets] incubation = ...` reach `adaptive-dev`: a catalog
  alias, a sync notice with the exact `devkit` command, or a documented manual edit? What happens to the
  previously projected `incubation` assets?
- **Q3 Context file**: Does `.devkit/incubation.md` move to an `adaptive-dev` path, and how does an existing file
  survive sync and re-selection (`CAP-DLV-idea-incubation` rule 15)?
- **Q4 Entry name**: Which name replaces `/incubate` so that it matches `adaptive-dev` and stays distinct from the
  SDD `/spec` entry?
- **Q5 SDD term**: Which term replaces "proposal incubation" in `CAP-DLV-proposal-incubation`,
  `UC-incubate-and-hand-off-a-proposal` and their references (about 30 files)? Old IDs stay resolvable through
  document `aliases`.
- **Q6 Code identifiers**: Which code reads the approach value (`devkit-dist` project models and config,
  `devkit-spec` policy, delivery and governance, `devkit-agt` integration), and which identifiers and codes
  rename with it?
- **Q7 Sequencing**: `PROP-deep-research-bundle` also edits the incubation bundle and `CAP-DLV-idea-incubation`.
  Which lands first in Development?

## 3. Proposed Design & Impact

- `devkit-dist` accepts `adaptive-dev` as the non-SDD approach, with the migration behavior Q1 settles.
- `devkit-spec` and `devkit-agt` branch on the renamed value; SDD lifecycle refusal under the non-SDD approach is
  unchanged.
- The `devkit_catalog.incubation` bundle becomes `adaptive-dev`, with its entry, context file and template
  renamed.
- Capabilities, use cases, architecture, glossary and install guides use `adaptive-dev` for the approach and the
  new SDD term for the proposal lifecycle; renamed IDs keep their old IDs in `aliases`.
- Existing ADRs, materials and completed specs stay unchanged as history; current documents cite them by ID.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-rename-incubation-to-adaptive-dev`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
