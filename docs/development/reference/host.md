# Host Integration Reference

Canonical semantics: `CAP-HOST-lifecycle-observation`.

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
it. Native integration confirmation and execution are described in `CAP-INT-mcp-services`.


## MCP services

Install `devkit-agt[mcp]` in a retained runtime. The base installation still supports hooks, configuration inspection
and integration preparation without the SDK.

| Command | Result |
| --- | --- |
| `devkit host mcp config [-w BASE] [--format json]` | Exact executable/arguments, Codex add/get/remove commands and TOML; changes no configuration |
| `devkit host mcp setup [--host codex] [--replace] [-w BASE] [--format json]` | Explicit user-scoped registration through Codex; matching entries unchanged, conflicting entries refused without --replace |
| `devkit host mcp status [--host codex] [-w BASE] [--format json]` | Read-only registration and SDK diagnostics; exit 0 matching with SDK, 1 findings, 2 inspection failure |
| `devkit host mcp serve [-w BASE]` | Installed service tools over native MCP stdio; stdout is JSON-RPC only |

Follow [optional MCP onboarding](../../../guides/install/mcp.md) from the installation routes. Run setup from the
retained base checkout and its retained Python environment; it rejects linked-worktree and submodule workspace or
runtime paths. It uses the running interpreter, imports the SDK/server before writing, calls `codex mcp add devkit`
and verifies the effective result. Identical enabled command/args with no environment, cwd or tool overrides are
`unchanged`; a different entry is refused unless `--replace` was explicit. Replacement does not first remove it.
Codex's writer owns persistence; a failed write/verification is not a devkit rollback guarantee. Concurrent external
host configuration edits are outside devkit's transaction scope.

Registration uses Codex's user scope and fixed name `devkit`, so switching repositories can conflict. Setup does
not edit project TOML, trust, tool approval policies or execution permissions. The read-only config command retains
its add/get/remove commands and TOML snippet. `codex mcp remove devkit` removes that named user registration.
`devkit sync` neither registers MCP nor inspects machine registration; there is no persistent MCP selection setting.

Status reports `state=missing|matching|different`, desired workspace/command/args, `sdk_available`, errors and notices;
it does not expose existing environment values or foreign server settings. Setup adds
`action=registered|replaced|unchanged`. Text results are `HOST_MCP_SETUP` / `HOST_MCP_STATUS` sentinels; JSON is one
object. `connection`, `approval_ui`, `trust` and `execution_permissions` remain `unknown`: reconnect the client,
inspect its tool catalog and verify actual UI separately. The executable, dependencies and base checkout must
remain available throughout the session.

Installed packages register factories under `devkit.host.services`: `factory(root) -> tuple[McpTool, ...]`.
`devkit.host.mcp` exports dependency-free `McpTool`, `Confirmation`, `ConfirmationReply` contracts. A tool receives
validated arguments and a confirmation callback backed by the current SDK request/session. Native form capability
is checked before elicitation. SDK response correlation binds each reply to the awaiting call; the adapter grants
no permission based on tool arguments. Duplicate tool names and unusable services fail closed. Service/library
Python stdout is discarded after the SDK captures its protocol stream. The built-in integration service is loaded
through this extension point rather than a host-to-domain import.

| Code | Next action |
| --- | --- |
| `HOST_MCP_REGISTRATION_FAILED` | Inspect Codex CLI/configuration access and effective registration before retrying |
| `HOST_MCP_REGISTRATION_MISSING` | Run setup from the retained base/runtime |
| `HOST_MCP_REGISTRATION_CONFLICT` | Inspect the existing entry; use --replace only for an intended replacement |
| `HOST_MCP_RUNTIME_UNSAFE` | Run setup outside linked worktrees using the retained base/runtime |
| `HOST_MCP_EXTRA_REQUIRED` | Install the MCP extra in the retained server runtime |
| `HOST_MCP_FAILED` | Inspect the installed service entry points and runtime, then reconnect |
| `HOST_MCP_ARGUMENT_INVALID` | Read the advertised tool schema and supply its declared arguments |
| `HOST_CONFIRMATION_UNAVAILABLE` | Use an interactive client with native form elicitation; inspect state before retrying |

`mcp serve` is a native-protocol exception to ordinary CLI output and output flags. Startup failures are advisory
errors on stderr with exit 2; no ordinary result JSON is written into the protocol stream. Tool results contain
structured advisory data, preserving partial progress from the service. Setup/trust, tool approval, business
confirmation and execution permissions are independent; none is inferred from the others.
