# Optional: Connect Codex or Claude Code to devkit MCP

Follow this after installing devkit and selecting bundles. MCP adds native service tools, including the integration
confirmation path. Ordinary asset synchronization and the approved CLI integration fallback work without it.
`devkit sync` does not register MCP servers or inspect machine registration.

The supported clients are the interactive Codex CLI and the Claude Code terminal CLI. Codex is registered through
devkit's setup adapter (§3); Claude Code is registered with its own CLI (§4). Claude Desktop, the VS Code extension
and Agent SDK sessions are not verified to display the confirmation form; use the CLI fallback there.

## 1. Choose the retained base and runtime

Use the base checkout that will remain after task worktrees are removed and its retained Python environment.
Run every command below there. Setup uses the running Python; do not invoke it from a disposable worktree runtime,
even with `-w` pointing to the base. Linked-worktree and submodule workspace/runtime paths are refused.

The chosen client's CLI must already be installed. Both routes register the fixed name `devkit` in the client's
**user scope** (`codex mcp add` or `claude mcp add --scope user`); neither writes project settings or changes trust,
approval policies or execution permissions. This registration is visible outside this repository. Include that scope
in the installation plan and use existing authorization when it already covers MCP setup; otherwise obtain
agreement before registration.

## 2. Install the extra and inspect

For the Git source used by the installation guide:

```bash
uv add --dev "devkit-agt[mcp] @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit host mcp config --format json
uv run devkit host mcp status --host codex --format json
```

Preserve the project's selected package source and revision; add the `mcp` extra to that dependency rather than
switching an existing pinned or wheel installation to another source. The extra belongs in the retained runtime.
`config` is read-only and works without the SDK; its `command` and `args` are what either client runs, while its
`add_command`, `inspect_command`, `remove_command` and `toml` fields are Codex-specific. `status` reads Codex
registration and local SDK availability, and does not inspect Claude Code;
exit 0 means matching user registration with the SDK and no shadowing settings, 1 means missing/different registration or absent SDK, and 2 means
inspection could not run. It does not connect to the server or prove visible approval UI.

## 3. Register Codex explicitly

```bash
uv run devkit host mcp setup --host codex --format json
uv run devkit host mcp status --host codex --format json
```

Setup reports `registered` on first registration and `unchanged` for an identical enabled registration. It captures
Codex output and verifies registration after writing. A different existing entry is
`HOST_MCP_REGISTRATION_CONFLICT`: inspect `codex mcp get devkit --json` locally before replacing it. Inspection can
contain environment values; do not paste credentials into reports. Status separates user `state` and workspace
`effective_state`; Codex can load project overrides. `HOST_MCP_REGISTRATION_SHADOWED` means a workspace/ancestor
project entry exists, or effective settings disagree with the user entry. Resolve that override explicitly first:
setup refuses before writing, even for a matching project entry and even with `--replace`. When the approved intent includes replacing
that entry, run:

```bash
uv run devkit host mcp setup --host codex --replace --format json
```

Replacement uses Codex's writer without first removing the old registration. It can redirect other sessions using
the same name, so never retry a conflict with `--replace` merely to make installation pass. Preserve unrelated
settings. After a registration failure, inspect before retrying; setup does not claim rollback of a host CLI write.

## 4. Register Claude Code explicitly

devkit has no Claude Code setup adapter. Register the `command` and `args` from §2's `config` output with Claude
Code's own writer, then inspect the result:

```bash
claude mcp get devkit
claude mcp add --scope user devkit -- <command> <args...>
claude mcp get devkit
```

The first `get` shows any existing `devkit` entry: when one exists with a different command or arguments, it can
belong to another repository or session, so replace it only when the approved intent includes that. `get` after
adding should report user scope, stdio, the same command and arguments, and a connected server. Preserve unrelated
settings.

## 5. Reconnect and verify in the client

Reconnect MCP or start a new client session in the retained base (for Claude Code, a new terminal session), then
inspect `/mcp` and the available tools. A successful setup, status or `get` result establishes registration only.
Record connection and visible native confirmation separately; `connection`, `approval_ui`, `trust` and
`execution_permissions` remain `unknown` in CLI reports.

For integration, confirm that the expected service tools are available, then verify confirmation during an actual
authorized integration. SDK tests and registration alone do not establish UI behavior. Do not perform a merge just
to test onboarding. Count the client's MCP tool permission prompt and the devkit confirmation form separately.

To remove the named user registration, use the client's own command:

```bash
codex mcp remove devkit
claude mcp remove devkit -s user
```

See [Host MCP reference](../../docs/development/reference/host.md#mcp-services),
[official Codex MCP documentation](https://developers.openai.com/codex/mcp/) and
[Claude Code MCP documentation](https://code.claude.com/docs/en/mcp).
