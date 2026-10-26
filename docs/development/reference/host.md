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

The public `devkit_dist.features.host` surface exports `HookDefinition`, `HookEvent`, `HookResponse`, `CodexAdapter`, `HostStatus`,
`read_hook`, `adapter_for`, `plan_config`, `dispatch`, `inspect_host`, and the host advisory classes. Domain services
register `event -> HookResponse` callables under `devkit_dist.features.host.handlers`. `dispatch` raises advisories; only the
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

Install `devkit-mcp`, or `devkit-agt[mcp]`, in a retained base/tool runtime for devkit-dist's shared artifact tools;
integration, proposal acceptance and handoff are CLI commands, never MCP tools. The optional wheel mounts
`devkit mcp`; domain tools remain in agt/spec. See `CAP-MCP-runtime-registration` and `CAP-INT-mcp-services`.

| Command | Result |
| --- | --- |
| `devkit mcp status --descriptor [-w WORKSPACE] [--executable PATH] --format json` | Verified retained descriptor; no writes |
| `devkit mcp setup [-w WORKSPACE] [--host codex|claude|antigravity] [--executable PATH]` | Exact eligible project reconciliation |
| `devkit mcp remove [-w WORKSPACE]` | Exact owned entry removal; local exclusions retained |
| `devkit sync --registrations-only [-w WORKSPACE]` | Reconcile optional registrations after locked asset restoration; no asset changes |
| `devkit mcp status [-w WORKSPACE] --format json` | Desired/recorded/project facts, runtime and unknown host state |
| `devkit mcp serve --workspace-root EXECUTOR --configuration-workspace OWNER --profile local|read-only` | Native MCP stdio |

Ordinary sync reconciles project registration by default when the provider is installed; `[mcp] register = false`
opts out. No package installation, global settings, trust or permission changes happen during sync. Tracked and
visible foreign files stay unchanged. Follow [MCP setup](../../../guides/install/mcp.md) for intentional installation
and host validation. Setup does not prove native UI support.

| Code | Recovery |
| --- | --- |
| `MCP_REGISTRATION_CONFLICT` | Inspect edited/unowned entries or journal/ledger state; restore exact ownership before sync |
| `MCP_REGISTRATION_UNAVAILABLE` | Keep host-owned files unchanged; use host setup or an independently authorized CLI/PR route |
| `MCP_RUNTIME_UNAVAILABLE` | Install/select a retained runtime with matching service packages, then reconcile |
| `MCP_RUNTIME_STALE` | The serving process loaded devkit code that differs from the installed code; restart or reconnect the service, then call again (read-only tools still run) |
| `MCP_WORKSPACE_UNAVAILABLE` | Reconnect from an existing retained checkout; inspect partial effects |
| `MCP_INTERACTIVE_UNAVAILABLE` | Use a local interactive Host or independently authorized CLI/PR route |
| `HOST_MCP_FAILED` | Correct installed service entry points/runtime and reconnect |
| `HOST_MCP_ARGUMENT_INVALID` | Supply only the advertised tool schema's arguments |
| `HOST_CONFIRMATION_UNAVAILABLE` | Obtain conversational approval from the Host before invoking the lifecycle CLI; no authority was granted |

`mcp serve` is a native-protocol exception to ordinary output/format flags; startup errors remain advisories on
stderr. Other commands emit one JSON object or an MCP result sentinel and advisory notices. No output includes
other servers' settings or environment values. Elicitation accept alone is insufficient: approve must be true.

For shared or personal approval/response defaults, set `[presentation] language = "ko"` (`auto`, `en`, `ko`)
in shared config or ignored `.devkit/config.local.toml`. `devkit config show --effective` reports the requested and
resolved language, source and fallback; another value falls back to `en`, which `devkit sync`, `devkit status`
and `devkit config show` report as a `PRESENTATION_LANGUAGE_UNSUPPORTED` warning. Run sync for response-style
assets; approval forms read per request.
Explicit response-style bundle variables win. See `CAP-DIST-sync-and-transactions` and `CAP-INT-mcp-services`;
this does not localize host-owned controls or establish visible native Korean form support.
