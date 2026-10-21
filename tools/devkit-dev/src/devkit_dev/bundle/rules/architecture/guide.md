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
