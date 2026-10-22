---
id: ADR-package-split-and-namespaces
title: Package split between devkit-dist and devkit-agt, and independent package namespaces
summary: "For splitting distribution from the harness, we give devkit-dist the devkit executable, config and receipt formats, mount harness commands via devkit.commands and give each wheel its own namespace and feature layout, to keep ownership explicit, accepting import churn and unreserved harness names."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-dist-module-split
  - ADR-dist-command-composition
  - ADR-dist-config-receipt-ownership
  - ADR-dist-bundles-compatibility
  - ADR-independent-package-namespaces-and-feature-layout
---

# [ADR-package-split-and-namespaces] Package split between devkit-dist and devkit-agt, and independent package namespaces

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `packages/devkit-dist/`, `packages/devkit/`, `packages/devkit-core/`,
  `packages/devkit-advisory/`, `tools/devkit-dev/`, `architecture/` (`ARCH-05-1-containers`, `ARCH-05-2-components`,
  `ARCH-05-3-command-plugins`, `ARCH-05-4-distribution-components`, `ARCH-07-deployment`), `capabilities/distribution/`
  (`CAP-DIST-content-packages`, `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions`,
  `CAP-DIST-workspace-ownership`, `CAP-DIST-in-repo-bundles`), `CAP-CMP-bounded-execution`, `guides/`

---

## 1. Context & Problem Statement

`SPEC-devkit-dist-package-separation` split the single `devkit-agt` wheel into `devkit-dist` (distribution, the
`devkit` executable, context loading, playbooks and native hooks) and `devkit-agt` (the harness engines), within
`ADR-dist-foundation-ownership`. The split had to settle the Python namespace and module boundaries, how the one
`devkit` executable reaches harness commands without naming harness modules, which package owns
`.devkit/config.toml` and the installation receipt, and which wheel ships each built-in bundle while existing
`devkit-agt` installations keep working.

Before the split, `devkit.cli` was a lazy click group whose static `COMMANDS` map named every built-in command,
including the harness groups and `devkit run`; other names were looked up in the `devkit.commands` entry point group
(`ARCH-05-3-command-plugins`). `.devkit/config.toml` accepted a closed set of top-level fields, passed the harness
tables through unread, and hard-coded three harness template tables in distribution. The `devkit` bundle mixed
distribution guidance with harness guidance (`materials/20261019-package-split-evidence.md` section 4).
`devkit.compact` (`devkit run`) imports only the core foundation and `devkit.advisory` and is used by rules, gate and
generated, so it is not distribution.

The first split kept every module in a shared PEP 420 `devkit` namespace. That obscured which wheel owns an import and
made package-specific dependency checks depend on a list of module names; application packages also grouped similar
operations differently. The shared foundation is now owned by `devkit-core`, so retaining a second package-level core
obscures whether a helper is generic infrastructure or feature behavior. `devkit.advisory` has runtime consumers
outside this repository and remains a compatibility contract. CLI names, bundle IDs and entry-point group names
identify integration contracts independently of Python imports.

Module paths quoted from the 2026-10-19 members (`devkit.cli`, `devkit.core.receipt`, `devkit.harness_guide`, the
`devkit.<area>` names) are their decision-time names; the namespace decision below moved them to the owning wheel's
regular package.

---

## 2. Decision Drivers

- Standalone `devkit-dist` imports nothing from `devkit-agt`, verifiable statically; dependency direction follows the
  foundation-to-engine layering.
- One `devkit` executable, owned by `devkit-dist`, with no competing console scripts.
- One owner per module and per file format (the package that writes it); no second copy of shared foundation code.
- A project's configuration stays valid whether or not `devkit-agt` is installed, and keeps catching typos;
  `devkit-dist` holds no harness defaults that can drift from the engines that apply them.
- A standalone installation deploys only guidance whose commands it has (agent-first: no directive an agent cannot
  follow), and what it cannot run is reported with a stable code and a deterministic directive.
- An existing `devkit-agt` installation keeps every command line, option, output, code, configuration key and receipt
  working.
- Reuse existing extension points; no new mechanism beyond what the split needs.
- No compatibility shims or migration paths while there are no external consumers (AGENTS.md), except the
  `devkit-advisory` semver contract; a move that buys nothing is still cost.
- Make wheel ownership visible from application import paths.
- Give packages a common feature structure without requiring unused layers; keep use case coordination separate from
  CLI/MCP transport and external IO.
- Check layer direction and package isolation without adding CRUD or transaction abstractions.
- Preserve the externally consumed advisory API and existing command and plugin discovery contracts.

---

## 3. Considered Options

### Python namespace and module boundaries

- **N1: keep the `devkit.*` paths in the shared PEP 420 namespace** (selected by `ADR-dist-module-split`, later
  superseded by `ADR-independent-package-namespaces-and-feature-layout`). No import changes; a module's owning wheel
  is not visible from its import path.
- **N2: a new top-level package `devkit_dist`** (rejected by `ADR-dist-module-split`): rewrites every import and
  documentation reference.
- **N3: rename only `devkit.distribution` to `devkit_dist`** (rejected by `ADR-dist-module-split`): mixed naming
  inside one wheel.
- **F1: move `core`, `search` and `host` whole into `devkit-dist`** (selected by `ADR-dist-module-split`, later
  superseded by `ADR-independent-package-namespaces-and-feature-layout`).
- **F2: split `core` into a distribution core and a harness core** (rejected by `ADR-dist-module-split`): a second
  foundation package and a changed plugin-facing API.
- **F3: move only the `host` modules distribution imports** (rejected by `ADR-dist-module-split`): `devkit host` and
  the MCP server would be missing standalone.
- **Home of `devkit.compact` in `devkit-dist`** (rejected by `ADR-dist-module-split`, user answer `compact-home`): it
  would widen the standalone scope by a feature that is not distribution; it stays in `devkit-agt`.
- **Keep the shared `devkit` namespace and normalize only its internal folders** (rejected by
  `ADR-independent-package-namespaces-and-feature-layout`): ownership still depends on a module allowlist.
- **Give every wheel a regular package and organize applications by feature** (selected by
  `ADR-independent-package-namespaces-and-feature-layout`): explicit ownership and local boundaries.
- **Copy a complete application framework into each package, including mandatory services, repositories and units of
  work** (rejected by `ADR-independent-package-namespaces-and-feature-layout`): abstractions without a corresponding
  operation or resource lifecycle.

### Command composition

- **M1: `devkit-agt` registers its groups under `devkit.commands`** (selected by `ADR-dist-command-composition`): no
  new mechanism; harness names lose their built-in reservation and a harness command pays one entry point scan.
- **M2: `devkit-dist` keeps the harness module paths in `COMMANDS` and reports a missing install** (rejected by
  `ADR-dist-command-composition`): breaks the dependency direction.
- **M3: a separate first-party group that keeps reservation** (rejected by `ADR-dist-command-composition`): a second
  loading path and precedence rule for a collision no package has.
- **M4: `devkit-agt` ships its own `devkit` console script** (rejected by `ADR-dist-command-composition`): competing
  console scripts.

### Configuration and receipt ownership

- **C1: status quo inside `devkit-dist`** (rejected by `ADR-dist-config-receipt-ownership`): a standalone template
  advertises harness tables, and harness defaults live in a package that does not apply them.
- **C2: reserved names in `devkit-dist`, harness templates contributed by `devkit-agt`** (selected by
  `ADR-dist-config-receipt-ownership`): validation unchanged in both installations; `devkit-dist` still knows the five
  reserved names.
- **C3: open field list, top-level names registered by entry point** (rejected by
  `ADR-dist-config-receipt-ownership`): a configuration with `[workflow]` becomes invalid without `devkit-agt`; typo
  detection depends on the installed set.
- **C4: move harness settings under `[tool.devkit-agt]`** (rejected by `ADR-dist-config-receipt-ownership`): breaks
  every configuration, policy reader and document, for no functional gain.

### Bundled content and compatibility

- **B1: bundle assignment by dependency** (selected by `ADR-dist-bundles-compatibility`).
- **B2: everything built in stays with `devkit-agt`** (rejected by `ADR-dist-bundles-compatibility`): no standalone
  consumption guidance, and `advisory` would require the harness.
- **B3: everything built in moves to `devkit-dist`** (rejected by `ADR-dist-bundles-compatibility`): `authoring` would
  make `devkit-dist` depend on the rule engine.
- **H1: a new auto-selected `harness` bundle shipped by `devkit-agt`** (selected by the user,
  `ADR-dist-bundles-compatibility`): one more managed bundle; `devkit:run` selections break.
- **H2: keep the harness guidance in the `devkit` bundle, worded conditionally** (rejected by
  `ADR-dist-bundles-compatibility`): standalone agents still load harness text and conditional directives.
- **K1: preserve behavior, change ownership metadata in place** (selected by `ADR-dist-bundles-compatibility`).
- **K2: shims for old ownership** (rejected by `ADR-dist-bundles-compatibility`): forbidden by the compatibility
  policy.

---

## 4. Decision Outcome

### Wheels, namespaces and layout

- `devkit-dist` owns `devkit_dist`; `devkit-agt` owns `devkit_agt`. Application extensions use their own regular
  packages. `devkit-advisory` retains the public PEP 420 `devkit.advisory` API and does not ship `devkit/__init__.py`.
  No installed path belongs to two wheels. (ADR-independent-package-namespaces-and-feature-layout)
- Applications organize behavior under `features/<feature>/`. A feature adds `cli`, `mcp`, `usecases`, `services`,
  `repositories` and `models` only when the corresponding responsibility exists; small layers may be single modules.
  Adapters call use cases; use cases coordinate services and repositories; lower layers never import their callers.
  Feature dependencies follow an explicit acyclic graph. (ADR-independent-package-namespaces-and-feature-layout)
- Package-level `base` contains shared contracts; optional `utils` contains technical helpers. Shared transport
  adapters require explicit package ownership; dist declares its common CLI boundary under `adapters`. Application
  packages do not introduce package-level `core`. (ADR-independent-package-namespaces-and-feature-layout)
- `devkit_core` is the foundation exception: `base` owns errors and SDK-free MCP contracts; `core` owns generic
  implementations and may depend on base. Base never imports core or application code. Project configuration,
  receipts and execution binding behavior remain in the distribution's project feature.
  (ADR-independent-package-namespaces-and-feature-layout)
- Bundle-only packages may keep only bundle assets. Repository-specific structure and layering rules belong to the
  `devkit-dev` bundle under `tools/devkit-dev`, initially without application layers.
  (ADR-independent-package-namespaces-and-feature-layout)
- The executable remains `devkit`; bundle IDs and entry-point groups retain their names. Entry-point targets move to
  the owning package. `devkit-dist` remains independent of the harness and MCP SDK; optional providers cross that
  boundary through existing entry-point groups. No compatibility wrappers are introduced for application module paths
  that have no external consumers. (ADR-independent-package-namespaces-and-feature-layout)
- `devkit-agt` keeps the rules, workflow, gate, worktree, generated, integration and compact (`devkit run`) areas, the
  `authoring` bundle area and the data-only `harness` bundle area, and depends on `devkit-dist` at the same version.
  (ADR-dist-module-split)
- The source tree of `devkit-dist` is `packages/devkit-dist/`; `devkit-agt` stays in `packages/devkit/`, so the
  documented Git dependency URL (`#subdirectory=packages/devkit`) keeps working. (ADR-dist-module-split)
- Entry points move with their target: the `devkit` console script, the `devkit.bundles` entries of the bundles
  `devkit-dist` ships and `devkit.host.handlers` `observe` are declared by `devkit-dist`; `devkit.post_sync`
  `gate-hooks`, `devkit.hygiene` `worktree-stale`, `devkit.finish_guard` `workflow-envelopes` and
  `devkit.host.services` `integration` stay with `devkit-agt`. (ADR-dist-module-split)
- The `search` extra moves to `devkit-dist`; `devkit-agt` keeps an extra of the same name that requires the matching
  `devkit-dist` extra, so `devkit-agt[search]` keeps working. (ADR-dist-module-split)
- The `[FIX]` directives for a missing extra (`SEARCH_EXTRA_MISSING` and the model fix in search, the
  `devkit playbook search --mode` help) MUST name the extra deterministically without detecting the installation: add
  the extra to the devkit requirement the project already declares, `devkit-agt[<extra>]` when it depends on
  `devkit-agt`, else `devkit-dist[<extra>]`. They never add a second direct requirement on `devkit-dist` next to
  `devkit-agt`, whose resolved source could conflict. (ADR-dist-module-split)
- Layering is enforced per wheel: a `devkit-dist` test refuses any reference to a `devkit-agt` area (`compact`
  included) from its sources and its entry points; `devkit-agt` keeps its own table, in which each of its areas may
  also use the `devkit-dist` areas, `compact` uses only the foundation and `advisory`, and the `harness` bundle area
  imports nothing. Harness command names held as plain strings by `devkit-dist` are not module references.
  (ADR-dist-module-split)

### Command composition

- `devkit-dist` MUST own the `devkit` console script and its `__main__`; its built-in `COMMANDS` map MUST name only
  modules shipped by `devkit-dist`. (ADR-dist-command-composition)
- `devkit-agt` MUST mount each of its commands (`rules`, `workflow`, `gate`, `worktree`, `generated`, `integration`
  and `run`) through a `devkit.commands` entry point with the command's current name and target, so command lines,
  options, output and codes stay unchanged. Harness names are not reserved: a third-party `devkit.commands` plugin
  named like a harness command fails with `COMMAND_PLUGIN_INVALID`. (ADR-dist-command-composition)
- `devkit --version` MUST read the `devkit-dist` version, keeping its `[VERSION: devkit <version>]` form; the
  receipt's tool record follows the same owner. (ADR-dist-command-composition, ADR-dist-bundles-compatibility)
- A standalone installation MUST answer a harness command name with a coded error instead of click's code-less usage
  error. `devkit-dist` holds a name-only list of the command names `devkit-agt` mounts (`rules`, `workflow`, `gate`,
  `worktree`, `generated`, `integration`, `run`) and consults it only when neither its built-in map nor any
  `devkit.commands` entry point has the name, so an installed `devkit-agt` (or any plugin of that name) always wins.
  The error is an `AdvisoryError` with one stable code (`HARNESS_COMMAND_UNAVAILABLE`), exit `2`, and a deterministic
  directive to add `devkit-agt` to the installation. (ADR-dist-command-composition)
- The directive is runnable and source-explicit in the form the missing-extra fixes use (the full Git requirement
  `devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit`, never a bare package name the
  default index would resolve): in a project, replace the `devkit-dist` requirement with that `devkit-agt` requirement
  in the same dependency group (the project never declares both); for a tool installation, reinstall naming both Git
  requirements (`uv tool install --reinstall 'devkit-dist @ git+...#subdirectory=packages/devkit-dist' --with
  'devkit-agt @ git+...#subdirectory=packages/devkit'`). Whether it carries a release ref follows the missing-extra
  fixes. The directive does not detect the installation form and is shared with the standalone asset notice
  `HARNESS_ENGINE_MISSING`. (ADR-dist-command-composition)
- The list holds command names only, never module paths or entry point targets. The per-wheel layering test MUST also
  scan the top-level CLI and `__main__` modules and every string constant that is a dotted module path or a
  `module:attribute` reference into a `devkit-agt` area, so a harness target left in the `COMMANDS` map fails it;
  docstrings, prose constants and bare command names stay allowed. `devkit-agt`'s entry point layering test reads the
  groups loaded by `devkit-dist` by scanning the `*GROUP` constants of the `devkit-dist` sources too. `devkit --help`
  in a standalone installation lists only installed commands, never the listed names. (ADR-dist-command-composition)
- `devkit-agt` ships no console script, so a tool installation names the script owner and adds the harness:
  `uv tool install <devkit-dist requirement> --with <devkit-agt requirement>`, each a wheel path or a full Git
  requirement (`devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist`), never a
  bare package name the default index would resolve. (ADR-dist-command-composition)

### Configuration and receipt

- `devkit-dist` MUST own the `.devkit/config.toml` schema (`SCHEMA`, the closed top-level field list, the
  `[tool.<name>]` table rule), the commented-template renderer, and the receipt format and its writer.
  (ADR-dist-config-receipt-ownership)
- The field list MUST keep `rules`, `workflow`, `gates`, `worktree` and `integration` as reserved names passed through
  unread, so a configuration reads the same with or without `devkit-agt`. (ADR-dist-config-receipt-ownership)
- The commented templates of `[workflow.approvals]`, `[workflow.stages]` and `[worktree]` live in `devkit-agt`,
  registered under a `devkit.config_tables` entry point group named after the reserved table; an entry whose name is
  not reserved is left out with `CONFIG_TEMPLATE_EXTENSION_FAILED`. (ADR-dist-config-receipt-ownership)
- Tools keep contributing `[tool.<name>]` tables through `devkit.config_template` unchanged (devkit-spec's
  `[tool.spec]`). (ADR-dist-config-receipt-ownership)
- The receipt's `tool.package` MUST name the running distributor, `devkit-dist`. Each bundle's package record names
  the wheel that ships it. The receipt schema version does not change; an existing receipt written by `devkit-agt`
  stays readable, and the next writing sync records the new names. The tool-version notice MUST name the package on
  both sides when it changed (`devkit-agt 0.1.1 -> devkit-dist 0.1.1`). (ADR-dist-config-receipt-ownership)

### Bundles and compatibility

- `devkit-dist` MUST register `devkit`, `advisory` and `git-commits`; `devkit-agt` MUST register `authoring` and the
  `harness` bundle. The names, presets and `auto_select` of `advisory`, `git-commits` and `authoring` stay as they
  were. (ADR-dist-bundles-compatibility)
- The `harness` bundle MUST be auto-selected (`auto_select = true`, opted out with `harness = false` under
  `[presets]`) and live in a data-only bundle area of `devkit-agt` whose `__init__.py` imports nothing. The name
  `harness` is the user's decision (`harness-bundle-name`, answer `keep-harness`); the bundle's contract lives in
  `CAP-DIST-content-packages`, separate from the `harness` capability area. It carries the harness intro and contracts
  (rules and gates run as code, configured in `[rules]` and `[gates]`; snapshot gates trust the committed receipt and
  fail when a managed rule no longer matches it); the harness parts of `consumption`, `resource-kinds` and
  `in-repo-bundle`; and the `devkit-run` instruction in its default preset `core` and the opt-in preset `run`
  (`devkit-run` plus `run-pointer`), with asset ids and texts unchanged except for the bundle they live in.
  (ADR-dist-bundles-compatibility)
- The `devkit` bundle MUST keep only distribution guidance: contracts 1 to 4, the distribution half of contract 6
  (commit `.devkit/installation.json` after `devkit sync`), and the distribution parts of `consumption`,
  `resource-kinds` and `in-repo-bundle`. It describes the rule, gate and workflow asset kinds only as kinds it deploys,
  noting that their engines come with `devkit-agt`, and names no harness command as a directive. Its in-repo bundle
  example adds the bundle next to the devkit requirement the project already declares and never adds both. Contract 3
  names the auto-selected bundles generically (`devkit list` shows them). Its only preset is `core`.
  (ADR-dist-bundles-compatibility)
- The generated `devkit-workflow` entry skill stays a projection of `devkit-dist`. (ADR-dist-bundles-compatibility)
- Bundles shipped by `devkit-dist` or `devkit-agt` MUST both count as built in (`builtin`), so the notice for
  auto-selected bundles of other packages keeps excluding first-party bundles, `harness` included.
  (ADR-dist-bundles-compatibility)
- In an installation without a `devkit.commands` entry point named `rules`, `gate` or `workflow`, `devkit sync` and
  `devkit status` MUST return a `WARNING` notice with one stable code (`HARNESS_ENGINE_MISSING`) for the deployed
  assets of the matching kind, naming the bundles and asset kinds that no installed engine runs, with the
  source-explicit directive of the command-name error. Engine presence is detected by entry point name only;
  `devkit-dist` never imports or locates a harness module. The notice changes no exit code (except under `--strict`)
  and deploys the assets as before. (ADR-dist-bundles-compatibility)
- With `devkit-agt` installed, every existing `devkit` command, option, sentinel, JSON field, advisory code and exit
  code MUST behave as before the split, except for the enumerated changes: the content of the `devkit` and `harness`
  bundles, the `harness` entry in `devkit list`, `devkit status` and the receipt, the receipt's tool and package names,
  the tool-version notice, the missing-extra `[FIX]` texts, the unreserved harness command names, and the two preset
  selections below. `devkit config template` output with `devkit-agt` installed stays byte-identical.
  (ADR-dist-bundles-compatibility)
- `devkit:run` fails with the existing `SELECTION_INVALID` until the configuration selects `harness:run`;
  `devkit:all` keeps working but no longer deploys `devkit-run` and `run-pointer`. Both are accepted in place (no alias
  preset, no migration reader, no special-cased directive; the release notes and guides name both). A cross-bundle
  preset hint in `SELECTION_INVALID` is a non-goal. (ADR-dist-bundles-compatibility)
- `devkit-dist`, `devkit-agt` and `devkit-advisory` MUST be released in lockstep from one tag at one version;
  `devkit-agt` pins `devkit-dist` to that exact version. `devkit-spec`, `devkit-catalog` and `devkit-starter` keep
  independent versions. (ADR-dist-bundles-compatibility)
- `devkit-spec` keeps depending on `devkit-agt`; `devkit-catalog` and `devkit-starter` switch their development
  dependency to `devkit-dist`. (ADR-dist-bundles-compatibility)
- Non-goals: renaming `packages/devkit`; shim modules, alias distributions or alias presets; a smaller third-party
  dependency set for `devkit-dist` (click, pyyaml, jinja2, tomlkit). (ADR-dist-bundles-compatibility)

---

## 5. Consequences

- **Positive**: wheel ownership is visible from import paths; a standalone `devkit-dist` deploys only guidance whose
  commands it has and reports what it cannot run; each harness template and guidance lives with its engine.
- **Negative / Risks**: harness command names lose built-in reservation; a harness command pays one
  `devkit.commands` scan on lookup (18 to 24 ms in-process, about 13 ms on the whole-process median,
  `materials/20261019-package-split-evidence.md` section 5), while commit-time gates and native host hooks pay none.
  Imports, dynamic module paths, wheel resource targets, tests and current documentation move together.
- **Tests**: tests move with their area; tests that exercise both wheels stay with `devkit-agt`. A separate dist-only
  check runs the `devkit-dist` tests in an environment that installs `devkit-dist` (with its extras) and not
  `devkit-agt`, asserting the harness package is not importable; CI runs it (`just test-dist`). Package isolation
  remains covered by independent-wheel tests, structure rules check folder and layer boundaries, and feature graph
  tests cover package-specific dependencies.
- **Configuration**: a project that installs only `devkit-dist` gets a template without harness tables; adding
  `devkit-agt` and running `devkit config template` adds them without changing a line. Snapshot gates keep trusting
  the committed receipt; the configuration schema does not change, and the only configuration a project must edit is
  a `devkit:run` selection, which becomes `harness:run`.
- **Upgrade**: a project with `devkit-agt` gets the `harness` bundle on its first sync after the upgrade (managed files
  under `.devkit/managed/harness/`, a `harness` receipt entry). A project that opted out with `devkit = false` gets
  `harness` selected and opts out again with `harness = false`. An override of a moved asset (`devkit-run`,
  `run-pointer`) stops applying and is re-created as `harness:<asset>`; an override of a split asset that keeps its
  path in the `devkit` bundle keeps applying with an upstream-drift report and is reconciled by the project.
- **Documentation**: `ARCH-05-3-command-plugins` describes `devkit-agt` as a first-party plugin, the tool installation
  form, the name-only list, its precedence (built-in map, then entry points, then the list) and its code;
  `CAP-DIST-manifest-spec`, `CAP-DIST-sync-and-transactions` and `CAP-DIST-workspace-ownership` state the owner of each
  format and the `devkit.config_tables` group, listed in `ARCH-05-4-distribution-components`;
  `CAP-DIST-content-packages` states which distributions' bundles are built in and lists `harness`;
  `CAP-DIST-in-repo-bundles` names both mirrors and the example dependency rule; the guides gain a distribution-only
  installation path; package READMEs, reference pages, `ARCH-05-1-containers`, `ARCH-05-2-components`,
  `ARCH-07-deployment` and `AGENTS.md` name each module's owner.

---

## 6. Confirmation

- `devkit-dist` per-wheel layering test (module references, top-level CLI files and string constants) and the
  `devkit-agt` entry point layering test; `devkit-dev` structure rules and feature graph tests.
- Dist-only check (`just test-dist`, `scripts/dist_only.sh`).
- Command discovery with `devkit-dist` alone (no harness commands listed; each listed name answers
  `HARNESS_COMMAND_UNAVAILABLE` with exit `2`; an unlisted unknown name keeps click's usage error), with both wheels and
  with `devkit-spec` added, and exactly one installed distribution providing the `devkit` script; a `devkit-agt` test
  keeps the name-only list equal to its declared `devkit.commands` names.
- A dist-only installation deploying a third-party bundle with rule, gate and workflow assets reports
  `HARNESS_ENGINE_MISSING` without changing the exit code; with `devkit-agt` there is no notice.
  `devkit get-context devkit` carries no harness command and `devkit get-context harness` carries the moved guidance;
  a `devkit-agt` test asserts `harness` is `builtin` and auto-selected with `["core"]`, a dist-only check asserts it is
  absent; the guide bundle test asserts the `devkit` bundle's in-repo example never lists `devkit-dist` and
  `devkit-agt` in one dependency group; a before/after comparison of the distribution commands' `--format json`
  output allows only the enumerated changes.

