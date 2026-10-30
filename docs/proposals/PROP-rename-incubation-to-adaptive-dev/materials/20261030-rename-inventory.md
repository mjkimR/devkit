---
id: MAT-incubation-rename-inventory
title: Incubation rename inventory
summary: "Inventory of every current file, identifier and consumer-facing name that carries the word incubation at base fb9b549a, grouped by concept, with the paths outside the draft's boundaries."
created_at: 2026-10-30
---

# [MAT-incubation-rename-inventory] Incubation rename inventory

## Evidence boundary

Measured on `plan-rename-incubation-to-adaptive-dev` at base `fb9b549a` with
`rg -l -i incubat`, excluding `specs/`, `docs/materials/` and `handbook/`.
111 files match; 14 of them are ADRs, 3 are proposals and 1 is the archived milestone `MS-idea-incubation`.

## Concept A: the non-SDD development approach and its bundle

| Surface | Current name | Location |
| --- | --- | --- |
| Approach value | `[development] approach = "incubation"` | `packages/devkit-dist/src/devkit_dist/features/project/models/development.py` (`Literal`, validation, `fix` text, message) |
| Config template comment | `sdd or incubation` | `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py:653` |
| Approach readers | `== "incubation"` / `!= "incubation"` | `devkit_spec.features.delivery.usecases.{attach,integration,cleanup}`, `devkit_spec.features.governance.services.applicability`, `devkit_spec.features.governance.usecases.hygiene`, `devkit_agt.features.integration.usecases.project` |
| Output text | `omitted:incubation` evidence, `"incubation: no targeted retained SDD unit"` omission reason, lifecycle refusal message | `devkit_agt.features.integration.usecases.project:45`, `applicability.py:63,88`, `policy/services/lifecycle.py:17` |
| Codes | `DEVELOPMENT_CONFIG_INVALID`, `SDD_LIFECYCLE_INACTIVE` | unchanged: neither code names the approach |
| Bundle | entry point `incubation = "devkit_catalog.incubation"`, `bundle.toml name = "incubation"` | `packages/devkit-catalog/pyproject.toml`, `packages/devkit-catalog/src/devkit_catalog/incubation/` |
| Assets | `incubate` skill, `incubate-research` skill, `incubation-pointer` guidance, `incubation-researcher` role, `current-context-template` | `bundle.toml` `[presets.core]` |
| Context file | `.devkit/incubation.md` (project-owned, never seeded) | `skills/incubate/references/current-context.md`, `CAP-DLV-idea-incubation` rules 14-15 |
| Scratch path | `.devkit/transient/incubation-research/` | `skills/incubate-research/references/workspace.md` (moves with `PROP-deep-research-bundle`) |
| Spec bundle text | "Under `incubation`", `/incubate` entry, sdd-baseline wording | `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/{AGENTS.md.jinja,guidance/spec-pointer.md,skills/spec/SKILL.md.jinja,playbooks/sdd-baseline/SKILL.md}` |
| Documents | `CAP-DLV-idea-incubation`, `CAP-DLV-incubation-sdd-baseline`, `UC-incubate-an-idea`, `UC-adopt-sdd-from-incubation` | `docs/capabilities/delivery/`, `docs/usecases/delivery/` |
| Guides | `guides/install/incubation-sdd-adoption.md`, `#idea-incubation` anchors | `guides/INSTALL_GUIDE.md`, `guides/install/{bundle-recommendations,existing-repository,new-repository}.md` |
| Glossary | **Development approach** definition, **Incubation current context** row | `docs/steering/glossary.md:42-43` |

## Concept B: the SDD proposal lifecycle

| Surface | Current name | Location |
| --- | --- | --- |
| Documents | `CAP-DLV-proposal-incubation` ("Proposal Incubation and Handoff"), `UC-incubate-and-hand-off-a-proposal` | `docs/capabilities/delivery/`, `docs/usecases/delivery/` |
| References to them | 21 current files (capabilities, use cases, `docs/development/reference/integration.md`, `packages/devkit-spec/README.md`, two source docstrings, two tests) | `rg -c 'CAP-DLV-proposal-incubation\|UC-incubate-and-hand-off-a-proposal'` |
| CLI help | "Incubate proposals in docs/proposals/ ..." and the module docstring "incubate a proposal" | `packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py:1,164` |
| Prose | "proposal incubation", "design incubation", "An incubation space" | `docs/architecture/ARCH-04-1-ecosystem-boundaries.md:66`, `ARCH-04-2-delivery-policy.md:67`, `docs/development/workflow.md:9`, `docs/README.md:17`, `docs/proposals/README.md:3` |
| Test fixtures | `INCUBATED` proposal fixture, `incubate` workflow ID in fixtures | `packages/devkit-spec/tests/support/spec_support/proposals.py`, `packages/devkit/tests/integration/features/workflow/test_layouts_and_authoring.py` |

The spec bundle already names this activity Planning: `planning.md`, `plan-<slug>` branches, `plan-intent`,
`plan-accept`, the `planning-worker` role and the `planning_effort` field.

## Current files outside the draft's `owns`

| Path | Why it changes |
| --- | --- |
| `AGENTS.md` | Its managed block is projected from `spec-pointer.md`; `devkit sync` rewrites it after the source changes. |
| `.devkit/installation.json` | The receipt records the re-projected spec assets after `devkit sync`. |
| `packages/devkit-dist/README.md`, `packages/devkit-spec/README.md`, `packages/devkit/README.md` | Each states the approach values. |
| `docs/README.md`, `docs/proposals/README.md`, `docs/development/workflow.md`, `docs/development/reference/integration.md` | Concept B prose and references. |
| `tests/e2e/smoke.sh` | Asserts the catalog bundle set and `.devkit/managed/incubation`. |
| `docs/decisions/` (7 ADRs cite a renamed document ID) | `ADR-immutable-decisions-editable-records`: `RULE-document-reference` reports an alias reference in an ADR and `devkit rules fix` rewrites it. |
| `docs/proposals/PROP-deep-research-bundle/proposal.md` | Cites `CAP-DLV-idea-incubation`; a current document, so an alias reference is reported. |

## History that keeps its wording

- ADR IDs and titles that contain incubation (`ADR-keep-incubation-guidance-opt-in-and-current-state-based`,
  `ADR-extend-incubation-with-optional-discovery-teams` and others) stay: they record decisions taken under the old
  name.
- `MS-idea-incubation` is `done` in `docs/roadmap/_archive/`.
- `specs/`, `docs/materials/` and `handbook/` stay as written.
