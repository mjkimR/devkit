---
id: SPEC-adaptive-package-extraction
title: Extract adaptive development into a devkit-adaptive distribution
summary: "Move the adaptive-dev bundle from the content-only devkit-catalog into a new devkit-adaptive distribution with unchanged bundle name, presets and assets, so adaptive development can gain commands while the catalog stays content-only."
status: planned
created: 2026-11-10
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-adaptive-package-extraction] Extract adaptive development into a devkit-adaptive distribution

## 1. Problem Statement & Motivation

Handed off from proposal PROP-adaptive-package-extraction on 2026-11-10.
- **Preserved Materials**: `docs/materials/2026-11/20261110-adaptive-package-extraction`
- Target Docs Blueprint: `PROP-adaptive-package-extraction-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

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

## 2. User Stories

- **US-1**: As an agent installing adaptive development, I want its bundle in an independent wheel so commands can be added later without changing bundle behavior.

## 3. Non-Goals

- **Scope Excluded**: a command, a `devkit.commands` entry point, a feature, a hook or a runtime requirement in
  `devkit-adaptive`; `PROP-adaptive-assignment-cli` owns the commands and introduces the requirement on
  `devkit-docs`.
- **Scope Excluded**: a change to the bundle's name, presets, asset IDs, asset text, projections or context file.
- **Scope Excluded**: a change in `devkit-dist` or `devkit-agt`.
- **Scope Excluded**: compatibility for an existing selection of `adaptive-dev`: a migration path, a guide step or
  troubleshooting text for it, a test of a selection that crosses the move, a runtime requirement of
  `devkit-catalog` on `devkit-adaptive`, an alias distribution, a shim module, a second registration of the bundle
  and an error hint that names the new package. Nothing uses the bundle outside this repository.
- **Scope Excluded**: moving `deep-research` or another catalog bundle.
- **Scope Excluded**: host lifecycle hooks; `PROP-adaptive-lifecycle-hooks` owns their investigation.
- **Scope Excluded**: a release, a release installation variant, a version other than the one
  `just version-sync` selects, and a change to release preparation beyond the bundle lookup of section 3.3.

## 4. Acceptance Criteria & Behavioral Contracts

The criteria are AC-01 to AC-04 and AC-06 to AC-08. AC-05 was withdrawn with the compatibility for existing
selections and its number is not reused, so the criteria keep the numbers under which the envelopes cite them.

### [AC-01] The distribution holds the bundle alone

- **Given** the workspace after the change,
- **When** `packages/devkit-adaptive/pyproject.toml` and `src/devkit_adaptive/` are read,
- **Then** the project is `devkit-adaptive` with `dependencies = []`, no optional dependencies and exactly one
  entry-point group, `devkit.bundles`, holding exactly `adaptive-dev = "devkit_adaptive.bundles.adaptive_dev"`; the
  package holds three initializers and `bundles/adaptive_dev/bundle/` and no other module. A test in
  `packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev.py` asserts the metadata, and
  `just rules-check` reports no `RULE-architecture` finding.

### [AC-02] The bundle is unchanged

- **Given** the checked head and the merge base of that head and the integration target
  (`git merge-base HEAD <target>`; the saved premerge target SHA at the final check),
- **When** `git rev-parse <merge-base>:packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle` is compared
  with `git rev-parse HEAD:packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle`,
- **Then** both print the same tree object, so the name, version, presets, asset IDs and every asset byte are
  identical, and an edit that landed on the target under the old path is carried to the new one.

### [AC-03] The catalog no longer ships the bundle

- **Given** the workspace after the change,
- **When** the catalog tests run (`just test catalog`),
- **Then** `packages/devkit-catalog/pyproject.toml` registers no `adaptive-dev` entry point and declares
  `dependencies = []`, `src/devkit_catalog/adaptive_dev/` does not exist, `test_bundles.py` passes and the
  role-conflict test of `test_deep_research.py` passes with the bundle located through its static import of
  `devkit_adaptive.bundles`.

### [AC-04] Installation without devkit-spec and without the catalog

- **Given** wheels built from the workspace for `devkit-advisory`, `devkit-cli`, `devkit-core`, `devkit-dist`,
  `devkit-agt`, `devkit-docs` and `devkit-adaptive`,
- **When** `packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py` installs them into
  a fresh environment and selects `adaptive-dev`, `adaptive-dev:agents` and `adaptive-dev:import`,
- **Then** the environment contains neither `devkit-spec` nor `devkit-catalog`, and every assertion the test made
  before the move on deployed assets, projections, approach inspection and preserved project-owned context still
  passes.

### [AC-06] Repository checks

- **Given** the workspace after `just init`,
- **When** `uv lock --check`, `just lint-check`, `just check`, `just rules-check`, `just test adaptive`,
  `just test catalog`, `just test dev`, `just test-dist`, `just test-affected` and `just smoke` run,
- **Then** each exits `0`; `just test adaptive` collects the moved tests, the citation test covers the
  `adaptive-dev` bundle through `devkit_adaptive.bundles`, and the smoke consumer reports `adaptive-dev` with the
  package `devkit-adaptive`.
- **And** a `just smoke` failure that also occurs at the Development base, at a check outside the lines section 3.3
  edits, does not fail this criterion; the final report names it with the base run that showed it.

### [AC-07] Living Spec, guides and decision

- **Given** the documents after the change,
- **When** `just rules-check` runs and
  `rg -n "devkit_catalog[/.]adaptive_dev|devkit-catalog/tests/[a-z0-9/_]*adaptive" docs/capabilities docs/usecases docs/architecture guides packages tools tests scripts README.md AGENTS.md .devkit/architecture.toml`
  runs,
- **Then** the rules report no finding and the search prints nothing; the documents of `target-docs.md` name
  `devkit-adaptive` as the owner and installation package of `adaptive-dev`; the decision promoted from
  `ADR-adaptive-dev-distribution` is accepted, and `ADR-adaptive-development-and-research` stays accepted with one
  line naming the clauses that decision replaces.
- **And** the five guides of section 3.5 name `devkit-adaptive` as the package of `adaptive-dev` for a fresh
  installation and hold no step for a project that selected the bundle before the move (review).

### [AC-08] A moved bundle keeps its version at release preparation

- **Given** the fixture workspace of `packages/devkit/tests/integration/package/test_selective_releases.py` with a
  completed baseline, in which a bundle moves with unchanged content from its package to a new package,
- **When** release preparation computes the plan,
- **Then** the bundle keeps its baseline version, the new package takes the release version and the former owner
  is reported as changed; a bundle whose content changed in the move takes the release version.

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

Planning answered the seven questions from repository evidence and the user's decisions.
`docs/materials/2026-11/20261110-adaptive-package-extraction/planning-evidence.md` holds the evidence and the option tables, historical Git `9ab4f8e5ec0d1e4922013106199835ce6b74838e:docs/proposals/PROP-adaptive-package-extraction/envelopes/scout-01.yaml` the wiring
inventory. Where an earlier envelope differs from this document, this document holds.

- **Q1 Layout**: distribution `devkit-adaptive` in `packages/devkit-adaptive/`, import package `devkit_adaptive`,
  bundle at `src/devkit_adaptive/bundles/adaptive_dev/bundle/`. The package holds three docstring-only initializers
  and the bundle; `ARCH-05-2-components` forbids empty layers, so `features/` and `cli.py` arrive with the first
  command.
- **Q2 Base dependency**: none in this unit (`dependencies = []`); the wheel is bundle-only at the move. A runtime
  requirement without code that imports it would end `devkit bundle snapshot` support for the source
  (`BUNDLE_SNAPSHOT_UNSUPPORTED`) and change the installed closure in a unit that promises no behavior change. The
  base dependency is settled as `devkit-docs`, which itself requires `devkit-agt` and so `devkit-dist`, and
  `PROP-adaptive-assignment-cli` introduces it together with the first commands. This unit adds neither the
  requirement nor a document or guide change for it. Capability rule 2 holds, because `devkit-docs` does not reach
  `devkit-spec`.
- **Q3 Existing selections**: none to carry. Nothing uses the `adaptive-dev` bundle outside this repository, and
  this repository does not select it, so the move has no migration path: no bridge, no crossing procedure and no
  guide step for a project that selected the bundle while the catalog shipped it. The guides name `devkit-adaptive`
  for a fresh installation only. `docs/materials/2026-11/20261110-adaptive-package-extraction/planning-evidence.md` set 3 records, as an observation and not as a
  requirement, what discovery reports when a selected bundle's distribution is missing.
- **Q4 Decisions**: `ADR-adaptive-dev-distribution` supersedes the owning-wheel clauses of
  `ADR-adaptive-development-and-research` and nothing else. `ADR-skill-local-swarm-roles` decides no owner and gets
  a wording repair. The exclusion of a command line or runtime is `PROP-adaptive-assignment-cli`'s to change.
- **Q5 Entry points**: `devkit.bundles` only. A `devkit.commands` entry is a mounted `devkit adaptive` group, which
  is a new command. `PROP-adaptive-assignment-cli` adds that entry with the command group
  `devkit adaptive assignment`; this unit registers nothing for it.
- **Q6 Repository wiring**: the files of section 3.3. Workspace membership, the release inventory, the `just`
  recipes and the affected-test selector discover the package by directory and need no edit. Release preparation
  needs one: it looks up a bundle's previous version under its package name, so the moved bundle would take the
  release version with unchanged content, against `ARCH-07-deployment` 1.1.
- **Q7 Tests**: six adaptive-dev test files move; `test_deep_research.py` stays and locates the bundle through a
  static import of `devkit_adaptive.bundles`, which keeps it selected by `just test-affected`. `just test-dist`
  syncs and collects `devkit-dist` only and is unaffected.

### 3. Proposed Design & Impact

#### 3.1 The distribution

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

#### 3.2 The catalog

- `packages/devkit-catalog/pyproject.toml` drops the `adaptive-dev` entry point; `src/devkit_catalog/adaptive_dev/`
  is removed. The catalog keeps `dependencies = []` and gains no runtime requirement on `devkit-adaptive`; its
  development group gains `devkit-adaptive` with a workspace source for the test of section 3.4.
- `packages/devkit-catalog/README.md` drops the table row and the section and points to the new package.

#### 3.3 Repository wiring

- Root `pyproject.toml`: `./packages/devkit-adaptive/src` in pyright `extraPaths` and
  `packages/devkit-adaptive/tests` in pytest `testpaths`; `uv.lock` regenerated with `uv lock`.
- `.devkit/architecture.toml`: a `devkit_adaptive` package (`kind = "content"`, `data_roots = ["bundles"]`);
  `adaptive_dev` leaves the `devkit_catalog` data roots.
- `scripts/_lib.sh`: the short name `adaptive devkit-adaptive`.
- `tools/devkit-dev/tests/integration/test_bundle_citations.py`: `devkit_adaptive.bundles` joins `SHIPPING`.
- `tests/e2e/smoke.sh`: the consumer installs the `devkit_adaptive` wheel, and the script asserts that
  `devkit-adaptive` provides `adaptive-dev`. The asserted set of bundles provided by `devkit-catalog` becomes the
  seven it registers after the move: `response-style`, `maintenance`, `cli-tool`, `command-design`,
  `deep-research`, `uiux-improve` and `design-explore`. The base asserts five names for a catalog that registers
  eight, so Development runs `just smoke` at its base first and records every failure that exists before its edits.
- `scripts/releases/prepare.py`: when the baseline holds no bundle of that name under the same package, release
  preparation takes the previous identity from the baseline package that registered a bundle of that name. An
  unchanged bundle then keeps its version across a change of owner (`ARCH-07-deployment` 1.1), while the new
  distribution takes the release version and the catalog advances for its changed payload.
- `.github/workflows/ci.yml`: the comment that lists packages.
- No edit: `justfile`, `scripts/affected_tests.py`, `scripts/dist_only.sh`, the other modules of
  `scripts/releases/`, this repository's `.devkit/config.toml` and receipt.

#### 3.4 Tests

- Move to `packages/devkit-adaptive/tests/` in the same tiers: `integration/bundles/test_adaptive_dev.py`,
  `test_adaptive_dev_documents.py`, `test_adaptive_import.py`, `test_adaptive_behavior_scorer.py`,
  `support/adaptive_behavior_scorer.py` and `e2e/bundles/adaptive_dev/test_installed_consumer.py`. Repoint their
  path constants, the package name and the entry point value.
- The end-to-end test builds `devkit-adaptive` instead of `devkit-catalog` and asserts that neither `devkit-spec`
  nor `devkit-catalog` is installed.
- `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` stays. It imports
  `devkit_adaptive.bundles` statically and derives the adaptive-dev bundle path from that module for the
  role-conflict test, as `tools/devkit-dev/tests/integration/test_bundle_citations.py` does, so a change to the
  bundle still selects the test.
- `packages/devkit/tests/integration/package/test_selective_releases.py` gains a case in which a bundle moves
  unchanged from one fixture package to a new one.

#### 3.5 Documents and guides

- Living Spec: the changes of `target-docs.md`.
- Guides: `guides/INSTALL_GUIDE.md`, `guides/install/new-repository.md`, `guides/install/existing-repository.md`,
  `guides/install/adaptive-dev-sdd-adoption.md` and `guides/install/bundle-recommendations.md` name
  `devkit-adaptive` wherever they name `devkit-catalog` as the package of `adaptive-dev`, and
  `guides/INSTALL_GUIDE.md` gains its installation and upgrade commands beside the catalog's. Each edit describes a
  fresh installation: in `guides/install/existing-repository.md` only the adaptive development paragraph changes,
  and no guide gains a subsection, a troubleshooting row or a step for a project that selected the bundle before
  the move.
- Root `AGENTS.md` and `README.md`: the package tables, module and short-name lists and README links.

### Planning decisions

| Subject | Decision | By |
| --- | --- | --- |
| Owner | `adaptive-dev` moves from `devkit-catalog` into its own distribution `devkit-adaptive`, shaped like `devkit-spec` | user |
| Scope | No command and no behavior change; bundle name, presets and asset IDs stay; hooks are `PROP-adaptive-lifecycle-hooks` | user |
| Size | `M`, one spec | host |
| Independence | The bundle keeps installing without `devkit-spec` | host |
| Names and layout (Q1) | Section 3.1; settled by `ADR-package-ownership-and-release-version`, `ARCH-05-2-components` 1.1 and `CAP-DIST-content-packages` §1 | evidence |
| Wheel contents (Q2, Q5) | Bundle-only at the move: `dependencies = []` and only `devkit.bundles` (`docs/materials/2026-11/20261110-adaptive-package-extraction/planning-evidence.md` sets 2 and 5). Recorded in `ADR-adaptive-dev-distribution` | user |
| Base dependency | `devkit-docs`, which itself requires `devkit-agt` and so `devkit-dist`, introduced by `PROP-adaptive-assignment-cli` together with the first commands. This unit adds neither the requirement nor its consequences nor guide changes for it; its guides describe the installation that holds after the move alone: `devkit-docs` beside `devkit-adaptive`, without `devkit-spec` | user |
| Follow-on command group | `PROP-adaptive-assignment-cli` adds `devkit adaptive assignment`. Information only: this unit registers `devkit.bundles` alone | user |
| Architecture declaration | `kind = "content"` with `data_roots = ["bundles"]`; the first command changes the kind to `features` in the entry it has to edit anyway. `RULE-architecture` accepts both | planning |
| Root development group | No entry for `devkit-adaptive`, as for the catalog; `just init` installs every member | planning |
| Version | `0.1.6` for the package beside the bundle's unchanged `0.1.6`; the release tooling gives a package absent from the baseline the release version | evidence |
| Bundle version at release | Release preparation finds a moved bundle's previous identity by bundle name (section 3.3, AC-08), so the existing MUST of `ARCH-07-deployment` 1.1 holds and the unchanged moved bundle keeps its version. The alternative, an exception to that MUST recorded in the PADR, was not taken: it changes a release contract to fit one lookup | user |
| Superseding decision (Q4) | One PADR limited to the owning wheel; no decision on a command line | evidence |
| `dev_effort` | Stays `medium`: the change is a move verified by tree identity and existing tests plus one lookup in release preparation with its own test; nothing is released by it, and no `high` trigger of the effort reference applies | planning |
| Existing selections (Q3) | No compatibility and no bridge: nothing uses the `adaptive-dev` bundle outside this repository, so the move has no migration path, and the guides name `devkit-adaptive` for fresh installations only. Recorded in `ADR-adaptive-dev-distribution` | user |
| Acceptance criteria numbering | AC-05 (an existing selection crosses the move) is withdrawn with its test and guide clause. AC-06 to AC-08 keep their numbers, because the recorded envelopes cite them | planning |
| Test selection | `test_deep_research.py` imports `devkit_adaptive.bundles`; the catalog's development group names `devkit-adaptive` | planning |

For `PROP-adaptive-assignment-cli`: the consequences of the requirement on `devkit-docs` and of the
`devkit.commands` entry point, for the installed closure, the `agents` and `import` presets and snapshot support
of this source, are that unit's to state with the change that introduces them. `docs/materials/2026-11/20261110-adaptive-package-extraction/planning-evidence.md`
set 2 holds the evidence this Planning collected.


## Assumptions and baseline

The accepted proposal remains applicable at base `9ab4f8e5ec0d1e4922013106199835ce6b74838e`. No new feature edge is introduced.
The Host measured `just smoke` there: foundation 210 tests passed, then the catalog bundle-set assertion failed because it expected five of eight registered bundles. The planned assertion update covers this failure.
Codex worker boundaries are emulated: every command uses the absolute assigned worktree, write scope is audited against the accepted input, and writes and commits request operation-specific sandbox approval.

The smoke expectation uses the actual registered name `app-uiux-improve`; the carried proposal shortened it to `uiux-improve`. This repairs the planned inventory assertion without changing any bundle name.
