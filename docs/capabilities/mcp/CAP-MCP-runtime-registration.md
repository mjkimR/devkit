---
id: CAP-MCP-runtime-registration
title: "MCP Runtime and Project Registration"
summary: "An optional retained MCP runtime binds native approval to an explicit configuration workspace, while dist reconciles exact ignored project registrations without changing host trust or global settings."
status: active
area: mcp
created: 2026-10-20
updated: 2026-10-20
---

# [CAP-MCP-runtime-registration] MCP Runtime and Project Registration

## Runtime contract

`devkit-mcp` ships `devkit_mcp`, mounts `devkit mcp`, discovers `devkit.host.services` and owns SDK stdio/form
adaptation. `devkit.core.mcp` supplies dependency-free `McpTool`, `Confirmation` and `ConfirmationReply`.
Services declare execution as read_only, preflight, interactive or approved_resume; omitted classification is
interactive regardless of descriptive MCP annotations. Schema validation and duplicate/unloadable service failures
remain deterministic. Native acceptance requires both accept and approve=true; decline, cancel, disconnect or
missing negotiated form capability grants no authority. Stdout contains only protocol traffic during serve.

The launch descriptor names three distinct locations: retained executable/import installation, retained executor
checkout and owning configuration workspace. The executor and workspace must share verified common Git identity.
Runtime selection checks the current and base virtualenv candidates, or an explicitly supplied executable, for
matching runtime/service versions and retained import locations. It never installs packages or searches arbitrary
interpreters. A linked-worktree interpreter or editable source is ineligible. No verified candidate produces
MCP_RUNTIME_UNAVAILABLE and no new entry.

Every protected invocation resolves the owning checkout's effective execution environment. Cloud prevents forms,
preflight and approved resume as well as interactive mutation; guards repeat after form/lock waits and before later
effects. The cloud registration profile exposes only declared read-only tools, and no registration is created if
none exist. Transport availability remains host-dependent. The configuration root cannot be changed by tool input.
Local Host approval can act on cloud-produced work because environment belongs to the calling Host, not the branch.

Workspace identity loss or malformed configuration fails closed. A deliberate removal of the exact owning checkout
may leave only terminal cleanup in the same approving call using its captured context. This exception cannot merge,
push, expand scope, survive a partial return or authorize resume. Process-local records cannot be transferred to
another server or reconstructed after restart. Retained read-only diagnostics remain available.

## Registration contract

Dist discovers the optional `devkit.mcp.registrations` provider without importing runtime/domain module names.
Ordinary sync reconciles selected Codex `.codex/config.toml` mcp_servers.devkit and Claude `.mcp.json`
mcpServers.devkit entries when `[mcp] register` is true (default). The ignored local ledger at
`.devkit/transient/mcp/registrations.json` records exact owned entries, destinations, workspace, launch descriptor
and owned exclusion lines. It is separate from the committed installation receipt.

Tracked destinations are never changed, including tracked paths covered by ignore patterns. Existing visible
foreign untracked files remain unchanged. Absent paths require an existing ignore rule or a narrow clone-local
Git info/exclude line. Before adding a line, inspect registered linked worktrees for visible foreign files the
line would hide and refuse when any exist. Never modify tracked ignore files, ignore an entire host directory,
or use index flags to conceal changes. Retain owned exclusions on removal and report manual cleanup after checking
all worktrees. Non-Git and unsupported selected hosts receive explicit unavailable diagnostics.

Hold the common Git exclusion lock before the checkout project lock. Validate destinations before writes, reject
symlinks/nonregular files, malformed/duplicate-key configuration and malformed ownership state. Only an exact
previously owned entry can change or disappear; unowned identical entries are not adopted. An absent whole file
can be recreated; a missing owned entry in an existing file is a conflict. Foreign settings remain semantically
intact, and no-op preserves bytes/mode. Recheck tracked/ignored state and captured file bytes before writes.

A recoverable registration journal binds destinations and ledger updates. An interrupted operation is recovered
before another ordinary change; foreign edits or newly tracked/visible destinations during recovery refuse mutation.
Installed narrow exclusions survive rollback because another checkout may already depend on them; the local ledger
retains their ownership and recovery itself is repeatable. Dry-run/check compute the same
plan without writes, installation or host launches. Locked sync validates without host-file changes and directs
changed existing local configuration to ordinary sync. An absent fresh-checkout registration does not block
locked asset restoration. After restoration, worktree setup invokes dist-owned `sync --registrations-only`,
which discovers the optional provider and reconciles local entries without touching assets or the receipt.
Without an installed provider and ownership state this mode does nothing. The trusted lifecycle guard runs
again before that initialization; copied opt-out and cloud configuration remain effective. Opt-out, uninstall and selected-agent removal retire only exact
owned entries. An unloadable installed provider is an error, not an uninstall signal.

Known user/ancestor/local/managed same-name declarations are inspected read-only and reported as collisions;
unknown effective selection remains unknown. Resolve global entries through host-owned tools. Status distinguishes
desired, recorded and project registration, runtime availability and unknown effective connection/form/trust/
permission state, without returning environment values or other servers' settings.

## Host workflow

The Host validates worker boundaries, committed scope and required checks, presents the result and calls the native
approval tool. Workers do not request business approval. No extra chat approval or prepare call is required when
connected native forms work. Trust/tool/sandbox prompts remain independent. Missing UI is never approval: install
and connect intentionally, or use an independently authorized explicit CLI/PR route. Real Codex and Claude terminal
UI validation is separate evidence from simulated protocol tests; desktop and VS Code adapters are outside scope.
