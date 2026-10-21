# Usecase boundaries

Expose each transport execution entrypoint as a concrete `BaseUseCase` subclass
from `devkit_core.base.usecase`. Give `execute` explicit input/result annotations;
both sync and async methods are allowed. CLI/MCP adapters construct or receive
the object and call `execute`. Keep internal helper functions behind this boundary.
Move filesystem, subprocess and business operations out of constructors; retain
inputs and construct dependencies there instead.

The AST check follows explicit imports, relative imports, aliases, facade exports
and retained instances without executing product imports. An exact transport-only
helper exception uses `[[usecase_exceptions]]` in `.devkit/architecture.toml` with
`source`, callable `target` and `reason`. Remove exceptions once unused. Do not use
exceptions for domain operation entrypoints or whole modules.

Computed dynamic dispatch, arbitrary dependency behavior and control-flow semantics
cannot be proven statically. Review those boundaries; approval policies are enforced
by the execution mechanism, not by inheritance alone.
