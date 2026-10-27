# Usecase boundaries

The rule reads `.devkit/architecture.toml` and every Python file of the declared
packages, and reports findings anywhere in the workspace. It declares these
inputs (`**/*.py`, `.devkit/architecture.toml`), so a run with explicit targets
that match none of them skips it; full runs, the commit gate and CI always run it.

Expose each transport execution entrypoint as a concrete `BaseUseCase` subclass
from `devkit_core.base.usecase`. Give `execute` explicit input/result annotations;
both sync and async methods are allowed. Transports (the `cli`, `mcp` and `http`
layers of a feature and package-level `adapters`) construct or receive the object
and call `execute`. Keep internal helper functions behind this boundary.
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

Per-file syntax extraction can reuse disposable facts under `.devkit/transient/rules/facts/` when a safe transient
directory exists. Every check rebuilds discovery, settings and cross-file judgment. Working-tree checks/fixes may
warm the memo after successful evaluation; snapshots and dry runs only read it. Missing or malformed memos cause
re-extraction without different findings or advisories. `CAP-GOV-rule-authoring` defines the descriptor contract.
