---
name: project-structure
description: Read before adding or moving repository Python modules or changing package dependencies.
---

# Package structure

Executable packages MUST place feature code under `features/<feature>/`.
Use only populated `cli`, `mcp`, `http`, `usecases`, `services`, `repositories`,
and `models` layers. A small layer MAY be a single Python module. Feature
`__init__.py` files MAY implement package management, including import/export
control, dynamic loading, lazy attributes and registration. They MUST NOT contain
business logic: put domain decisions, execution workflows and command bodies in
named layer modules. Review this boundary by responsibility, not by banning
functions or classes. `errors.py` holds feature errors.
`bootstrap.py` assembles dependencies. A declared root `adapters/` MAY hold
transport boundaries shared by features; it calls models and usecases, and
lower execution layers MUST NOT import it. Package `base` holds shared contracts;
`utils` holds policy-free helpers. Add them only when needed. General packages
MUST NOT add `core`; `devkit_core` owns the shared `base/core` foundation.

Imports MUST follow the layer directions declared by `RULE-architecture`:
models/errors are contracts; repositories use contracts; services use contracts
and repositories; usecases coordinate services and repositories; transports call
usecases and contracts. Package base MUST NOT import features, utils, adapters or core implementations;
utils MUST NOT import features. Cross-feature imports MUST use declared public APIs and follow the source feature's
explicit `feature_dependencies` declaration. The actual feature dependency graph
MUST be acyclic, including dependencies through facade exports.
Dist and agt use independent `devkit_dist` and `devkit_agt` roots. The advisory
public API remains `devkit.advisory`.

`.devkit/architecture.toml` owns source roots, feature names, resource areas,
package and feature dependencies and explicit adapter exceptions. A necessary exception
MUST identify an exact source and target module plus its reason. Do not add a
wildcard exclusion to conceal a dependency. Keep rule tests beside their rule;
other tests belong under the package's `tests`. Content packages, bundle data,
viewer static assets and the foundation use their declared special layouts.


# Contracts and adapters

Use cases SHOULD expose explicit input/result contracts. Functions are sufficient
for stateless operations; use classes when they own state or shared behavior.
Do not introduce empty `BaseUseCase` or `BaseRepository` classes for uniformity.
A replaceable repository boundary SHOULD use a feature-owned `Protocol` when
multiple implementations or test substitution need a shared contract. Add a base
implementation only when implementations actually share behavior. CLI commands
remain transport adapters; add a shared Command registration/execution contract
only when a concrete CLI/MCP consumer needs it.

CLI directories MAY contain multiple modules grouped by commands that change
together. Keep group assembly in `app.py` where useful; command bodies translate
arguments and output and call usecases. Keep business orchestration in usecases.

# Tests and bundle resources

Package tests MUST use `tests/unit/`, `tests/integration/` and `tests/e2e/` as
needed, with reusable helpers in `tests/support/`. Root `conftest.py` and
`__init__.py` are allowed. Within each category, SHOULD mirror source ownership,
for example `features/<feature>/usecases/`, `base/` or `core/`; do not create empty
categories. Unit tests isolate behavior and adapters, integration tests connect
real components or filesystem/Git boundaries, and e2e tests exercise installed
public CLI/MCP flows. Shared package-installation combinations belong in the
repository-level e2e harness. Classify by the tested boundary, not by whether the
package is an application. A deployed rule's tests MUST remain beside that rule.

Reusable helpers shared by multiple devkit packages MAY live in `devkit_dev.testing`
when a concrete shared need exists. Consume them through development dependencies
only; product runtime code MUST NOT depend on devkit-dev. Keep helpers used by one
package in its own `tests/support/`.

Executable packages MUST place each bundle manifest at
`bundles/<name>/bundle/bundle.toml`, with that bundle's assets beside it.
Content-only packages such as devkit-dev, devkit-catalog and devkit-starter MAY
keep their own declared bundle-only layouts. Static assets are separately
declared resource areas.
