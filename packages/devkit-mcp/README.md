# devkit-mcp

Optional stdio transport, native forms and installed service discovery. `devkit-dist` owns the `devkit`
executable and project registration; domain services stay in their packages. Install this wheel intentionally,
then run `devkit sync` from a retained runtime to reconcile local Codex/Claude/Antigravity project registrations.

`devkit mcp config`, `setup`, `remove`, `status` and `serve` use explicit owning configuration workspaces.
Registration does not establish connection, native UI, trust or execution permission. Cloud profiles expose only
declared read-only services; use an independently authorized CLI/PR route when native approval is unavailable.
