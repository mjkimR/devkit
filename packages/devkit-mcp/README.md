# devkit-mcp

Optional FastMCP stdio transport, native forms and installed service discovery. `devkit-dist` owns the `devkit`
executable and project registration; domain services stay in their packages. Install this wheel intentionally,
then run `devkit sync` from a retained runtime to reconcile local Codex/Claude/Antigravity project registrations.

`devkit mcp status` (including `--descriptor`), `setup`, `remove` and `serve` use explicit owning configuration workspaces.
Registration does not establish connection, native UI, trust or execution permission. Cloud profiles expose only
declared read-only services; use an independently authorized CLI/PR route when native approval is unavailable.

Dist registers the shared artifact tools `shared_put`, `shared_get` and `shared_list`. Put is a bounded write
without business approval forms; cloud profiles hide and refuse it. Read tools resolve the owning configuration
workspace and never initialize or clean storage. See `CAP-COLL-shared-artifacts` and `CAP-MCP-runtime-registration`
for the domain and transport contracts.

## Layout

`src/devkit_mcp/features/runtime/` owns the optional runtime feature: `cli/` adapts command input/output,
`usecases/` coordinates registration changes, discovers installed tool contracts and verifies retained runtimes,
and `mcp/` adapts the SDK-free tool contracts to FastMCP's stdio transport. Domain operations remain in the packages that
declare their tool contracts.
