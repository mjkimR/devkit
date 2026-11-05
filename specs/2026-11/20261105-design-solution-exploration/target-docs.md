---
id: PROP-design-solution-exploration-target
title: Target Living Spec Structure for PROP-design-solution-exploration
status: draft
proposal: SPEC-design-solution-exploration
created_at: 2026-11-05
targets:
  - file: docs/capabilities/delivery/CAP-DLV-design-exploration.md
  - file: docs/usecases/delivery/UC-explore-a-design-problem.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: packages/devkit-catalog/README.md
  - file: guides/install/bundle-recommendations.md
---

# [Blueprint] PROP-design-solution-exploration: General design exploration

This blueprint names the planned contracts and exact future paths. Proposed new document IDs below are plain
text until Development creates them. The proposal contains the reasons; these targets contain the retained rules.

## 1. Capability and use case

Create CAP-DLV-design-exploration at `docs/capabilities/delivery/CAP-DLV-design-exploration.md`.
It describes user-only invocation, general solution design, optional roles with independent first passes,
concrete mechanisms and tradeoffs, conversation-first retention and coordinator authority. It excludes automatic
implementation, global role registration, mandatory research or comparative-benefit validation. Link the new
use case in frontmatter and declare the skill source as its entrypoint.

Create UC-explore-a-design-problem at `docs/usecases/delivery/UC-explore-a-design-problem.md`.
Its main scenario recovers the goal and constraints, selects useful perspectives, compares returned mechanisms
and presents actionable directions. Extensions cover a simple inline answer, insufficient constraints, unavailable
fresh contexts, partial research and a requested output destination. Link the capability in frontmatter.

No product screens or UX documents change: the skill's output is a design discussion, not a product interface.

## 2. Architecture and decision

Update `ARCH-05-2-components` at its existing catalog layout paragraph to include the opt-in
`devkit_catalog/design_explore/bundle/` module. It contains content only, no runtime dependency or cross-feature
edge, and no assets imported from deep-research or another bundle.

`ADR-explicit-solution-exploration` becomes an ADR at handoff. The capability restates its invocation, local-role
and output-authority clauses. The implementation reconciles those trace references after creating the documents.

## 3. Exact implementation paths

| Planned path | Intended change |
| --- | --- |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/__init__.py` | Empty content-module initializer. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/bundle.toml` | `design-explore` bundle, `core` preset and one `invocation = "user"` skill; no `auto_select`. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/SKILL.md` | Explicit entry, concise process and completion boundaries. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/roles/solution-explorer.md` | One reusable role with per-assignment premise and constraint packet. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/roles/reference-researcher.md` | Optional bounded evidence and precedent investigation. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/roles/design-critic.md` | Optional consequential criticism; zero findings permitted. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/references/orchestration.md` | Fresh-context payload, optional casts, fallback, return validation and coordinator ownership. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/references/exploration-methods.md` | Simplification, premise removal and mechanism transfer, with general-design examples. |
| `packages/devkit-catalog/pyproject.toml` | Add only the `design-explore = "devkit_catalog.design_explore"` bundle entrypoint. |
| `packages/devkit-catalog/tests/integration/bundles/test_design_explore.py` | Real sync selection, user-only projection, local-role ownership, independent removal and key instruction semantics. |
| `packages/devkit-catalog/tests/e2e/bundles/design_explore/test_installed_consumer.py` | Built-wheel consumer selection/removal and role packaging without devkit-spec or companion bundles. |

Do not modify other bundle sources or general test infrastructure. Use the installed consumer tests and catalog
manifest checks as references, without copying another bundle's behavior contracts. The package version remains
the existing catalog version. No new dependency or `uv.lock` change is planned.

## 4. Consumer guidance and verification

Add a `design-explore` row and concise usage text in `packages/devkit-catalog/README.md` and
`guides/install/bundle-recommendations.md`. Recommend only on an explicit request for general solution design;
selection never starts the skill and no always-loaded pointer or specialist metadata is introduced.

Development runs focused integration and wheel-consumer checks plus required lint, types and governance rules.
Semantic review checks that architecture/model/workflow examples preserve goals, produce meaningfully distinct
mechanisms and stay within output authority. Checks establish packaging and instruction consistency, not creativity
or superiority over one agent. The Host schedules changes to shared registration and guidance files sequentially
with other catalog additions.
