---
id: CAP-MCP-runtime-registration
title: "MCP Runtime and Project Registration"
summary: "An optional retained MCP runtime binds invocation and presentation context to an owning workspace and reconciles ignored project registrations without changing host trust; lifecycle mutations run through Host-authorized CLI operations while shared artifact MCP remains available."
status: active
area: mcp
usecases:
  - UC-drive-development-to-integration
entrypoints:
  - packages/devkit-mcp/src/devkit_mcp/
  - packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py
  - packages/devkit-core/src/devkit_core/base/mcp.py
created: 2026-10-20
updated: 2026-10-22
---

# [CAP-MCP-runtime-registration] MCP Runtime and Project Registration

## Runtime contract

`devkit-mcp` ships `devkit_mcp`, mounts `devkit mcp`, discovers `devkit_dist.features.host.services` and adapts the
SDK-free contracts to FastMCP's stdio transport. `devkit_core.base.mcp` supplies dependency-free `McpTool`,
`Confirmation` and `ConfirmationReply`.
Services declare execution as read_only, bounded_write, preflight, interactive or approved_resume; omitted classification is
interactive regardless of descriptive MCP annotations. Schema validation and duplicate/unloadable service failures
remain deterministic. Native acceptance requires both accept and approve=true; decline, cancel, disconnect or
missing negotiated form capability grants no authority. Stdout contains only protocol traffic during serve.

The server records the installed devkit source when it starts: the SHA-256 of every Python file under the import
locations of the top-level `devkit` namespace and each `devkit_*` package. Before every call other than read_only, a
loaded module of those packages whose file is now absent, unreadable, unrecorded or different refuses the call with
`MCP_RUNTIME_STALE`, naming the stale modules, before execution guards and the tool run; its directive is to restart
or reconnect the retained service. Files the process never imported and rule or gate plugins loaded from managed
assets do not count. The server never re-imports, restarts or reselects a runtime itself, and the refusal grants no
authority. Read-only tools keep running.

The launch descriptor names three distinct locations: retained executable/import installation, retained executor
checkout and owning configuration workspace. The executor and workspace must share verified common Git identity.
Runtime selection checks the current and base virtualenv candidates, or an explicitly supplied executable, for
matching runtime/service versions and retained import locations. It never installs packages or searches arbitrary
interpreters. A linked-worktree interpreter or editable source is ineligible. No verified candidate produces
MCP_RUNTIME_UNAVAILABLE (`INPUT_ERROR`, target `--executable`) and no new entry: an error that refuses `mcp setup`
before any write, and a warning after ordinary sync.

Every protected invocation resolves the owning checkout's effective execution environment. Cloud prevents forms,
bounded writes, preflight and approved resume as well as interactive mutation; guards repeat after form/lock waits and before later
effects. The cloud registration profile exposes only declared read-only tools, and no registration is created if
none exist. Transport availability remains host-dependent. The configuration root cannot be changed by tool input.
Local Host approval can act on cloud-produced work because environment belongs to the calling Host, not the branch.

Workspace identity loss or malformed configuration fails closed. A deliberate removal of the exact owning checkout
may leave only terminal cleanup in the same approving call using its captured context. This exception cannot merge,
push, expand scope, survive a partial return or authorize resume. Process-local records cannot be transferred to
another server or reconstructed after restart. Retained read-only diagnostics remain available.

## Registration contract

Dist discovers the optional `devkit.mcp.registrations` provider without importing runtime/domain module names.
Ordinary sync reconciles selected Codex `.codex/config.toml` mcp_servers.devkit, Claude `.mcp.json`
mcpServers.devkit, and Antigravity `.agents/mcp_config.json` mcpServers.devkit entries when `[mcp] register` is true (default). The ignored local ledger at
`.devkit/transient/mcp/registrations.json` records exact owned entries, destinations, workspace, launch descriptor
and owned exclusion lines. It is separate from the committed installation receipt.

Tracked destinations are never changed, including tracked paths covered by ignore patterns. Existing visible
foreign untracked files remain unchanged. Absent paths require an existing ignore rule or a narrow clone-local
Git info/exclude line. Before adding a line, inspect registered linked worktrees for visible foreign files the
line would hide and refuse when any exist. Never modify tracked ignore files, ignore an entire host directory,
or use index flags to conceal changes. Retain owned exclusions on removal; the run that removes the last owned
entry reports them once (`MCP_EXCLUSIONS_RETAINED` notice). A tracked, visible or foreign-hiding destination is a
`MCP_REGISTRATION_UNAVAILABLE` warning naming the file, a selected host without an adapter `MCP_HOST_UNSUPPORTED`, a
same-name user or managed layer `MCP_REGISTRATION_SHADOWED`. A non-Git workspace is `MCP_CHECKOUT_REQUIRED`
(`INPUT_ERROR`, target `--workspace-root`): `mcp setup` and `mcp remove` check it, and that the workspace holds
`.devkit/` (`ARGUMENT_INVALID`), before taking any lock; ordinary sync reports it as a warning.

`mcp setup --host HOST` limits registration to the named hosts (repeatable; default: the configured agents). It
reconciles the whole project state, so the owned entries of every host not named are removed; a later run without
`--host` registers the configured agents again.

Hold the common Git exclusion lock before the checkout project lock. Validate destinations before writes, reject
symlinks/nonregular files, malformed/duplicate-key configuration and malformed ownership state
(`MCP_REGISTRATION_CONFLICT`, `INTERACTION`: the user decides how to restore the file in `[TARGET]`). Only an exact
previously owned entry can change or disappear; unowned identical entries are not adopted. An absent whole file
can be recreated; a missing owned entry in an existing file is a conflict. Foreign settings remain semantically
intact, and no-op preserves bytes/mode. Recheck tracked/ignored state and captured file bytes before writes.

A recoverable registration journal binds destinations and ledger updates. An interrupted operation is recovered
before another ordinary change (a plan that finds the journal is `MCP_REGISTRATION_INTERRUPTED`, `AUTO` with
`uv run devkit sync`); a registration write while the ledger is not yet Git-ignored is `MCP_LEDGER_UNIGNORED`,
`AUTO` with the same fix; foreign edits or newly tracked/visible destinations during recovery refuse mutation.
Installed narrow exclusions survive rollback because another checkout may already depend on them; the local ledger
retains their ownership and recovery itself is repeatable. Dry-run/check compute the same
plan without writes, installation or host launches. Locked sync validates without host-file changes and directs
changed existing local configuration to ordinary sync. An absent fresh-checkout registration does not block
locked asset restoration. After restoration, worktree setup invokes dist-owned `sync --registrations-only`,
which discovers the optional provider and reconciles local entries without touching assets or the receipt.
`devkit sync --registrations-only [-w DIR] [--format text|json]` accepts no other sync mode or selection flag
(`ARGUMENT_INVALID`) and prints `[MCP_REGISTRATION: changes=<n>]` (JSON `{"actions": [...], "notices": [...]}`).
Each planned change carries its path (relative to the checkout, or absolute for a linked worktree's common Git
info/exclude) and the kind `create`, `update` or `remove` from the captured bytes. A read-only check answers which
selected hosts ordinary sync would register but this checkout does not hold (register in effect, provider entry
point installed but not loaded, eligible destination, no matching owned entry), so status can report a fresh
checkout's missing registration without importing devkit-mcp or the MCP SDK.
Without an installed provider and ownership state this mode does nothing. The trusted lifecycle guard runs
again before that initialization; copied opt-out and cloud configuration remain effective. Opt-out, uninstall and selected-agent removal retire only exact
owned entries. An unloadable installed provider is an error, not an uninstall signal.

Known user/ancestor/local/managed same-name declarations are inspected read-only and reported as collisions;
unknown effective selection remains unknown. Resolve global entries through host-owned tools. Status distinguishes
desired, recorded and project registration, runtime availability and unknown effective connection/form/trust/
permission state, without returning environment values or other servers' settings. The always-unknown facts appear
in JSON only; text prints `[MCP: action= package= runtime=]` and one `[MCP_HOST: ...]` line per host, and
`--descriptor` prints `[MCP_DESCRIPTOR: command= profile= executor= workspace=]`.

## Host workflow

The Host validates worker boundaries, committed scope and required checks, presents the exact report, target and
effects, obtains conversational approval under `ask`, then invokes lifecycle CLI operations. The CLI revalidates
source identity and policy but does not authenticate the conversational decision. Workers do not request business
approval. Shared artifact MCP services retain their existing access rules. Trust, tool and sandbox prompts remain
independent from business approval.


Trusted lifecycle child operations inherit a refusal-only execution constraint naming the original configuration
workspace, common Git identity and filesystem identity. It contains no request, approval allowlist or terminal
removal state and cannot authorize any operation. Child sync rechecks that owner after clone/project locks and
before transaction writes, including recovery. The target checkout's copied local configuration cannot replace
the owner's constraint. Missing/changed owner identity or cloud transition stops remaining writes; partial
transactions retain their journals for an independently authorized recovery. The parent rechecks on child return.

## Form presentation context

The existing invocation binding also lets core presentation resolution select the owning configuration workspace
for domain-owned form text. The retained executor's preferences do not override it. Language is read once per form,
with no language/workspace tool argument and no additional serialized approval authority. Execution/environment and
workspace identity guards still run independently before and after confirmation and before effects. Static domain
copy and host-owned display limits are specified in `CAP-INT-mcp-services` and `CAP-DLV-proposal-incubation`.

## Shared artifact services

`devkit_dist.features.shared.mcp` supplies the fixed `bounded_write` tool `shared_put` and the `read_only` tools `shared_get` and `shared_list`.
Bounded writes invoke a validated domain API without a business approval form; this classification grants neither
host permission nor arbitrary filesystem authority. Cloud discovery omits them and invocation rejects forged calls.
Unknown execution classifications fail closed. Both reads and writes bind configuration to the owning workspace,
including shared.adapter; executor preferences and request arguments cannot select another workspace.
`CAP-COLL-shared-artifacts` specifies artifact identity, retention, transport parity and adapter semantics.
