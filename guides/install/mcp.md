# Optional: Connect Codex to devkit MCP

Follow this after installing devkit and selecting bundles. MCP adds native service tools, including the integration
confirmation path. Ordinary asset synchronization and the approved CLI integration fallback work without it.
`devkit sync` does not register MCP servers or inspect machine registration.

## 1. Choose the retained base and runtime

Use the base checkout that will remain after task worktrees are removed and its retained Python environment.
Run every command below there. Setup uses the running Python; do not invoke it from a disposable worktree runtime,
even with `-w` pointing to the base. Linked-worktree and submodule workspace/runtime paths are refused.

Codex CLI must already be installed. The adapter registers the fixed name `devkit` in Codex's **user scope** through
`codex mcp add`; it does not write project settings or change trust, approval policies or execution permissions.
This registration is visible outside this repository. Include that scope in the installation plan and use existing
authorization when it already covers MCP setup; otherwise obtain agreement before registration.

## 2. Install the extra and inspect

For the Git source used by the installation guide:

```bash
uv add --dev "devkit-agt[mcp] @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit host mcp config --format json
uv run devkit host mcp status --host codex --format json
```

Preserve the project's selected package source and revision; add the `mcp` extra to that dependency rather than
switching an existing pinned or wheel installation to another source. The extra belongs in the retained runtime.
`config` is read-only and works without the SDK. `status` reads Codex registration and local SDK availability;
exit 0 means matching registration with the SDK, 1 means missing/different registration or absent SDK, and 2 means
inspection could not run. It does not connect to the server or prove visible approval UI.

## 3. Register explicitly

```bash
uv run devkit host mcp setup --host codex --format json
uv run devkit host mcp status --host codex --format json
```

Setup reports `registered` on first registration and `unchanged` for an identical enabled registration. It captures
Codex output and verifies registration after writing. A different existing entry is
`HOST_MCP_REGISTRATION_CONFLICT`: inspect `codex mcp get devkit --json` locally before replacing it. Inspection can
contain environment values; do not paste credentials into reports. When the approved intent includes replacing
that entry, run:

```bash
uv run devkit host mcp setup --host codex --replace --format json
```

Replacement uses Codex's writer without first removing the old registration. It can redirect other sessions using
the same name, so never retry a conflict with `--replace` merely to make installation pass. Preserve unrelated
settings. After a registration failure, inspect before retrying; setup does not claim rollback of a host CLI write.

## 4. Reconnect and verify in the client

Reconnect MCP or start a new Codex session, then inspect `/mcp` and the available tools. A successful setup or
status result establishes registration only. Record connection and visible native confirmation separately;
`connection`, `approval_ui`, `trust` and `execution_permissions` remain `unknown` in CLI reports.

For integration, confirm that the expected service tools are available, then verify confirmation during an actual
authorized integration. SDK tests and registration alone do not establish UI behavior. Do not perform a merge just
to test onboarding. Claude Code and other hosts have no devkit setup adapter in this route.

To remove this named user registration, use Codex's own command:

```bash
codex mcp remove devkit
```

See [Host MCP reference](../../docs/development/reference/host.md#mcp-services) and
[official Codex MCP documentation](https://developers.openai.com/codex/mcp/).
