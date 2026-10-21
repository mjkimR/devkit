---
name: project-structure
description: Read before adding or moving repository Python modules or changing package dependencies.
---

# Package boundaries and roles

This repository is a Python monorepo managed with `uv` workspaces and `just`. Each wheel owns an independent
regular Python package with explicit responsibility boundaries:

- **`devkit-core` (`devkit_core`):** Shared foundation without CLI or application dependencies. Pure primitives
  for filesystem, Git, parsing, and extension dispatch under `core/`, and shared base contracts (`BaseUseCase`,
  MCP interfaces) under `base/`. `base` never imports `core`, and neither imports application packages.
- **`devkit-dist` (`devkit_dist`):** Agent asset distribution and the `devkit` CLI executable. Manages bundles,
  agent projections, sync, context loading, operational playbooks, and native hooks. Never imports `devkit_agt` or
  the MCP SDK.
- **`devkit-agt` (`devkit_agt`):** Developer harness mounted under `devkit` CLI entry points. Owns the rule
  engine, delivery workflows, commit gates, task worktrees, generated files, and integration coordination.
- **`devkit-spec` (`devkit_spec`):** Spec-driven delivery commands and agent assets. Manages proposals, specs,
  milestones, living spec reconciliation (`docs/`), and delivery handoffs.
- **`devkit-mcp` (`devkit_mcp`):** Optional MCP transport adapter, native confirmation forms, and retained-runtime
  registration provider. Domain services stay in their owning feature packages.
- **`devkit-advisory` (`devkit.advisory`):** The Agent Advisory Protocol library. Preserved in its PEP 420 namespace
  as a semver contract with external consumers.
- **`devkit-viewer` (`devkit_viewer`):** Local read-only browser viewer for Living Spec, proposals, specs, and roadmaps.
- **`devkit-catalog` & `devkit-starter`:** Content packages providing opt-in and example bundles.
- **`devkit-dev` (`devkit_dev`):** Repository-only development tools, governance rules, and convention instructions.
  Runtime packages must never depend on it.


# Feature structure and layer boundaries

Executable application packages MUST place feature code under `features/<feature>/`.
Use only populated `cli`, `mcp`, `http`, `usecases`, `services`, `repositories`, and `models` layers.
A small layer MAY be a single Python module.

- **`__init__.py` responsibility:** Feature `__init__.py` files MAY implement package management, including
  import/export control, dynamic loading, lazy attributes, and registration. They MUST NOT contain business logic:
  put domain decisions, execution workflows, and command bodies in named layer modules.
- **Layer import directions:** Imports MUST follow the layer directions declared by `RULE-architecture`:
  `models` and `errors` are contracts; `repositories` use contracts; `services` use contracts and repositories;
  `usecases` coordinate services and repositories; transports (`cli`, `mcp`, `http`) call usecases and contracts.
- **Package base & utils:** Package `base` holds shared contracts; `utils` holds policy-free technical helpers.
  Create neither until needed. General packages MUST NOT add `core`; `devkit_core` owns the shared `base/core` foundation.
  Package `base` MUST NOT import features, utils, adapters, or core implementations; `utils` MUST NOT import features.
- **Adapters:** A declared root `adapters/` MAY hold transport boundaries shared by features (e.g. CLI output framing);
  it calls models and usecases, and lower execution layers MUST NOT import it.
- **Cross-feature dependencies:** Cross-feature imports MUST use declared public APIs and follow the source feature's
  explicit `feature_dependencies` declaration in `.devkit/architecture.toml`. The actual feature dependency graph
  MUST be acyclic, including dependencies through facade exports.
- **Architecture configuration:** `.devkit/architecture.toml` owns source roots, feature names, resource areas,
  package and feature dependencies, and explicit adapter exceptions.


# Contracts and adapters

CLI and MCP execution entrypoints MUST be concrete `BaseUseCase` subclasses from `devkit_core.base.usecase`,
exposing a fully typed `execute` method (sync or async). Adapters construct or receive these use case instances and
invoke `execute`; usecases coordinate domain services and repositories.

- **Constructors:** Constructors MUST only retain inputs and wire dependencies. They MUST NEVER perform execution,
  filesystem reads/writes, or subprocess operations.
- **Helpers:** Internal composition helpers MAY remain functions; they are not transport execution entrypoints.
- **Repositories & Protocols:** Define feature-owned repository `Protocol` contracts when test substitution or multiple
  backends need a contract. Do not mandate `BaseRepository`, a Command abstraction, or Unit of Work without a concrete
  requirement.
- **CLI Command Modules:** Split CLI modules by related command groups where useful. Keep group assembly in transport
  wiring (`cli.py` / `app.py`); command bodies translate arguments, format output, and invoke usecases.


# Tests and bundle manifests

- **Tests:** Package tests MUST be organized into `tests/unit/`, `tests/integration/`, and `tests/e2e/` tiers.
  See the `testing` instruction (`tools/devkit-dev/src/devkit_dev/bundle/instructions/testing.md`) for explicit tier
  isolation boundaries, directory mirroring, and developer execution loops.
- **Bundle Manifests:** Executable packages MUST place each bundle manifest at `bundles/<name>/bundle/bundle.toml`,
  with that bundle's assets beside it. Content-only packages (devkit-dev, devkit-catalog, devkit-starter) MAY keep
  their declared bundle-only layouts. Static assets are separately declared resource areas in `.devkit/architecture.toml`.
