---
id: SPEC-devkit-dist-package-separation
title: Separate asset distribution into independent devkit-dist package
summary: "Splits devkit-agt into a devkit-dist wheel (foundation, distribution, root devkit CLI, devkit/advisory/git-commits bundles) and a devkit-agt wheel that mounts the harness commands and ships the authoring and new harness bundles, with coded standalone signals and per-wheel layering."
status: planned
created: 2026-10-19
related_capabilities:
  - CAP-DIST-content-packages
  - CAP-DIST-manifest-spec
  - CAP-DIST-sync-and-transactions
  - CAP-DIST-workspace-ownership
  - CAP-DIST-in-repo-bundles
  - CAP-DIST-context-and-playbooks
  - CAP-DIST-agent-projections
  - CAP-HOST-lifecycle-observation
  - CAP-SRCH-document-search
  - CAP-CMP-bounded-execution
  - CAP-INT-mcp-services
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-devkit-dist-package-separation] Separate asset distribution into independent devkit-dist package

## 1. Problem Statement & Motivation

Handed off from proposal PROP-devkit-dist-package-separation on 2026-10-19 (preserved materials:
`docs/materials/2026-10/20261019-devkit-dist-package-separation`). The decisions are `ADR-dist-foundation-ownership`,
`ADR-dist-module-split`, `ADR-dist-command-composition`, `ADR-dist-config-receipt-ownership` and
`ADR-dist-bundles-compatibility`; this spec turns them into checkable behavior and does not reopen them.

`devkit-agt` (`packages/devkit`) ships the agent asset distribution (bundle manifests, projections, sync, the receipt,
context loading, playbooks, native hooks) together with the developer harness (rule engine, delivery workflows,
commit gates, task worktrees, generated files, integration, `devkit run`). A repository that only deploys skills,
playbooks and instructions gets the harness code, its commands and its auto-deployed guidance. The third-party
dependency set is the same either way (click, pyyaml, jinja2, tomlkit); the gain is the harness code, commands and
guidance not installed or deployed.

After this change three wheels share the PEP 420 `devkit` namespace, released in lockstep at one version:

1. `devkit-advisory`: unchanged.
2. `devkit-dist` (new, `packages/devkit-dist`): `devkit.core`, `devkit.search`, `devkit.host`, `devkit.distribution`,
   `devkit.cli`, `devkit.__main__`, the `devkit`, `advisory` and `git-commits` bundles, the sole `devkit` console
   script, the `.devkit/config.toml` schema and the receipt.
3. `devkit-agt` (`packages/devkit`): `devkit.rules`, `devkit.workflow`, `devkit.gate`, `devkit.worktree`,
   `devkit.generated`, `devkit.integration`, `devkit.compact`, the `authoring` bundle and the new auto-selected
   `harness` bundle (`devkit.harness_guide`); it depends on `devkit-dist` at its own version and mounts its commands
   through `devkit.commands`.

`devkit-spec` keeps depending on `devkit-agt`; `devkit-catalog` and `devkit-starter` test against `devkit-dist`.

## 2. User Stories

- **US-1**: As a maintainer of a repository that only deploys agent assets, I want to install `devkit-dist` alone and
  get sync, context loading, playbooks and native hooks, so that no harness code, command or guidance is installed or
  deployed.
- **US-2**: As an agent in a standalone installation, I want a harness command name or a deployed rule, gate or
  workflow asset that nothing runs to be reported with a stable code and a runnable directive, so that I can tell the
  user what to install instead of guessing.
- **US-3**: As an existing `devkit-agt` user, I want every command, option, output, code, configuration key and import
  path to keep working after the upgrade, except the enumerated changes of `ADR-dist-bundles-compatibility`, so that
  upgrading needs one sync and one commit.
- **US-4**: As a devkit maintainer, I want per-wheel layering and a dist-only test environment enforced by tests and
  CI, so that `devkit-dist` never starts depending on `devkit-agt` again.

## 3. Non-Goals

1. **Scope Excluded**: renaming `packages/devkit` or the `devkit-agt` distribution; the documented Git URL
   `#subdirectory=packages/devkit` keeps naming `devkit-agt`.
2. **Scope Excluded**: shim modules, alias distributions, alias presets (`devkit:run`), legacy receipt readers or any
   migration path (AGENTS.md compatibility section; `ADR-dist-bundles-compatibility` K2).
3. **Scope Excluded**: a hint in `SELECTION_INVALID` naming a same-named preset of another installed bundle (settled
   by the user, `ADR-dist-bundles-compatibility`).
4. **Scope Excluded**: a smaller third-party dependency set for `devkit-dist`; it keeps click, pyyaml, jinja2 and
   tomlkit.
5. **Scope Excluded**: changing the `devkit-advisory` API or its version beyond the lockstep release number.
6. **Scope Excluded**: switching `devkit-viewer` or `devkit-spec` to `devkit-dist`; both keep their `devkit-agt`
   dependency.
   - **Rationale**: the ADRs name only `devkit-catalog` and `devkit-starter` for the switch; changing a published
     dependency would drop the harness from their consumers' environments, a change no ADR enumerates.
   - **When to Reconsider**: a viewer consumer asks for a viewer installation without the harness.
7. **Scope Excluded**: publishing a release or pushing tags; the release wiring is changed and checked locally.

## 4. Acceptance Criteria & Behavioral Contracts

A *standalone installation* has `devkit-dist` (with `devkit-advisory`) and no `devkit-agt`. A *combined installation*
has both. The *harness command names* are `rules`, `workflow`, `gate`, `worktree`, `generated`, `integration` and
`run`. The *install directive* is the deterministic `[FIX]` text shared by `HARNESS_COMMAND_UNAVAILABLE` and
`HARNESS_ENGINE_MISSING`: in a project, replace the `devkit-dist` requirement with
`devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit` in the same dependency group; for
a tool installation, run `uv tool install --reinstall 'devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist' --with 'devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit'`.

### [AC-01] A standalone installation runs distribution without the harness
- **Given** a fresh project whose environment installs only the `devkit-dist` and `devkit-advisory` wheels
- **When** it runs `devkit --version`, `devkit --help` and a probe of `importlib.util.find_spec("devkit.rules")`
- **Then** `--version` prints `[VERSION: devkit <devkit-dist version>]` and exits `0`, the help lists exactly the
  commands `add`, `bundle`, `config`, `get-context`, `host`, `list`, `override`, `playbook`, `recover`, `remove`,
  `status` and `sync` and none of the harness command names, and the probe returns `None`

### [AC-02] A harness command name answers with a coded error in a standalone installation
- **Given** a standalone installation with no `devkit.commands` entry point named like a harness command
- **When** it runs `devkit <name> ...` for each harness command name, with and without `--format json`
- **Then** each exits `2` with nothing on stdout and an `[ERROR]` advisory with code `HARNESS_COMMAND_UNAVAILABLE` and
  the install directive as `[FIX]` on stderr; with `--format json` stdout is one JSON object whose `error.code` is
  `HARNESS_COMMAND_UNAVAILABLE` and stderr is empty; `devkit no-such-command` keeps click's usage error (exit `2`)
  without that code, and `devkit --help` never lists a harness command name

### [AC-03] Installed commands win over the name-only list
- **Given** the name-only list of harness command names held by `devkit-dist`
- **When** `devkit rules` is looked up in a combined installation, in a standalone installation with a third-party
  `devkit.commands` entry point named `rules`, and in a combined installation where a third party also declares `rules`
- **Then** the first runs the rule engine of `devkit-agt`, the second runs the third-party command, and the third exits
  `2` with `COMMAND_PLUGIN_INVALID` naming both declarations; the list holds command names only and no module path or
  entry point target

### [AC-04] A combined installation keeps every command under one executable
- **Given** a combined installation (and the same with `devkit-spec` added)
- **When** it runs `devkit --help`, each harness command with `--help`, and reads the `console_scripts` entry points of
  every installed distribution
- **Then** the help lists every built-in command and every harness command name (and `spec` with `devkit-spec`), each
  harness `--help` exits `0`, and exactly one installed distribution, `devkit-dist`, declares the `devkit` script while
  `devkit-agt` declares no console script

### [AC-05] Standalone sync deploys only distribution guidance
- **Given** a fresh standalone project
- **When** it runs `devkit sync` and then `devkit get-context devkit`
- **Then** the receipt records the bundles `advisory` and `devkit` with package `devkit-dist` and no `harness` or
  `authoring` entry, its `tool.package` is `devkit-dist`, and the constitution and instruction files of the `devkit`
  bundle contain none of the strings `devkit rules`, `devkit gate`, `devkit workflow` and `devkit run`

### [AC-06] Assets no installed engine runs raise a coded warning
- **Given** a standalone installation that deploys a bundle with `rule`, `gate` and `workflow` assets
- **When** it runs `devkit sync` and `devkit status --format json`
- **Then** both report one `WARNING` notice with code `HARNESS_ENGINE_MISSING` that names each bundle with its asset
  kinds and carries the install directive, the assets are deployed and recorded as before, and the exit codes are those
  without the notice; in a combined installation (entry points `rules`, `gate` and `workflow` present) the same sync and
  status report no such notice

### [AC-07] The harness bundle ships with devkit-agt, auto-selected and built in
- **Given** a combined installation and a fresh project
- **When** it runs `devkit list --format json`, `devkit sync` and `devkit get-context harness`
- **Then** `harness` is listed with package `devkit-agt`, `builtin: true`, `auto_select: true` and default preset
  `core`; the sync deploys it with `["core"]` and raises no `BUNDLE_AUTO_SELECTED` notice for it; its context carries
  the rules and commit gates contract, the snapshot-gate contract and the instructions `devkit-run`,
  `harness-consumption` and `harness-assets`

### [AC-08] Built-in bundles of both wheels count as built in
- **Given** a combined installation
- **When** bundle discovery runs
- **Then** `devkit`, `advisory` and `git-commits` are reported with package `devkit-dist` and `authoring` and `harness`
  with package `devkit-agt`, all five with `builtin: true`; a standalone installation reports only the first three

### [AC-09] The devkit run guidance moves with its preset
- **Given** a combined installation
- **When** a project selects `harness:run`, then `devkit = ["core", "run"]`, then `devkit = "all"`
- **Then** `harness:run` deploys `.devkit/managed/harness/instructions/devkit-run.md` and the `run-pointer` line in the
  root `AGENTS.md` block; `devkit:run` fails with `SELECTION_INVALID` whose fix lists `devkit:all, devkit:core`; and
  `devkit:all` deploys neither `devkit-run` nor `run-pointer`

### [AC-10] The receipt records devkit-dist as the writing tool
- **Given** a project whose receipt records `tool = {package = "devkit-agt", version = "0.1.1"}` and built-in bundle
  packages `devkit-agt`
- **When** a writing `devkit sync` runs in a combined installation at version 0.1.1
- **Then** it reads the old receipt without error, records `tool.package = "devkit-dist"` and each bundle's shipping
  wheel as its package, keeps receipt `schema = 1`, and reports `TOOL_VERSION_CHANGED` with a message starting
  `devkit-agt 0.1.1 -> devkit-dist 0.1.1`; when only the version changes the message keeps the form
  `devkit-dist <old> -> <new>`

### [AC-11] Harness configuration templates come from devkit-agt
- **Given** the commented configuration template
- **When** `devkit config template --print` renders it in a combined installation, in a standalone installation, and
  with a `devkit.config_tables` entry point whose name is not a reserved table
- **Then** the combined `text` is byte-identical to the text before the split (`[workflow.approvals]`,
  `[workflow.stages]` and `[worktree]` at the same place); the standalone `text` contains no `[workflow` or
  `[worktree` header; the unreserved entry is left out with a `CONFIG_TEMPLATE_EXTENSION_FAILED` warning; and a
  configuration with `[rules]`, `[workflow]`, `[gates]`, `[worktree]` and `[integration]` tables reads without error in
  both installations while an unknown top-level key is still refused with `CONFIG_INVALID`

### [AC-12] Missing-extra directives name the requirement the project declares
- **Given** a missing `search` or `mcp` extra
- **When** `SEARCH_EXTRA_MISSING`, the embedding model error, `HOST_MCP_EXTRA_REQUIRED` and the help of
  `devkit playbook search --mode` are rendered
- **Then** each names `devkit-agt[<extra>] @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit`
  for a project that depends on `devkit-agt` and
  `devkit-dist[<extra>] @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist` otherwise (the
  help names both extras), and none tells the project to add `devkit-dist` next to `devkit-agt`

### [AC-13] Layering is enforced per wheel
- **Given** the sources and entry points of each wheel
- **When** the layering tests of `devkit-dist` and `devkit-agt` run
- **Then** the `devkit-dist` test fails on any import, importing-call argument, dotted module path or `module:attribute`
  string constant naming a `devkit-agt` area (`compact` included) in any `devkit-dist` module (`devkit/cli.py` and
  `devkit/__main__.py` included) and on a `devkit-dist` entry point targeting one; the `devkit-agt` test keeps its
  area table (`compact` using only `core` and `advisory`, `harness_guide` importing nothing), maps entry point groups to
  loading areas from the `*GROUP` constants of both wheels' sources, and asserts that the name-only list equals the
  `devkit.commands` names `devkit-agt` declares

### [AC-14] The devkit-dist tests pass without devkit-agt
- **Given** an environment synced exactly with `devkit-dist` and its `search` and `mcp` extras
- **When** `just test-dist` runs
- **Then** it fails unless `importlib.util.find_spec("devkit.rules")` is `None` there, runs every test under
  `packages/devkit-dist/tests` and exits `0`; the CI workflow runs it

### [AC-15] The wheels build and release in lockstep without overlapping files
- **Given** the workspace at one version
- **When** the wheels are built and `scripts/release.sh v<version>` runs
- **Then** `devkit_dist`, `devkit_agt` and `devkit_advisory` wheels carry that version, no installed file path appears
  in two wheels (no root `devkit/py.typed`, no `devkit/__init__.py`), `devkit-agt` requires `devkit-dist==<version>` and
  `devkit-advisory==<version>`, its `search` and `mcp` extras require `devkit-dist[search]` and `devkit-dist[mcp]`, the
  release refuses a tag that does not match all three versions, and the release notes install the `devkit-dist` wheel
  wherever they install `devkit-agt`

### [AC-16] The consumer smoke covers both installations and the tool form
- **Given** the built wheels
- **When** `just smoke` runs
- **Then** it passes after checking AC-01, AC-02, AC-05 and AC-06 in a standalone consumer, the existing combined
  consumer flow with every harness command group, and a tool installation `uv tool install <devkit-dist wheel> --with
  <devkit-agt wheel>` whose `devkit --version` and `devkit rules --help` exit `0`

### [AC-17] An override of a moved asset stops applying without breaking the sync
- **Given** a combined installation and a project that overrides `devkit:devkit-run`
- **When** it runs `devkit sync`
- **Then** the sync exits `0`, deploys `harness:devkit-run` from upstream, leaves the override files under
  `.devkit/overrides/devkit/` in place, and `devkit override create harness:devkit-run` re-creates the override in the
  new bundle

## 5. Assumptions

- **Advisory rule asset**: the `advisory` bundle's opt-in `python` preset ships the `unique-code` rule asset, so the
  ADR statement that no first-party standalone bundle ships rule assets does not hold for that preset. The bundle
  still moves to `devkit-dist` as decided; a standalone project selecting `advisory:python` receives
  `HARNESS_ENGINE_MISSING` (AC-06), and the per-wheel layering test treats rule code under a data area's `bundle/`
  (no package, loaded only by the rule engine from synchronized copies) as bundle content allowed to import
  `devkit.rules`, as the current layering test does.
- **Harness asset ids**: the moved harness sections become two instructions of the `harness` bundle:
  `harness-consumption` (configuration tables of the engines, workflows, rules and commit gates) and `harness-assets`
  (running and testing rule, gate and workflow assets, rule tests and Git snapshot gates of an in-repository bundle,
  `--rules-dir`, the `devkit-agt` development dependency). `devkit-run` and `run-pointer` keep their ids and texts.
- **Reserved table templates**: a `devkit.config_tables` entry point is named after a reserved top-level table and
  returns `TemplateTable` values whose paths are relative to that table; entries render in name order before the
  `[tool.<name>]` tables, without an intro line, which keeps the combined template byte-identical.
- **Engine detection**: `devkit.distribution` reads only the names of `devkit.commands` entry points (`rules`, `gate`,
  `workflow`) for `HARNESS_ENGINE_MISSING`; it never loads them.
- **Dist test support**: shared helpers of the `devkit-dist` tests live in a `distsupport` package so that both test
  trees can sit on one `pythonpath` with `devkit-agt`'s `testsupport`.
- **Before/after comparison**: the `--format json` comparison of the distribution commands required by
  `ADR-dist-bundles-compatibility` runs on wheels built from the base commit and from this branch in a fixture project;
  it is verification evidence for the final report, not a test.
