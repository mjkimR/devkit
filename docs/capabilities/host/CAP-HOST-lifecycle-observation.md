---
id: CAP-HOST-lifecycle-observation
title: "Host Lifecycle Observation"
summary: "Host lifecycle hook dispatch, exact project MCP registration for Codex, Claude Code and Antigravity, and read-only installation diagnostics; optional MCP transport lives in devkit-mcp."
area: host
status: active
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/host/cli.py
  - packages/devkit-dist/src/devkit_dist/features/host/models/errors.py
  - packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py
created_at: 2026-10-17
---

# [CAP-HOST-lifecycle-observation] Host Integration

`devkit_dist.features.host` (shipped by `devkit-dist`, so native hooks work without `devkit-agt`) connects host
lifecycle events to installed service handlers. `devkit_dist.features.distribution` deploys hook
definitions and manages their registrations. The host module owns native input/output and service dispatch; a
service owns its domain behavior. The integration service uses this boundary without placing Git
execution, SDD models or approval policy inside an adapter. Quick reference: [reference.md](../../development/reference/host.md).

## 1. Boundaries

- `host/hooks`: host-neutral `HookDefinition`, `HookEvent` and `HookResponse` contracts.
- `host/adapters/codex`: Codex CLI event capabilities, command registration and native response rendering.
- `host/runner`: receipt-bound dispatch to the `devkit_dist.features.host.handlers` entry-point group.
- `distribution`: manifest validation, selection, overrides, shared-file planning, receipt, transaction and removal.

Among features, `host` MUST depend only on `devkit_dist.features.project` (`RULE-architecture`). `distribution` MAY depend on `host`. No service is required to import
distribution internals. The separate `devkit_mcp` runtime supplies optional FastMCP stdio transport for installed
service factories (`devkit_dist.features.host.services`). `CAP-INT-mcp-services` defines the CLI
integration approval contract, while `host/registrations` reconciles exact local project entries. Host adapters MUST NOT grant filesystem/network permission
or contain a Git executor, automatic policy dispatch or background recovery. Setup: [MCP services](../../development/reference/host.md#mcp-services).

The initial adapter targets locally executed Codex CLI command hooks on POSIX. Other hosts are unsupported.
Protocol definitions follow [Codex Hooks](https://learn.chatgpt.com/docs/hooks); deployment and subprocess tests
verify the generated command, not interactive host trust or event delivery. Those SHOULD be recorded separately in a
real Codex session. A configured hook is not proof of a running hook.

## 2. Hook assets

A bundle declares one `hook` asset per handler registration:

```toml
[[assets]]
id = "trace-tools"
kind = "hook"
source = "hooks/trace-tools.toml"
```

The source is one UTF-8 TOML file, not a shell command or Python script:

```toml
host = "codex"
event = "PreToolUse"
handler = "observe"
matcher = "^Bash$"
timeout = 10
```

Required fields are `host`, `event`, `handler`. `matcher` defaults to the empty string (all occurrences), and
`timeout` defaults to 10 seconds, an integer from 1 through 600. Unknown fields are errors. Only `codex` is supported;
events are `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionEnd`. Nonempty matchers on
`UserPromptSubmit` or `Stop` MUST be rejected because Codex ignores them. `SessionEnd` MUST have an explicit timeout
of at most 3 seconds. The native host interprets matcher regular expressions; devkit MUST NOT translate them.

Sync MUST register only a selected hook targeting a selected agent. Unsupported selected agents are reported under
`unprojected`. `variants`, `seeded` and `invocation` are not supported for hooks. Project overrides follow the normal
asset override contract; sync MUST validate the effective definition before changing host configuration.

## 3. Shared configuration ownership

`devkit bundle plan` lists generated registrations under `host_hooks`. `sync --dry-run` and `sync --check` include
the shared host configuration in the same planning path as ordinary sync. Planning MUST NOT run code.

For Codex, sync MUST update only receipt-recorded matcher groups in `.codex/hooks.json`. The receipt's `host_hooks`
array stores `host`, `asset` (`bundle:id`), `event`, `handler`, `command`, `matcher`, `timeout`; it MUST NOT claim ownership of the
whole host file through `files`. Existing top-level metadata, foreign events and foreign matcher groups MUST be
preserved semantically, including their relative order. JSON whitespace can change when entries change; a no-op
MUST keep the exact bytes and the existing file mode. Duplicate JSON keys and malformed hook maps MUST be refused.

Each previous owned group MUST occur exactly once in an existing host file. IF an owned group is missing, edited or
duplicated, THEN sync MUST fail with `HOST_HOOK_CONFLICT` before any transaction writes. Identical unowned groups
MUST be refused rather than adopted.
Restore the recorded group from the receipt after reviewing local edits, then sync. No force/adopt mode exists.
An absent entire file can be restored from the receipt, including by `sync --locked` when nothing else changes.
Locked sync MUST NOT edit an existing shared host file; a changed selection or definition is `RECEIPT_STALE`.

Removing a hook, deselecting its bundle or dropping Codex from the agent selection MUST remove only its exact owned
group. An empty `hooks` object and the file container remain. The shared-file change MUST participate in the
existing sync journal and rollback. Symlinked or nonregular host destinations MUST be refused. The devkit project
lock serializes devkit writers; other editors do not take that lock, so users SHOULD NOT edit host configuration
during sync.

This is a narrow exception to distribution's host-settings boundary: credentials, project trust, hook trust, user settings and permission settings remain host-owned. Exact ignored
project MCP entries are separately reconciled under `CAP-MCP-runtime-registration`. Existing inline hooks MUST be
preserved; Codex can load them alongside `hooks.json` and report its own configuration warning.

## 4. Runtime and service extension

The generated command is `devkit host hook --host codex --asset <bundle:id>`. The Codex process MUST have the
installed `devkit` executable on its PATH; for a project-local installation, launch Codex with the project's
`.venv/bin` prepended to PATH. The hook MUST NOT run a package installation or network operation. The executable
and its environment MUST remain available for the lifetime of the host session.

The command MUST read at most 1 MiB of native JSON, use the event's absolute `cwd` to find the devkit project (also from
a subdirectory), verify the receipt-selected source, registration and event, and invoke exactly one installed handler.
WHILE a sync journal is interrupted, the command MUST NOT dispatch. The host's registration timeout bounds the process.

Service packages register a callable:

```toml
[project.entry-points."devkit.host.handlers"]
my-context = "my_package.host:context"
```

```python
from devkit_dist.features.host import HookEvent, HookResponse

def context(event: HookEvent) -> HookResponse:
    return HookResponse(additional_context="Read the repository's delivery contract.")
```

A handler receives `host`, native event `name`, project `root`, qualified `asset` and the native `payload` mapping.
It MUST return `HookResponse()`, or context of at most 4096 characters for `SessionStart`, `UserPromptSubmit`,
`PreToolUse` or `PostToolUse`. Codex receives `hookSpecificOutput` with `hookEventName` and `additionalContext`.
Other events accept an empty response only. Handler identity is bound into the receipt as well: changing a hook
override to another service requires sync before dispatch, even when the native command stays the same. Missing, duplicate or unloadable handlers and malformed responses are
`HOST_HOOK_DISPATCH_FAILED`. Handler exceptions MUST be reported by type without copying exception text that could
contain input. Python stdout from handlers MUST be discarded to preserve the native response protocol. Handlers MUST NOT
print, log sensitive event content, spawn detached work or interpret event input as approval authority.

The first path is advisory: input/configuration/handler failures MUST emit a warning on stderr, native `{}` on stdout
and exit 0. It MUST NOT grant approval or permission, and it cannot enforce a security boundary. A host timeout also has
host-defined behavior. Domain services MUST enforce their own readiness and authorization at mutation time.

`devkit host hook` is a documented host-protocol exception to normal CLI output: stdout MUST be the native response,
with no result sentinels or ordinary error object. `host status` MUST follow the normal output/advisory contract.

## 5. Observer and inspection

The built-in `observe` handler MUST store only `host`, `asset`, `event` and UTC `received_at`, atomically, in
`.devkit/transient/host/<host>/<bundle>/<asset>.json` (mode 0600). Each file holds the latest event, not an audit log
or retry journal. It MUST NOT store session IDs, cwd, prompts, tool inputs, commands or transcript content. Concurrent
observations can overwrite the latest timestamp; counts and exactly-once delivery are not claimed.

`devkit host status --format json` reports each registration, source/handler validity and last observer metadata.
`runtime_on_path` describes the current inspection process; it cannot establish the PATH of a separately launched
Codex process. Trust and execution permissions MUST always be reported as `unknown`. `devkit status` MUST include hook
installation problems without loading service handlers. Neither status command establishes effective host enablement.

The observer handler remains available to hook definitions supplied by installed bundles. Business approvals, setup
and trust prompts, and execution-permission prompts are separate observations.

## 6. Project MCP registration

Dist owns the narrow `devkit.mcp.registrations` provider boundary and project-file reconciler described by
`CAP-MCP-runtime-registration`. It does not own MCP transport. Installing the optional runtime enables
ordinary sync to reconcile exact local Codex, Claude Code and Antigravity entries; `[mcp] register = false` opts out. Uninstall,
opt-out and selected-agent removal MUST retire only exact owned entries. Host trust, permissions and global settings
remain host-owned. Registration facts do not prove connectivity.


Approval language is bounded supplied content under `CAP-INT-mcp-services` and
`CAP-DLV-proposal-planning`. The owning workspace's presentation preference MUST NOT localize hooks, tool results,
host chrome, trust or permission prompts, or change any registration or execution guard.
