# Optional: Connect Codex or Claude Code to devkit MCP

Follow this after installing devkit and selecting bundles. MCP adds native service tools of `devkit-agt`, including
the integration confirmation path; asset sync and the approved CLI integration fallback work without it, and
`devkit sync` never registers MCP servers.

Supported clients are the interactive Codex CLI (registered through devkit's setup adapter, §3) and the Claude Code
terminal CLI (registered with its own CLI, §4). Elsewhere (Claude Desktop, the VS Code extension, Agent SDK
sessions) the confirmation form is not verified; use the CLI fallback there.

## 1. Choose the retained base and runtime

Run every command below in the base checkout that remains after task worktrees are removed, with its retained
Python environment; setup registers the running Python, so never run it from a disposable worktree runtime.

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

Add the `mcp` extra to the project's existing devkit requirement, keeping its source and revision (a
distribution-only installation uses `devkit-dist[mcp]`); never add a second devkit requirement. `config` is
read-only; its `command` and `args` are what either client runs. `status` inspects only Codex registration and the
local SDK; it does not connect to the server or prove visible approval UI.

## 3. Register Codex explicitly

```bash
uv run devkit host mcp setup --host codex --format json
uv run devkit host mcp status --host codex --format json
```

Setup reports `registered` or `unchanged` and verifies the registration after writing. A different existing entry
is `HOST_MCP_REGISTRATION_CONFLICT`: inspect `codex mcp get devkit --json` locally before replacing it, and do not
paste credentials it shows into reports. `HOST_MCP_REGISTRATION_SHADOWED` means a project-level entry overrides the
user entry; resolve it explicitly first, since setup refuses it even with `--replace`. When the approved intent
includes replacing the user entry, run:

```bash
uv run devkit host mcp setup --host codex --replace --format json
```

Replacement can redirect other sessions using the same name, so never retry a conflict with `--replace` merely to
make installation pass. After a registration failure, inspect before retrying; setup does not roll back a host CLI
write.

## 4. Register Claude Code explicitly

devkit has no Claude Code setup adapter. Register the `command` and `args` from §2's `config` output with Claude
Code's own writer, then inspect the result:

```bash
claude mcp get devkit
claude mcp add --scope user devkit -- <command> <args...>
claude mcp get devkit
```

An existing `devkit` entry with a different command or arguments can belong to another repository or session:
replace it only when the approved intent includes that. The final `get` should report user scope, stdio, the same
command and arguments, and a connected server.

## 5. Reconnect and verify in the client

Reconnect MCP or start a new client session in the retained base, then inspect `/mcp` and the available tools. A
successful setup, status or `get` establishes registration only: report registration, client connection and the
visible confirmation form as separate observations, and verify the form during an actual authorized integration,
never by merging just to test onboarding.

To remove the named user registration, use the client's own command:

```bash
codex mcp remove devkit
claude mcp remove devkit -s user
```

See [Host MCP reference](../../docs/development/reference/host.md#mcp-services),
[official Codex MCP documentation](https://developers.openai.com/codex/mcp/) and
[Claude Code MCP documentation](https://code.claude.com/docs/en/mcp).
