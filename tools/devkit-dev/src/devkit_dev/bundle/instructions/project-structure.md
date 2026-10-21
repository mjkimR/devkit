---
name: project-structure
description: Read before adding or moving repository Python modules or changing package dependencies.
---

# Package structure

Executable packages MUST place feature code under `features/<feature>/`.
Use only populated `cli`, `mcp`, `http`, `usecases`, `services`, `repositories`,
and `models` layers. A small layer MAY be a single Python module. Feature
`__init__.py` files expose deliberate public APIs; `errors.py` holds feature errors.
`bootstrap.py` assembles dependencies. A declared root `adapters/` MAY hold
transport boundaries shared by features; it calls models and usecases, and
lower execution layers MUST NOT import it. Package `base` holds shared contracts;
`utils` holds policy-free helpers. Add them only when needed. General packages
MUST NOT add `core`; `devkit_core` owns the shared `base/core` foundation.

Imports MUST follow the layer directions declared by `RULE-architecture`:
models/errors are contracts; repositories use contracts; services use contracts
and repositories; usecases coordinate services and repositories; transports call
usecases and contracts. Package base MUST NOT import features, utils, adapters or core implementations;
utils MUST NOT import features. Cross-feature imports use declared public APIs.
Dist and agt use independent `devkit_dist` and `devkit_agt` roots. The advisory
public API remains `devkit.advisory`.

`.devkit/architecture.toml` owns source roots, feature names, resource areas,
package dependencies and explicit adapter exceptions. A necessary exception
MUST identify an exact source and target module plus its reason. Do not add a
wildcard exclusion to conceal a dependency. Keep rule tests beside their rule;
other tests belong under the package's `tests`. Content packages, bundle data,
viewer static assets and the foundation use their declared special layouts.
