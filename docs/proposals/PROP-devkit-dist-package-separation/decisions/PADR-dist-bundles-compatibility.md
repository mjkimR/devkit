---
id: PADR-dist-bundles-compatibility
title: Bundled content and compatibility of the split
summary: Assigns each built-in bundle to the package whose commands it describes and lists the CLI, configuration, receipt and Python API behaviors the split preserves.
proposal: PROP-devkit-dist-package-separation
status: draft
created_at: 2026-10-19
---

# [PADR-dist-bundles-compatibility] Bundled content and compatibility of the split

- **Status**: Draft
- **Date**: 2026-10-19
- **Answers**: Q5 (bundled content and compatibility) of `PROP-devkit-dist-package-separation`.

---

## 1. Context & Problem Statement

`devkit-agt` registers four built-in bundles under `devkit.bundles`: `devkit` (auto-selected; consumption,
resource kinds, in-repo bundles, `devkit run`, and the opt-in `run` preset with an `AGENTS.md` pointer), `advisory`
(auto-selected; the Agent Advisory Protocol), `authoring` (opt-in; playbooks plus two rule assets, its Python area
imports `devkit.rules`) and `git-commits` (opt-in; commit conventions, data only). Discovery marks a bundle
`builtin` when its distribution is `devkit-agt` (`BUILTIN_DISTRIBUTION`), which decides the
"auto-selected bundle of another package" notice and the `builtin` field of `devkit status`.

The `devkit` bundle mixes distribution guidance with harness guidance (inventory in
`materials/20261019-package-split-evidence.md` section 4): its constitution (intro and contracts 5 and 6), the
`consumption` instruction (description, configuration table, "Workflows", "Rules and commit gates"),
`resource-kinds` (rule, gate and workflow kinds and their commands) and `in-repo-bundle` (rule tests, a
`devkit-agt` development dependency) describe `devkit rules`, `devkit gate` and `devkit workflow`, which a
standalone `devkit-dist` installation does not have. Distribution code also emits harness directives: sync
generates the `devkit-workflow` entry skill (`installation/workflow_skill.py`), whose steps run `devkit workflow`,
whenever a selected bundle ships a workflow asset, and rule and gate assets are deployed without any engine to run
them. The proposal promises existing
`devkit-agt` users full compatibility through dependency inclusion and command re-export.

## 2. Decision Drivers

- A standalone installation deploys only guidance whose commands it has (agent-first: no directive an agent cannot
  follow).
- An existing `devkit-agt` installation keeps every command, configuration key, receipt and import path working.
- No compatibility shims or migration paths while there are no external consumers (AGENTS.md), except for the
  `devkit-advisory` semver contract, which this change does not touch.

## 3. Considered Options

### Bundle assignment

- **B1: by dependency (selected).** A bundle ships with the wheel that provides everything its assets need:
  `devkit` and `advisory` with `devkit-dist` (both data only and auto-selected); `git-commits` with `devkit-dist`
  (data only, no engine); `authoring` with `devkit-agt` (its rule assets need the rule engine, its area imports
  `devkit.rules`). Pros: each wheel's bundles work in each wheel's minimal environment.
- **B2: everything built in stays with `devkit-agt`.** Cons: a standalone installation deploys no consumption
  guidance at all, and the `advisory` protocol guide would require the harness.
- **B3: everything built in moves to `devkit-dist`.** Cons: `authoring`'s rule assets and area would make
  `devkit-dist` depend on `devkit.rules`, violating `PADR-dist-foundation-ownership`.

Where the harness guidance now inside the `devkit` bundle goes is decided by the user (question
`harness-guidance`); where `devkit run` and its guidance go follows question `compact-home`; how a standalone
installation reports harness assets it cannot run and harness command names follows question
`standalone-harness-signals`. The generated `devkit-workflow` entry skill stays a projection of `devkit-dist`
(workflow assets are part of its manifest taxonomy). It is the one harness directive a standalone installation can
still deploy, and only for a third-party or in-repo bundle: no first-party bundle installable without `devkit-agt`
ships rule, gate or workflow assets (only `devkit-spec`, which requires `devkit-agt`, and `authoring`, which ships
with it, do). The driver above therefore holds for every first-party standalone setup; the third-party case is what
`standalone-harness-signals` covers.

### Compatibility

- **K1: preserve behavior, change ownership metadata in place (selected).** Command names, options, output, codes,
  configuration keys, receipt schema, entry point group names and import paths stay; package names recorded in the
  receipt, the version source and the extras' home change. No alias packages or shim modules.
- **K2: shims for old ownership (a `devkit-agt` that re-exports moved modules, legacy receipt readers).** Cons:
  unnecessary with N1 of `PADR-dist-module-split` (import paths do not change) and forbidden by the compatibility
  policy.

## 4. Decision Outcome

Choose **B1** and **K1**.

- `devkit-dist` MUST register `devkit`, `advisory` and `git-commits`; `devkit-agt` MUST register `authoring`.
  Bundle names, presets and `auto_select` stay as they are unless the answer to `harness-guidance` or
  `compact-home` moves assets between bundles.
- Bundles shipped by `devkit-dist` or `devkit-agt` MUST both count as built in (`builtin`), so the notice for
  auto-selected bundles of other packages keeps excluding first-party bundles.
- With `devkit-agt` installed, every existing `devkit` command, option, sentinel, JSON field, advisory code and exit
  code MUST behave as before the split. `devkit --version` keeps its `[VERSION: devkit <version>]` form and reports
  the `devkit-dist` version.
- `devkit-dist`, `devkit-agt` and `devkit-advisory` MUST be released in lockstep from one tag at one version;
  `devkit-agt` pins `devkit-dist` to that exact version, as it pins `devkit-advisory`. `devkit-spec`,
  `devkit-catalog` and `devkit-starter` keep independent versions.
- `devkit-spec` keeps depending on `devkit-agt` (it uses `devkit.rules`, `devkit.workflow`, `devkit.worktree` and
  `devkit.integration`); `devkit-catalog` and `devkit-starter`, which only need the manifest reader in tests, switch
  their development dependency to `devkit-dist`.
- Configuration and receipt behavior follow `PADR-dist-config-receipt-ownership`; import paths follow
  `PADR-dist-module-split`.
- Non-goals: renaming `packages/devkit`; shim modules or alias distributions; a smaller third-party dependency set
  for `devkit-dist` (it needs every runtime dependency `devkit-agt` has today: click, pyyaml, jinja2, tomlkit).

## 5. Consequences

- The installation guides (`guides/`) gain a distribution-only installation path next to the existing harness and
  SDD paths; release notes list the `devkit-dist` wheel, which a release-wheel installation of `devkit-agt` must name
  explicitly.
- `CAP-DIST-content-packages` states which distribution's bundles are built in.
- The first writing `devkit sync` after the upgrade rewrites `.devkit/installation.json` (tool and package names),
  which the project commits with the upgrade.
