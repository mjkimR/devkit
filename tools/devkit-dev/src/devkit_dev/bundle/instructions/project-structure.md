---
name: project-structure
description: Read before adding or moving repository Python modules or changing package dependencies.
---

# Package and Layer Boundaries

## Packages

Each wheel owns one independent regular Python package; no installed path belongs to two wheels. Place a module in
the package that owns its responsibility and keep its imports inside these limits:

| Package | Owns | Import limits |
| --- | --- | --- |
| `devkit-core` (`devkit_core`) | Filesystem, Git, parsing and extension primitives under `core/`; shared contracts (`BaseUseCase`, MCP interfaces) under `base/` | `base` never imports `core`; neither imports an application package |
| `devkit-cli` (`devkit_cli`) | The agent-first command-line boundary for any click command; a semver contract with external consumers | `click` and `devkit-advisory` only |
| `devkit-advisory` (`devkit.advisory`) | The Agent Advisory Protocol library in its PEP 420 namespace; a semver contract | Add no `src/devkit/__init__.py` |
| `devkit-dist` (`devkit_dist`) | The `devkit` executable, bundles, projections, sync, context loading, playbooks, native hooks; `adapters/cli.py` configures `devkit_cli` | Never `devkit_agt` or the MCP SDK |
| `devkit-agt` (`devkit_agt`) | Rule engine, delivery workflows, commit gates, task worktrees, generated files, integration, mounted through `devkit.commands` entry points | |
| `devkit-spec` (`devkit_spec`) | Proposals, specs, milestones, Living Spec reconciliation and delivery handoffs | |
| `devkit-mcp` (`devkit_mcp`) | Optional MCP transport, native confirmation forms, retained-runtime registration; domain services stay in their feature packages | |
| `devkit-viewer` (`devkit_viewer`) | The local read-only viewer | |
| `devkit-catalog`, `devkit-starter` | Opt-in and example content bundles | |
| `devkit-dev` (`devkit_dev`) | Repository-only tools, rules and instructions | No runtime package depends on it |

## Feature structure

- Place feature code of an application package under `features/<feature>/`, using only the populated `cli`, `mcp`,
  `http`, `usecases`, `services`, `repositories` and `models` layers; a small layer can be a single module.
- Keep `__init__.py` to package management: import/export control, dynamic loading, lazy attributes and
  registration. Put domain decisions, execution workflows and command bodies in named layer modules.
- Follow the layer directions `RULE-architecture` enforces: `models` and `errors` are contracts; `repositories` use
  contracts; `services` use contracts and repositories; `usecases` coordinate services and repositories; transports
  (`cli`, `mcp`, `http`) call usecases and contracts.
- Create a package `base` (shared contracts) or `utils` (policy-free technical helpers) only when needed, and never
  a package-level `core`; `devkit_core` owns the shared `base`/`core` foundation. `base` imports no features, utils,
  adapters or core implementations; `utils` imports no features.
- Put transport boundaries shared by features (such as CLI output framing) in a declared root `adapters/`; it calls
  models and usecases, and lower execution layers never import it.
- Import across features only through declared public APIs and the source feature's `feature_dependencies` in
  `.devkit/architecture.toml`. Keep the feature graph acyclic, including dependencies through facade exports.
- Declare source roots, feature names, resource areas, package and feature dependencies and adapter exceptions in
  `.devkit/architecture.toml`.

## Use cases and adapters

- Make every CLI and MCP execution entrypoint a concrete `BaseUseCase` subclass from `devkit_core.base.usecase` with
  a fully typed `execute` method (sync or async). Adapters construct or receive the instance and call `execute`.
- In a constructor, only retain inputs and wire dependencies; do execution, file access and subprocesses in
  `execute`.
- Keep internal composition helpers as functions; they are not transport entrypoints.
- Define a feature-owned repository `Protocol` when test substitution or several backends need a contract. Add no
  `BaseRepository`, Command abstraction or Unit of Work without a concrete requirement.
- Split CLI modules by related command group where useful. Keep group assembly in transport wiring (`cli.py`,
  `app.py`); command bodies translate arguments, format output and call usecases.

## Tests and bundle manifests

- Organize package tests by the `testing` instruction.
- Place each bundle manifest of an executable package at `bundles/<name>/bundle/bundle.toml`, with that bundle's
  assets beside it. `devkit-dev`, `devkit-catalog` and `devkit-starter` keep their declared bundle-only layouts.
  Declare static assets as resource areas in `.devkit/architecture.toml`.

## Completion

`uv run devkit rules check` reports no `RULE-architecture` or `RULE-usecase-boundaries` violation for the changed
modules.
