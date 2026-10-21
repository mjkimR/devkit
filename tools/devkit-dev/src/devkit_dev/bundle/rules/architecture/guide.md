# Architecture violations

Move modules to their owning feature and layer; update imports and entry-point
module paths together. Put shared contracts in base and execution in features.
Expose intentional cross-feature APIs through a facade or declare a narrow
public module in `.devkit/architecture.toml`. Resolve reverse dependencies by
moving a contract down or coordinating the operation in a usecase.

The check parses regular, relative, nested, constant dynamic imports and module
path strings. It cannot infer computed dynamic paths or prove function behavior.
An exact import exception documents an existing mixed responsibility; it is
checked for continued use and must be removed when that responsibility is split.


Place package tests in `tests/{unit,integration,e2e}/` as needed and shared helpers
in `tests/support/`; root `conftest.py` and `__init__.py` are allowed. Keep embedded
rule tests beside their deployed rule. Executable bundle manifests belong at
`bundles/<name>/bundle/bundle.toml`; content-only layouts remain declared exceptions.

`__init__.py` may contain import/export control, dynamic loaders, lazy attributes
and other package management code. Business logic belongs in named layer modules.
The static check enforces import directions there but cannot distinguish package
management from business semantics; review that responsibility explicitly rather
than treating any function/class declaration as a violation.
