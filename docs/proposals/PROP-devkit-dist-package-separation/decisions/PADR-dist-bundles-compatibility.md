---
id: PADR-dist-bundles-compatibility
title: Bundled content and compatibility of the split
summary: Assigns each built-in bundle to the package whose commands it describes, moves the harness guidance and devkit run guidance of the devkit bundle into a new auto-selected harness bundle shipped by devkit-agt, and lists the behaviors the split preserves and the one selection it breaks.
proposal: PROP-devkit-dist-package-separation
status: draft
created_at: 2026-10-19
---

# [PADR-dist-bundles-compatibility] Bundled content and compatibility of the split

- **Status**: Draft
- **Date**: 2026-10-19
- **Answers**: Q5 (bundled content and compatibility) of `PROP-devkit-dist-package-separation`, with the user's
  answers to `harness-guidance`, `compact-home` and `standalone-harness-signals` (`envelopes/answer-01.yaml`).

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
`resource-kinds` (rule, gate and workflow kinds and their commands) and `in-repo-bundle` (rule tests, snapshot
gates, a `devkit-agt` development dependency) describe `devkit rules`, `devkit gate` and `devkit workflow`, which a
standalone `devkit-dist` installation does not have; its `devkit-run` instruction and `run-pointer` guidance
describe `devkit run`, which ships with `devkit-agt` (`PADR-dist-module-split`). Distribution code also emits
harness directives: sync generates the `devkit-workflow` entry skill (`installation/workflow_skill.py`), whose
steps run `devkit workflow`, whenever a selected bundle ships a workflow asset, and rule and gate assets are
deployed without any engine to run them. The proposal promises existing `devkit-agt` users full compatibility
through dependency inclusion and command re-export.

## 2. Decision Drivers

- A standalone installation deploys only guidance whose commands it has (agent-first: no directive an agent cannot
  follow), and what it cannot run is reported with a stable code and a deterministic directive.
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

### Harness guidance of the `devkit` bundle (user question `harness-guidance`)

- **H1: a new auto-selected `harness` bundle shipped by `devkit-agt` (selected by the user).** The harness
  guidance and the `devkit run` guidance leave the `devkit` bundle for a bundle that ships with the engines it
  describes. Pros: a standalone agent loads no harness text; each bundle's guidance matches its wheel. Cons: one
  more managed bundle and receipt entry where `devkit-agt` is installed; `devkit:run` selections break
  (compatibility below).
- **H2: keep the guidance in the `devkit` bundle, worded to apply only when `devkit-agt` is installed.** Rejected:
  standalone agents still load harness text and conditional directives.
- Moving the whole `devkit` bundle to `devkit-agt` is B2 and stays rejected.

The generated `devkit-workflow` entry skill stays a projection of `devkit-dist` (workflow assets are part of its
manifest taxonomy). No first-party bundle installable without `devkit-agt` ships rule, gate or workflow assets
(only `devkit-spec`, which requires `devkit-agt`, and `authoring`, which ships with it, do), so the first driver holds
for every first-party standalone setup; a third-party or in-repo bundle that ships such assets into a standalone
installation is reported by the standalone signal below (user question `standalone-harness-signals`, answer
`both`; the command-name half is in `PADR-dist-command-composition`).

### Compatibility

- **K1: preserve behavior, change ownership metadata in place (selected).** Command names, options, output, codes,
  configuration keys, receipt schema, entry point group names and import paths stay; package names recorded in the
  receipt, the version source and the extras' home change. No alias packages or shim modules.
- **K2: shims for old ownership (a `devkit-agt` that re-exports moved modules, legacy receipt readers, a `devkit:run`
  alias).** Cons: unnecessary with N1 of `PADR-dist-module-split` (import paths do not change) and forbidden by the
  compatibility policy.

## 4. Decision Outcome

Choose **B1**, **H1** and **K1**.

- `devkit-dist` MUST register `devkit`, `advisory` and `git-commits`; `devkit-agt` MUST register `authoring` and
  the new `harness` bundle. The names, presets and `auto_select` of `advisory`, `git-commits` and `authoring` stay
  as they are.
- The `harness` bundle MUST be auto-selected (`auto_select = true`, opted out with `harness = false` under
  `[presets]`) and live in a data-only bundle area of `devkit-agt` whose `__init__.py` imports nothing, like the
  other built-in bundle areas (proposed module `devkit.harness_guide`). The name `harness` is the user's proposed
  name; because `harness` also names the `devkit-spec` capability area (`docs/capabilities/harness/`), it is put to
  the user for confirmation (question `harness-bundle-name`) before it becomes a selection key. It carries:
  - a constitution with the harness intro (rules and commit gates run as code) and the harness contracts: today's
    contract 5 (rules and gates run as code, configured in `[rules]` and `[gates]`) and the snapshot-gate part of
    contract 6 (snapshot gates trust the committed receipt and fail when a managed rule no longer matches it). The
    Planning inventory behind the `harness-guidance` question listed all of contract 6 as harness text; its first
    sentence (commit the receipt after `devkit sync`) is distribution guidance, so under the user's decision that
    the `devkit` bundle keeps distribution guidance it stays there (a correction of that inventory, open to the
    user at plan-accept);
  - the harness parts of `consumption` (rules, gates and workflows in the configuration table, "Workflows",
    "Rules and commit gates" with `.git/devkit.config` and the `rules-check` gate), of `resource-kinds` (how rule,
    gate and workflow assets are run and tested: `devkit rules`, `devkit rules test`, `devkit gate`,
    `devkit workflow next`) and of `in-repo-bundle` (rule tests, "Rules in Git snapshot gates", `--rules-dir`, the
    `devkit-agt` development dependency the rules need);
  - the `devkit-run` instruction in its default preset `core`, and the opt-in preset `run` (`devkit-run` plus the
    `run-pointer` guidance), with the asset ids and texts unchanged except for the bundle they live in.
  Asset ids and the exact split of the moved sections into instructions are settled in Development.
- The `devkit` bundle MUST keep only distribution guidance: contracts 1 to 4, the distribution half of contract 6
  (commit `.devkit/installation.json` after `devkit sync`; the receipt is a `devkit-dist` format), and the
  distribution parts of `consumption`, `resource-kinds` and `in-repo-bundle`. It describes the rule, gate and
  workflow asset kinds only as kinds it deploys, noting that their engines come with `devkit-agt`, and names no
  harness command as a directive. Its in-repo bundle example adds the bundle next to the devkit requirement the
  project already declares (`devkit-agt` when the project uses the harness, otherwise `devkit-dist`) and never adds
  both, the rule `PADR-dist-module-split` sets for the missing-extra directives. Contract 3 names the
  auto-selected bundles generically (`devkit list` shows them) instead of listing `devkit` and `advisory`. Its only
  preset is `core`; the `run` preset and the `devkit-run` and `run-pointer` assets leave it.
- Bundles shipped by `devkit-dist` or `devkit-agt` MUST both count as built in (`builtin`), so the notice for
  auto-selected bundles of other packages keeps excluding first-party bundles, `harness` included.
- In an installation without a `devkit.commands` entry point named `rules`, `gate` or `workflow`, `devkit sync` and
  `devkit status` MUST return a `WARNING` notice with one stable code for the deployed assets of the matching kind
  (`rule`, `gate`, `workflow`), naming the bundles and asset kinds that no installed engine runs, with a
  deterministic directive to add `devkit-agt` to the installation (proposed code `HARNESS_ENGINE_MISSING`; the
  directive wording is shared with the command-name error of `PADR-dist-command-composition`). Engine presence is
  detected by entry point name only; `devkit-dist` never imports or locates a harness module. The notice changes
  no exit code (except under `--strict`) and deploys the assets as before. Its directive is the source-explicit
  one of `PADR-dist-command-composition`.
- With `devkit-agt` installed, every existing `devkit` command, option, sentinel, JSON field, advisory code and exit
  code MUST behave as before the split, except for these enumerated changes: the content of the `devkit` bundle and
  the new `harness` bundle (`devkit get-context`, managed files), the `harness` entry in `devkit list`,
  `devkit status` and the receipt, the receipt's tool and package names, the tool-version notice naming both
  packages (`PADR-dist-config-receipt-ownership`), the missing-extra `[FIX]` texts (`PADR-dist-module-split`), a
  third-party `devkit.commands` plugin named like a harness command now failing with `COMMAND_PLUGIN_INVALID`
  instead of being ignored (`PADR-dist-command-composition`), and the two preset selections below. `devkit config
  template` output with `devkit-agt` installed stays byte-identical (the harness tables keep their place).
  `devkit --version` keeps its `[VERSION: devkit <version>]` form and reports the `devkit-dist` version.
- Two selections of the `devkit` bundle change, accepted in place under the AGENTS.md compatibility policy (no alias
  preset, no migration reader, no special-cased directive; the release notes and guides name both):
  - `devkit:run` (`devkit = ["core", "run"]`, `devkit = "run"`, `devkit add devkit:run`) fails with the existing
    `SELECTION_INVALID`, which stops the whole sync (the `harness` bundle included) until the configuration selects
    `harness:run`; its fix lists the bundle's own presets (`devkit:all, devkit:core`), neither of which restores the
    pointer.
  - `devkit:all` (`devkit = "all"`) keeps working but no longer deploys `devkit-run` and `run-pointer`; a project
    that wants the pointer selects `harness:run`.
  A generic `SELECTION_INVALID` hint naming a preset of the same name in another installed bundle is a non-goal
  (it needs the installed-bundle set at every selection call site; open to the user at plan-accept).
- `devkit-dist`, `devkit-agt` and `devkit-advisory` MUST be released in lockstep from one tag at one version;
  `devkit-agt` pins `devkit-dist` to that exact version, as it pins `devkit-advisory`. `devkit-spec`,
  `devkit-catalog` and `devkit-starter` keep independent versions.
- `devkit-spec` keeps depending on `devkit-agt` (it uses `devkit.rules`, `devkit.workflow`, `devkit.worktree` and
  `devkit.integration`); `devkit-catalog` and `devkit-starter`, which only need the manifest reader in tests, switch
  their development dependency to `devkit-dist`.
- Configuration and receipt behavior follow `PADR-dist-config-receipt-ownership`; import paths follow
  `PADR-dist-module-split`.
- Non-goals: renaming `packages/devkit`; shim modules, alias distributions or alias presets; a cross-bundle preset
  hint in `SELECTION_INVALID`; a smaller third-party
  dependency set for `devkit-dist` (it needs every runtime dependency `devkit-agt` has today: click, pyyaml, jinja2,
  tomlkit).

## 5. Consequences

- The installation guides (`guides/`) gain a distribution-only installation path next to the existing harness and
  SDD paths. The release notes carry one list: the `devkit-dist` wheel, which a release-wheel installation of
  `devkit-agt` must name explicitly; the new auto-selected `harness` bundle; `devkit:run` to `harness:run` (the sync
  fails until changed); the `devkit:all` change; the re-selection of `harness` in projects that opted out with
  `devkit = false`; and the two override cases below.
- `CAP-DIST-content-packages` states which distribution's bundles are built in and lists `harness`;
  `docs/development/reference/distribution.md` (bundles shipped with devkit), `docs/development/reference/compact.md`,
  `CAP-CMP-bounded-execution` and `guides/install/bundle-recommendations.md` name `harness` as the home of
  `devkit-run` and `harness:run` as the opt-in pointer; the CAP-DIST contract that owns sync and status notices
  documents the standalone notice and its code. `CAP-DIST-in-repo-bundles`, whose consumer mirror is the
  `in-repo-bundle` instruction, names both mirrors (the `devkit` bundle for the bundle setup, the `harness` bundle
  for rule discovery, rule tests and Git snapshot gates) and states the example dependency rule above.
- A project with `devkit-agt` gets the `harness` bundle on its first sync after the upgrade: the moved instructions
  appear under `.devkit/managed/harness/`, the `devkit` bundle's managed files change or disappear, and the receipt
  gains a `harness` entry, all committed with the upgrade. A project that opted out with `devkit = false` gets
  `harness` selected (built-in bundles raise no new-bundle notice) and opts out again with `harness = false`.
  Overrides resolve by bundle name and path: an override of a moved asset (`devkit-run`, `run-pointer`) stops
  applying and is re-created as `harness:<asset>`; an override of a split asset that keeps its path in the `devkit`
  bundle (`consumption`, the constitution) keeps applying with an upstream-drift report and still carries the old
  harness text, so the project reconciles it (removing the harness sections) to avoid deploying them twice.
- Development reconciles the `devkit:run` selections: this repository's `.devkit/config.toml` and receipt select only
  `devkit:core` and no first-party package configuration selects `devkit:run` (checked at Planning, materials
  section 8), so no selection here changes; the references to update are the `devkit` bundle manifest, its guide
  bundle test (`tests/distribution/test_guide_bundle.py`), the documents listed above, and the `devkit-spec` bundle
  texts that point to `in-repo-bundle` for rules (`spec-rule` skill), which also point to the `harness` bundle for
  rule tests and snapshot gates.
- Verification covers a dist-only installation that deploys a third-party bundle with rule, gate and workflow
  assets (notice with its code, assets deployed, exit code unchanged), the same with `devkit-agt` installed (no
  notice), and both bundles' context: `devkit get-context devkit` carries no harness command, `devkit get-context
  harness` carries the moved guidance. A `devkit-agt` test asserts that `harness` is listed `builtin`, auto-selected
  with `["core"]`, and a dist-only check asserts it is absent (no existing test covers it: the `BUILTINS` constant
  of `tests/distribution/test_builtin_selection.py` is unused). The guide bundle test asserts that the `devkit`
  bundle's in-repo example never lists `devkit-dist` and `devkit-agt` in one dependency group. A before/after
  comparison of the `--format json`
  output of the distribution commands on a fixture project allows only the enumerated changes above.
