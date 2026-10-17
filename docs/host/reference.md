# Host Integration Reference

Canonical semantics: [overview.md](overview.md).

| Command | Result |
| --- | --- |
| `devkit host status [--host codex] [-w DIR] [--format json]` | Read-only installation, handler and last observer status; exit 0 or 1 for findings, 2 when inspection cannot run |
| `devkit host hook --host codex --asset BUNDLE:ID [-w DIR]` | Native event JSON on stdin, native JSON response on stdout; advisory failures return `{}` and exit 0 |
| `devkit bundle plan SOURCE --agent codex` | Managed files and `host_hooks` registrations, without writing |
| `devkit sync --dry-run` | Preview shared-file and managed-file writes |
| `devkit sync --check` | Exit 1 when synchronization is needed |
| `devkit remove BUNDLE` | Remove that bundle's exact owned registrations and managed files |

The public `devkit.host` surface exports `HookDefinition`, `HookEvent`, `HookResponse`, `CodexAdapter`, `HostStatus`,
`read_hook`, `adapter_for`, `plan_config`, `dispatch`, `inspect_host`, and the host advisory classes. Domain services
register `event -> HookResponse` callables under `devkit.host.handlers`. `dispatch` raises advisories; only the
native CLI boundary turns them into warning responses. See the overview for the trust and execution limits.

| Code | Next action |
| --- | --- |
| `HOST_HOOK_INVALID` | Correct the source definition and sync |
| `HOST_CONFIG_INVALID` | Correct the shared JSON configuration and sync |
| `HOST_HOOK_CONFLICT` | Review local changes, restore the receipt-recorded groups, preserve foreign entries, then sync |
| `HOST_HOOK_MISSING` | Sync to restore an absent whole host file |
| `HOST_HOOK_DISPATCH_FAILED` | Inspect host status, correct the source/handler/environment problem, then retry |

Malformed bundle sources are surfaced as `BUNDLE_INVALID` by bundle validation; unsafe deployment paths follow
distribution's existing path advisory contract. A valid installation is not proof that Codex has enabled or trusted
it. Native integration confirmation and execution are described in [Integration](../integration/overview.md).


## MCP services

Install `devkit-agt[mcp]` in a retained runtime. The base installation still supports hooks, configuration inspection
and integration preparation without the SDK.

| Command | Result |
| --- | --- |
| `devkit host mcp config [-w BASE] [--format json]` | Exact executable/arguments, Codex add/get/remove commands and TOML; changes no configuration |
| `devkit host mcp serve [-w BASE]` | Installed service tools over native MCP stdio; stdout is JSON-RPC only |

The config command prints a `codex mcp add devkit -- ...` command. Review the retained runtime and base path before
executing it. `codex mcp get devkit --json` inspects registration; `codex mcp remove devkit` removes that named
registration through Codex. Existing user settings and trust remain host-owned. Registration is not connection or
UI evidence. The executable, dependencies and base checkout must remain available throughout the session.

Installed packages register factories under `devkit.host.services`: `factory(root) -> tuple[McpTool, ...]`.
`devkit.host.mcp` exports dependency-free `McpTool`, `Confirmation`, `ConfirmationReply` contracts. A tool receives
validated arguments and a confirmation callback backed by the current SDK request/session. Native form capability
is checked before elicitation. SDK response correlation binds each reply to the awaiting call; the adapter grants
no permission based on tool arguments. Duplicate tool names and unusable services fail closed. Service/library
Python stdout is discarded after the SDK captures its protocol stream. The built-in integration service is loaded
through this extension point rather than a host-to-domain import.

| Code | Next action |
| --- | --- |
| `HOST_MCP_EXTRA_REQUIRED` | Install the MCP extra in the retained server runtime |
| `HOST_MCP_FAILED` | Inspect the installed service entry points and runtime, then reconnect |
| `HOST_MCP_ARGUMENT_INVALID` | Read the advertised tool schema and supply its declared arguments |
| `HOST_CONFIRMATION_UNAVAILABLE` | Use an interactive client with native form elicitation; inspect state before retrying |

`mcp serve` is a native-protocol exception to ordinary CLI output and output flags. Startup failures are advisory
errors on stderr with exit 2; no ordinary result JSON is written into the protocol stream. Tool results contain
structured advisory data, preserving partial progress from the service. Setup/trust, tool approval, business
confirmation and execution permissions are independent; none is inferred from the others.
