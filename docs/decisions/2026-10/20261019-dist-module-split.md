---
id: ADR-dist-module-split
title: Namespace and module split between devkit-dist and devkit-agt
summary: Keeps the devkit.* module paths through the shared PEP 420 namespace and moves core, search, host, distribution and the root CLI whole into devkit-dist, leaving the harness engines and devkit.compact (devkit run) in devkit-agt.
proposal: SPEC-devkit-dist-package-separation
status: accepted
created_at: 2026-10-19
---

# [ADR-dist-module-split] Namespace and module split between devkit-dist and devkit-agt

- **Status**: Accepted
- **Date**: 2026-10-19
- **Answers**: Q1 (packaging and namespace) and Q4 (foundation boundaries) of `SPEC-devkit-dist-package-separation`,
  within `ADR-dist-foundation-ownership`, with the user's answer to `compact-home` (`envelopes/answer-01.yaml`).

---

## 1. Context & Problem Statement

`devkit` is already a PEP 420 namespace package shared by two wheels: `devkit-agt` ships `src/devkit` and
`devkit-advisory` ships only `devkit/advisory/` (no `src/devkit/__init__.py`, enforced by the agent guide). The
static import closure of `devkit.distribution` (every `import`, lazy ones included) reaches all 15 `devkit.core`
modules (the `devkit.core` package re-exports them), all of `devkit.search`, part of `devkit.host` and
`devkit.advisory`, and nothing else: no `rules`, `workflow`, `gate`, `worktree`, `compact`, `generated` or
`integration` module. `devkit.host` and `devkit.search` import only `core` and `advisory`. The layering test
(`packages/devkit/tests/test_layering.py`) already enforces these edges. Evidence:
`materials/20261019-package-split-evidence.md`.

`devkit.compact` (`devkit run`) imports only `devkit.core` and `devkit.advisory` and is imported by `devkit.rules`,
`devkit.gate` and `devkit.generated`, so either wheel keeps the dependency direction; it is not distribution.

`ADR-dist-foundation-ownership` requires `devkit-dist` to run distribution, native hooks, context loading and
playbooks without `devkit-agt`, and leaves the namespace and the exact core/search/host split to Planning.

## 2. Decision Drivers

- Standalone `devkit-dist` imports nothing from `devkit-agt`, verifiable statically.
- Minimal churn for the existing importers: `devkit-agt` itself, `devkit-spec` (about 140 `from devkit...`
  imports) and rule plugin code in bundles, which import `devkit.core`, `devkit.rules` and `devkit.advisory` by
  module path.
- One owner per module; no second copy of shared foundation code.
- The repository has no external consumers yet (AGENTS.md compatibility section), so moves may be made in place,
  but a move that buys nothing is still cost.

## 3. Considered Options

### Q1: Python namespace

- **N1: keep the `devkit.*` paths in the shared PEP 420 namespace (selected).** `devkit-dist` ships
  `devkit/{core,search,host,distribution,...}` and the top-level modules `devkit/cli.py` and `devkit/__main__.py`;
  `devkit-agt` ships its engine subpackages into the same namespace, as `devkit-advisory` already does.
  Pros: no import changes anywhere; plugin code, docs and the layering test keep their names; the mechanism is
  already proven in this workspace. Cons: a module's owning wheel is not visible from its import path; top-level
  files under `devkit/` (`py.typed`) must be shipped by exactly one wheel.
- **N2: a new top-level package `devkit_dist`.** Pros: ownership visible in every import. Cons: rewrites every
  `devkit.core`, `devkit.distribution`, `devkit.host` and `devkit.search` import in `devkit-agt`, `devkit-spec`
  and rule plugins, and every documentation reference (`devkit.core.cli` is the plugin contract of
  `ARCH-05-3-command-plugins`); it either moves `devkit.core` under `devkit_dist`, breaking every plugin, or
  splits one foundation across two names.
- **N3: rename only `devkit.distribution` to `devkit_dist`.** Cons: mixed naming inside one wheel with no gain
  over N1.

### Q4: foundation boundaries

- **F1: move `core`, `search` and `host` whole (selected).** Pros: the closure already reaches every `core`
  module; `host` brings native hooks, the hook runner, `devkit host` and the MCP server, to which `devkit-agt`
  keeps adding its integration tools through the `devkit.host.services` entry point; playbook search needs all of
  `search`. Cons: harness-oriented helpers in `core` (`git`, `locks`, `plugins`, `deadline`) ship in the
  distribution wheel.
- **Home of `devkit.compact` (user question `compact-home`).** In `devkit-dist` it would cost no bundle or
  configuration change but widen the standalone scope of `ADR-dist-foundation-ownership` by a feature that is not
  distribution; in `devkit-agt` the standalone scope stays as agreed, and its guidance moves to the `harness`
  bundle with a `devkit:run` selection break (`ADR-dist-bundles-compatibility`). The user chose `devkit-agt`.
- **F2: split `core` into a distribution core and a harness core.** Cons: `devkit.core` re-exports every module and
  `receipt` and `project`, which distribution needs, use `git`, `paths` and `files`; the split creates a second
  foundation package, changes the plugin-facing API and saves under 1000 lines.
- **F3: move only the `host` modules distribution imports (configuration, hooks model, runner, status).** Cons:
  projected native hooks call `devkit host`, which would then be missing standalone, and the MCP server would stay
  behind; this contradicts `ADR-dist-foundation-ownership`.

## 4. Decision Outcome

Choose **N1** and **F1**.

- `devkit-dist` MUST keep the import paths `devkit.core`, `devkit.search`, `devkit.host`, `devkit.distribution`,
  `devkit.cli` and `devkit.__main__` unchanged, shipped into the shared `devkit` namespace. No wheel ships
  `src/devkit/__init__.py`, and no installed file path is shipped by more than one wheel: the root
  `devkit/py.typed` marker is replaced by a `py.typed` in each area package (PEP 561 places markers in the
  subpackages of a namespace).
- `devkit-dist` MUST ship `devkit.core`, `devkit.search` and `devkit.host` whole, `devkit.distribution` with the
  `devkit` bundle (`devkit.distribution.guide`), the root command line, and the bundle areas assigned to it by
  `ADR-dist-bundles-compatibility`.
- `devkit-agt` MUST keep `devkit.rules`, `devkit.workflow`, `devkit.gate`, `devkit.worktree`, `devkit.generated`,
  `devkit.integration` and `devkit.compact` (`devkit run`, mounted through `devkit.commands`,
  `ADR-dist-command-composition`), the `authoring` bundle area and the new data-only `harness` bundle area
  `devkit.harness_guide` (`ADR-dist-bundles-compatibility`), and depends on `devkit-dist` at the same version.
- The new source tree is `packages/devkit-dist/` (wheel `devkit-dist`); `devkit-agt` stays in `packages/devkit/`,
  so the documented Git dependency URL (`#subdirectory=packages/devkit`) keeps working.
- Entry points move with their target: the `devkit` console script, the `devkit.bundles` entries of the bundles
  `devkit-dist` ships and `devkit.host.handlers` `observe` are declared by `devkit-dist`; `devkit.post_sync`
  `gate-hooks`, `devkit.hygiene` `worktree-stale`, `devkit.finish_guard` `workflow-envelopes` and
  `devkit.host.services` `integration` stay with `devkit-agt`.
- The `search` and `mcp` extras move to `devkit-dist`; `devkit-agt` keeps extras of the same names that require
  the matching `devkit-dist` extras, so `devkit-agt[search]` and `devkit-agt[mcp]` keep working.
- The `[FIX]` directives for a missing extra (`SEARCH_EXTRA_MISSING` and the model fix in `devkit.search`, the MCP
  extra in `devkit.host`, the `devkit playbook search --mode` help) MUST name the extra deterministically without
  detecting the installation: add the extra to the devkit requirement the project already declares,
  `devkit-agt[<extra>]` when it depends on `devkit-agt`, else `devkit-dist[<extra>]`. They never add a second direct
  requirement on `devkit-dist` next to `devkit-agt`, whose resolved source could conflict.
- Layering is enforced per wheel: a `devkit-dist` test refuses any reference to a `devkit-agt` area (`compact`
  included) from its sources (`devkit/cli.py`, `devkit/__main__.py` and string constants included,
  `ADR-dist-command-composition`) and its entry points; `devkit-agt` keeps its own table, in which each of its areas may
  also use the `devkit-dist` areas, `compact` keeps using only `core` and `advisory`, and the `harness` bundle area
  imports nothing. Harness command names held as plain strings by `devkit-dist` (`ADR-dist-command-composition`)
  are not module references.

## 5. Consequences

- Tests move with their area: `core`, `search`, `host` and `distribution` tests become `devkit-dist` tests and run
  in an environment without `devkit-agt`, as `ADR-dist-foundation-ownership` requires; tests that exercise both
  wheels together stay with `devkit-agt`; `compact` tests and the CI compact test path stay with `devkit-agt`. Four `devkit-dist`-side tests currently reach harness code
  (`distribution/test_config_template.py`, `core/test_cli.py`, the hook assertion of `distribution/test_sync.py`,
  and `testsupport.gate`), and move or split accordingly (`materials/20261019-package-split-evidence.md` section 5).
- The workspace venv installs every package, so `devkit-agt` entry points stay visible to `devkit-dist` tests run
  there. A separate dist-only check MUST run the `devkit-dist` tests in an environment that installs `devkit-dist`
  (with its extras) and not `devkit-agt` (a separate environment synced exactly with only `devkit-dist`, or the
  smoke installation; the workspace dev group installs `devkit-agt`, so an inexact sync does not qualify),
  asserting `importlib.util.find_spec("devkit.rules") is None`; CI runs it.
- Root `pyproject.toml` adds the new source root to ruff `namespace-packages`, Pyright `extraPaths`, pytest
  `testpaths` and the dev dependency group; release, smoke and CI wiring add the new wheel.
- Package READMEs, `docs/development/reference/` pages, `ARCH-05-1-containers`, `ARCH-05-2-components` and
  `ARCH-07-deployment` name the new owner of each module, and the root `AGENTS.md` (Architecture and Boundaries:
  the layering rule stated for `packages/devkit` and its list of data-only bundle areas, which gains the
  `harness_guide` area; Packages: `devkit-agt` as the single distribution) describes the three wheels and the per-wheel layering.
