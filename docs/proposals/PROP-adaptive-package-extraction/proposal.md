---
id: PROP-adaptive-package-extraction
title: Extract adaptive development into a devkit-adaptive distribution
summary: "Move the adaptive-dev bundle from the content-only devkit-catalog into a new devkit-adaptive distribution with unchanged bundle name, presets and assets, so adaptive development can gain commands while the catalog stays content-only."
status: reviewing                     # draft | reviewing | accepted | rejected
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
    - packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev_documents.py
    - packages/devkit-catalog/tests/integration/bundles/test_adaptive_import.py
    - packages/devkit-catalog/tests/integration/bundles/test_adaptive_behavior_scorer.py
    - packages/devkit-catalog/tests/integration/bundles/test_deep_research.py
    - packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/
    - packages/devkit-catalog/tests/support/adaptive_behavior_scorer.py
    - tools/devkit-dev/tests/integration/test_bundle_citations.py
    - tests/e2e/smoke.sh
    - scripts/_lib.sh
    - pyproject.toml
    - uv.lock
    - .devkit/architecture.toml
    - .github/workflows/ci.yml
    - AGENTS.md
    - README.md
    - guides/INSTALL_GUIDE.md
    - guides/install/
    - docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - docs/usecases/delivery/UC-advance-an-idea.md
    - docs/usecases/delivery/UC-import-third-party-agent-assets.md
    - docs/architecture/ARCH-05-1-containers.md
    - docs/architecture/ARCH-05-2-components.md
    - docs/architecture/ARCH-07-deployment.md
    - docs/decisions/2026-11/20261102-adaptive-development-and-research.md
    - docs/decisions/2026-11/20261106-skill-local-swarm-roles.md
  excludes:
    - packages/devkit-spec/
    - packages/devkit-dist/src/
    - packages/devkit/src/
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

Planning answered the seven questions from repository evidence. `materials/planning-evidence.md` holds the evidence
and the option tables, `envelopes/scout-01.yaml` the wiring inventory.

- **Q1 Layout**: distribution `devkit-adaptive` in `packages/devkit-adaptive/`, import package `devkit_adaptive`,
  bundle at `src/devkit_adaptive/bundles/adaptive_dev/bundle/`. The package holds three docstring-only initializers
  and the bundle; `ARCH-05-2-components` forbids empty layers, so `features/` and `cli.py` arrive with the first
  command.
- **Q2 Base dependency**: none in this unit (`dependencies = []`). A requirement on `devkit-dist` or `devkit-agt`
  without code that imports it would end `devkit bundle snapshot` support for the source
  (`BUNDLE_SNAPSHOT_UNSUPPORTED`), and `devkit-agt` would install the auto-selected `harness` bundle for consumers
  of the `agents` and `import` presets that run on `devkit-dist` alone. `PROP-adaptive-assignment-cli` decides the
  base with its commands. Capability rule 2 holds either way, because nothing reaches `devkit-spec`.
- **Q3 Existing selections**: a project that selected `adaptive-dev` and upgrades without installing
  `devkit-adaptive` gets `SELECTION_INVALID` (`selected bundle is not installed: adaptive-dev`) from `devkit sync`
  and under `errors` of `devkit status`; nothing is deleted. After it installs the package, its selection, overrides
  and role keys apply unchanged, and the next sync rewrites the receipt's package record. Of the five options
  compared, only a documented installation step breaks no other contract; the user decides (Planning decisions).
- **Q4 Decisions**: `PADR-adaptive-dev-distribution` supersedes the owning-wheel clauses of
  `ADR-adaptive-development-and-research` and nothing else. `ADR-skill-local-swarm-roles` decides no owner and gets
  a wording repair. The exclusion of a command line or runtime is `PROP-adaptive-assignment-cli`'s to change.
- **Q5 Entry points**: `devkit.bundles` only. A `devkit.commands` entry is a mounted `devkit adaptive` group, which
  is a new command.
- **Q6 Repository wiring**: the files of section 3.3. Workspace membership, the release inventory, the `just`
  recipes and the affected-test selector discover the package by directory and need no edit.
- **Q7 Tests**: six adaptive-dev test files move; `test_deep_research.py` stays and loads the bundle from its new
  path. `just test-dist` syncs and collects `devkit-dist` only and is unaffected.

## 3. Proposed Design & Impact

### 3.1 The distribution

- `packages/devkit-adaptive/pyproject.toml`: name `devkit-adaptive`, version `0.1.6`, `requires-python = ">=3.12"`,
  `dependencies = []`, no optional dependencies, the single entry point
  `adaptive-dev = "devkit_adaptive.bundles.adaptive_dev"` under `devkit.bundles`, the Hatch wheel mapping
  `packages = ["src/devkit_adaptive"]` and a development group `["devkit-dist"]` with its workspace source.
- `src/devkit_adaptive/__init__.py`, `bundles/__init__.py` and `bundles/adaptive_dev/__init__.py` hold a docstring
  only. No `features/`, `cli.py`, `base/`, `utils/` or `adapters/`.
- `src/devkit_adaptive/bundles/adaptive_dev/bundle/` is the moved bundle tree, byte for byte; its `bundle.toml`
  keeps `name = "adaptive-dev"`, `version = "0.1.6"`, the presets and the asset IDs.
- `packages/devkit-adaptive/README.md` takes the "Adaptive development" section of the catalog README, with the
  installation command of the new distribution.

### 3.2 The catalog

- `packages/devkit-catalog/pyproject.toml` drops the `adaptive-dev` entry point; `src/devkit_catalog/adaptive_dev/`
  is removed. The catalog keeps `dependencies = []` and gains no requirement on `devkit-adaptive`.
- `packages/devkit-catalog/README.md` drops the table row and the section and points to the new package.

### 3.3 Repository wiring

- Root `pyproject.toml`: `./packages/devkit-adaptive/src` in pyright `extraPaths` and
  `packages/devkit-adaptive/tests` in pytest `testpaths`; `uv.lock` regenerated with `uv lock`.
- `.devkit/architecture.toml`: a `devkit_adaptive` package (`kind = "content"`, `data_roots = ["bundles"]`);
  `adaptive_dev` leaves the `devkit_catalog` data roots.
- `scripts/_lib.sh`: the short name `adaptive devkit-adaptive`.
- `tools/devkit-dev/tests/integration/test_bundle_citations.py`: `devkit_adaptive.bundles` joins `SHIPPING`.
- `tests/e2e/smoke.sh`: the consumer installs the `devkit_adaptive` wheel; `adaptive-dev` leaves the set of bundles
  provided by `devkit-catalog`, and the script asserts that `devkit-adaptive` provides it.
- `.github/workflows/ci.yml`: the comment that lists packages.
- No edit: `justfile`, `scripts/affected_tests.py`, `scripts/dist_only.sh`, `scripts/releases/`, this repository's
  `.devkit/config.toml` and receipt.

### 3.4 Tests

- Move to `packages/devkit-adaptive/tests/` in the same tiers: `integration/bundles/test_adaptive_dev.py`,
  `test_adaptive_dev_documents.py`, `test_adaptive_import.py`, `test_adaptive_behavior_scorer.py`,
  `support/adaptive_behavior_scorer.py` and `e2e/bundles/adaptive_dev/test_installed_consumer.py`. Repoint their
  path constants, the package name and the entry point value.
- The end-to-end test builds `devkit-adaptive` instead of `devkit-catalog` and asserts that neither `devkit-spec`
  nor `devkit-catalog` is installed.
- `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` stays and loads the adaptive-dev bundle
  from its new path for the role-conflict test.

### 3.5 Documents and guides

- Living Spec: the changes of `target-docs.md`.
- Guides: `guides/INSTALL_GUIDE.md` and `guides/install/` name `devkit-adaptive` as the package of `adaptive-dev`,
  with its installation and upgrade commands. `guides/install/existing-repository.md` gains a subsection for an
  existing selection beside "Upgrading across the package split", and the `SELECTION_INVALID` row of
  `guides/INSTALL_GUIDE.md` names the move.
- Root `AGENTS.md` and `README.md`: the package tables, module and short-name lists and README links.

### 3.6 An existing selection

This subsection states the recommended option of question q1; the user's answer may replace it.

A project that selected `adaptive-dev` adds `devkit-adaptive` to the dependency group that holds its devkit
packages, runs `uv run devkit sync` and commits `pyproject.toml`, `uv.lock` and `.devkit/installation.json`. Its
`[presets]` entry, overrides and `adaptive-dev:<role>` keys stay as they are. Until it adds the package,
`devkit sync` stops with `SELECTION_INVALID` and deletes nothing. The guide tells the reader to install the package
instead of following the error's `[FIX]`, which names `devkit remove adaptive-dev`.

## Non-Goals

- **Scope Excluded**: a command, a `devkit.commands` entry point, a feature, a hook or a runtime requirement in
  `devkit-adaptive`; `PROP-adaptive-assignment-cli` owns the commands and their base dependency.
- **Scope Excluded**: a change to the bundle's name, presets, asset IDs, asset text, projections or context file.
- **Scope Excluded**: a change in `devkit-dist` or `devkit-agt`, including a hint in `SELECTION_INVALID` that names
  the new package.
- **Scope Excluded**: a requirement of `devkit-catalog` on `devkit-adaptive`, an alias distribution, a shim module
  or a second registration of the bundle.
- **Scope Excluded**: moving `deep-research` or another catalog bundle.
- **Scope Excluded**: host lifecycle hooks; `PROP-adaptive-lifecycle-hooks` owns their investigation.
- **Scope Excluded**: a release, a release installation variant and a version other than the one
  `just version-sync` selects.

## Acceptance Criteria

### [AC-01] The distribution holds the bundle alone

- **Given** the workspace after the change,
- **When** `packages/devkit-adaptive/pyproject.toml` and `src/devkit_adaptive/` are read,
- **Then** the project is `devkit-adaptive` with `dependencies = []`, no optional dependencies and exactly one
  entry-point group, `devkit.bundles`, holding exactly `adaptive-dev = "devkit_adaptive.bundles.adaptive_dev"`; the
  package holds three initializers and `bundles/adaptive_dev/bundle/` and no other module. A test in
  `packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev.py` asserts the metadata, and
  `just rules-check` reports no `RULE-architecture` finding.

### [AC-02] The bundle is unchanged

- **Given** the base commit of the Development branch,
- **When** `git rev-parse <base>:packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle` is compared with
  `git rev-parse HEAD:packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle`,
- **Then** both print the same tree object, so the name, version, presets, asset IDs and every asset byte are
  identical.

### [AC-03] The catalog no longer ships the bundle

- **Given** the workspace after the change,
- **When** the catalog tests run (`just test catalog`),
- **Then** `packages/devkit-catalog/pyproject.toml` registers no `adaptive-dev` entry point and declares
  `dependencies = []`, `src/devkit_catalog/adaptive_dev/` does not exist, `test_bundles.py` passes and the
  role-conflict test of `test_deep_research.py` passes with the bundle loaded from `packages/devkit-adaptive/`.

### [AC-04] Installation without devkit-spec and without the catalog

- **Given** wheels built from the workspace for `devkit-advisory`, `devkit-cli`, `devkit-core`, `devkit-dist`,
  `devkit-agt`, `devkit-docs` and `devkit-adaptive`,
- **When** `packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py` installs them into
  a fresh environment and selects `adaptive-dev`, `adaptive-dev:agents` and `adaptive-dev:import`,
- **Then** the environment contains neither `devkit-spec` nor `devkit-catalog`, and every assertion the test made
  before the move on deployed assets, projections, approach inspection and preserved project-owned context still
  passes.

### [AC-05] An existing selection crosses the move

- **Given** a project synchronized with the `adaptive-dev` bundle provided by a distribution named
  `devkit-catalog`, with a project-owned `.devkit/adaptive-dev.md`,
- **When** the same bundle is provided by `devkit-adaptive` and `devkit sync` runs with the unchanged configuration,
- **Then** the sync succeeds, the deployed and projected files are byte-identical, `.devkit/adaptive-dev.md` is
  unchanged and the receipt's package record for `adaptive-dev` names `devkit-adaptive`. An integration test in
  `packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev.py` asserts this with two `InstalledBundle`
  values of the real bundle.
- **And** `guides/install/existing-repository.md` states the step of section 3.6 with its commands, and the
  `SELECTION_INVALID` row of `guides/INSTALL_GUIDE.md` names `devkit-adaptive` (review).

### [AC-06] Repository checks

- **Given** the workspace after `just init`,
- **When** `uv lock --check`, `just lint-check`, `just check`, `just rules-check`, `just test adaptive`,
  `just test catalog`, `just test dev`, `just test-dist`, `just test-affected` and `just smoke` run,
- **Then** each exits `0`; `just test adaptive` collects the moved tests, the citation test covers the
  `adaptive-dev` bundle through `devkit_adaptive.bundles`, and the smoke consumer reports `adaptive-dev` with the
  package `devkit-adaptive`.

### [AC-07] Living Spec, guides and decision

- **Given** the documents after the change,
- **When** `just rules-check` runs and
  `rg -n "devkit_catalog[/.]adaptive_dev|devkit-catalog/tests/[a-z0-9/_]*adaptive" docs/capabilities docs/usecases docs/architecture guides packages tools tests scripts README.md AGENTS.md .devkit/architecture.toml`
  runs,
- **Then** the rules report no finding and the search prints nothing; the documents of `target-docs.md` name
  `devkit-adaptive` as the owner and installation package of `adaptive-dev`; the decision promoted from
  `PADR-adaptive-dev-distribution` is accepted, and `ADR-adaptive-development-and-research` stays accepted with one
  line naming the clauses that decision replaces.

## Planning decisions

| Subject | Decision | By |
| --- | --- | --- |
| Owner | `adaptive-dev` moves from `devkit-catalog` into its own distribution `devkit-adaptive`, shaped like `devkit-spec` | user |
| Scope | No command and no behavior change; bundle name, presets and asset IDs stay; hooks are `PROP-adaptive-lifecycle-hooks` | user |
| Size | `M`, one spec | host |
| Independence | The bundle keeps installing without `devkit-spec` | host |
| Names and layout (Q1) | Section 3.1; settled by `ADR-package-ownership-and-release-version`, `ARCH-05-2-components` 1.1 and `CAP-DIST-content-packages` §1 | evidence |
| Wheel contents (Q2, Q5) | No runtime requirement and only `devkit.bundles` at the move; follows from the user's scope, because either addition changes behavior (`materials/planning-evidence.md` sets 2 and 5). Recorded in `PADR-adaptive-dev-distribution` | evidence |
| Architecture declaration | `kind = "content"` with `data_roots = ["bundles"]`; the first command changes the kind to `features` in the entry it has to edit anyway. `RULE-architecture` accepts both | planning |
| Root development group | No entry for `devkit-adaptive`, as for the catalog; `just init` installs every member | planning |
| Version | `0.1.6` for the package beside the bundle's unchanged `0.1.6`; the release tooling gives a package absent from the baseline the release version | evidence |
| Superseding decision (Q4) | One PADR limited to the owning wheel; no decision on a command line | evidence |
| `dev_effort` | Stays `medium`: the change is a move verified by tree identity and existing tests, nothing is released by it, and the consumer-facing step is the user's explicit choice | planning |
| Existing selections (Q3) | Open: question q1. Recommended: no bridge, a documented installation step (section 3.6) | user, pending |

`PADR-adaptive-dev-distribution` names "the catalog stays dependency-free" as a driver. If the answer to q1 makes
the catalog require `devkit-adaptive`, the next Planning turn rewrites that driver, section 3.6, the Non-Goals and
AC-03 and AC-05.

For `PROP-adaptive-assignment-cli`: adding a runtime requirement or a `devkit.commands` entry point ends snapshot
support for this source, and a requirement on `devkit-agt` changes what a `devkit-dist`-only consumer of the
`agents` and `import` presets installs (`materials/planning-evidence.md` set 2).

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
