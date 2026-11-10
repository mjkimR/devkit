---
id: PROP-adaptive-package-extraction
title: Extract adaptive development into a devkit-adaptive distribution
summary: "Move the adaptive-dev bundle from the content-only devkit-catalog into a new devkit-adaptive distribution that can carry code, keeping existing selections working, so adaptive development can gain commands."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-10
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-adaptive-development-runtime
boundaries:
  owns:
    - packages/
    - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/
    - packages/devkit-catalog/pyproject.toml
    - packages/devkit-catalog/README.md
    - packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py
    - packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/
    - packages/devkit-catalog/tests/support/adaptive_behavior_scorer.py
    - docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    - docs/architecture/ARCH-05-2-components.md
    - docs/architecture/ARCH-07-deployment.md
    - guides/install/
    - .devkit/architecture.toml
    - pyproject.toml
  excludes:
    - packages/devkit-spec/
    - packages/devkit-dist/src/devkit_dist/features/host/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-adaptive-package-extraction] Extract adaptive development into a devkit-adaptive distribution

## 1. Background & Hypothesis

The `adaptive-dev` bundle lives in `devkit-catalog`, a content-only distribution with no dependencies and no Python
code besides bundle discovery. `ARCH-05-2-components` assigns the bundle to that catalog, and
`CAP-DLV-adaptive-development` excludes a new wheel and a runtime. `ADR-adaptive-development-and-research` chose
guidance over a runtime or CLI when the bundle was introduced.

`MS-adaptive-development-runtime` adds commands for delegated assignments (`PROP-adaptive-assignment-cli`). A
command needs Python code, a command entry point and tests, which the content-only catalog does not carry.
`devkit-spec` is the precedent: one distribution that owns its bundle under `bundles/` and its commands under
`features/`.

Hypothesis: moving the bundle into a `devkit-adaptive` distribution shaped like `devkit-spec` is a packaging change
with no change in agent behavior. The bundle name `adaptive-dev`, its presets and asset IDs, and its independence
from `devkit-spec` stay as they are, and the next proposal adds commands without another move.

## 2. Technical Spike Questions

- **Q1 Layout**: Which distribution, import package and directory names does the package use, and which
  `ARCH-05-2-components` layout rules apply to a package that starts with a bundle and no feature?
- **Q2 Base dependency**: Does `devkit-adaptive` depend on `devkit-dist` only, or on `devkit-agt`? Capability rule 2
  requires installation with docs and catalog without `devkit-spec`; the answer decides whether later commands may
  use harness features such as worktrees.
- **Q3 Existing selections**: What does a project that selected `adaptive-dev` and installs only `devkit-catalog`
  observe after the move? Compare a dependency from the catalog on the new distribution, a release-inventory change
  and a documented installation step, and name the resulting error code when the bundle is missing.
- **Q4 Decisions**: Which clauses change: the "new wheel" exclusion in `CAP-DLV-adaptive-development`, the catalog
  ownership sentence in `ARCH-05-2-components` and the runtime clause of `ADR-adaptive-development-and-research`?
  Which need a superseding decision limited to packaging?
- **Q5 Entry points**: Does the package register only `devkit.bundles`, or also an empty `devkit.commands` group
  before the commands exist?
- **Q6 Repository wiring**: Which root files change: workspace members, release inventory and version pins,
  `.devkit/architecture.toml` data roots, `just` recipes, affected-test selection, smoke tests and install guides?
- **Q7 Tests**: Which tests move with the bundle, and does `just test-dist` still pass without `devkit-agt`?

## 3. Proposed Design & Impact

- Create `packages/devkit-adaptive` with the bundle under a `bundles/` directory, following `devkit-spec`.
- Move the bundle sources, their integration and end-to-end tests and the evidence scorer test support.
- Remove the `adaptive-dev` entry point and data root from `devkit-catalog`.
- Keep bundle name, presets, asset IDs, projections and the context file name unchanged.
- Update the capability, architecture, deployment documents, package READMEs and install guides.
- Add no command, hook or behavior change; `PROP-adaptive-assignment-cli` owns the commands.

Host lifecycle hooks for adaptive development are outside this proposal; `PROP-adaptive-lifecycle-hooks` owns their
investigation.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr adaptive-package-extraction "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept adaptive-package-extraction --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff adaptive-package-extraction.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
