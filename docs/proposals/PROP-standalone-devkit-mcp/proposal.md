---
id: PROP-standalone-devkit-mcp
title: Independent devkit-mcp runtime and default approval integration
summary: "Extract the shared MCP runtime into devkit-mcp, manage project registrations through sync, and make native MCP the default interactive approval route while retaining domain services in their owning packages."
status: accepted
created_at: 2026-10-20
target_area: host/
priority: high
size: L
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/
    - pyproject.toml
    - uv.lock
    - justfile
    - AGENTS.md
    - .github/workflows/
    - docs/architecture/
    - docs/development/
    - docs/decisions/
    - packages/devkit-dist/src/devkit/core/
    - packages/devkit-dist/src/devkit/host/
    - packages/devkit-dist/src/devkit/distribution/
    - packages/devkit/src/devkit/integration/
    - packages/devkit-spec/src/devkit_spec/handoff_mcp.py
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec/
    - scripts/
    - guides/install/
    - docs/capabilities/host/
    - docs/capabilities/integration/
    - docs/capabilities/delivery/
    - docs/capabilities/worktree/
  excludes:
    - packages/devkit-advisory/
    - packages/devkit-spec/src/devkit_spec/scope/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-standalone-devkit-mcp] Independent devkit-mcp runtime and default approval integration

## 1. Background & Hypothesis

The selected direction is an independent optional `devkit-mcp` wheel. It owns stdio transport, native form
adaptation, installed service discovery and runtime diagnostics. Domain execution stays in `devkit-agt`
(integration) and `devkit-spec` (handoff). Ordinary hooks and project-file synchronization stay in `devkit-dist`.

`PADR-independent-mcp-runtime-with-project-registration-and-environment-guards` records the package and authority
boundary. `materials/runtime-and-registration-evidence.md` records code evidence, official platform support,
alternatives and the verification matrix. These are proposed contracts pending `plan-accept`, not implemented
behavior. No Development or integration is authorized by this Planning run.

## 2. Settled Design

### Package and service ownership

- Create `packages/devkit-mcp/` with Python namespace `devkit_mcp`, tests and README. Depend on the exact
  `devkit-dist` release plus `mcp>=1.30,<2` and the directly imported `jsonschema` dependency. Add the new wheel to
  the foundation lockstep release without changing the existing advisory API. No namespace path overlaps.
- Move dependency-free `McpTool`, `Confirmation` and `ConfirmationReply` to `devkit.core.mcp`. Both domain packages
  import those contracts without requiring the optional SDK. Keep `devkit.host.services` as the service entry-point
  group; a group name alone does not imply ownership by `devkit.host`. The new runtime loads it.
- Mount `devkit mcp` through `devkit.commands`; remove `devkit host mcp` and its old modules instead of adding
  compatibility shims. Preserve config/status/serve capabilities under the new command; setup becomes explicit
  project reconciliation and remove removes exact owned project entries. Drop implicit user-scoped setup.
- Remove `devkit-dist[mcp]`; keep `devkit-agt[mcp]` as a convenience dependency on the same-version `devkit-mcp`.
  A dist-only install imports no SDK/runtime. Runtime-only installation depends on dist and can start/discover an
  empty service set. Installing agt or spec makes only those packages' services available.
- Add a narrow `devkit.mcp.registrations` provider contract to dist's host layer. The runtime provider supplies its
  launch descriptor. Dist owns host-file reconciliation so it can remove previously owned entries after the
  runtime package has been uninstalled. This is the same dependency-inversion direction as existing extensions;
  dist never imports `devkit_mcp`, integration or spec by module name. No generic remote plugin manager is added.

### Project registration and ownership

Sync reconciles one `devkit` entry for each selected supported agent: Codex CLI in `.codex/config.toml`
(`[mcp_servers.devkit]`), Claude Code in project `.mcp.json` (`mcpServers.devkit`). `[mcp] register = true` is the
default when the runtime provider is installed; `false` opts out. It is a local presentation/integration preference,
not an approval policy. Sync installs no packages, edits no global registration, trusts no project/server and changes
no host permission setting. Unsupported selected hosts get an explicit unsupported diagnostic.

The desired descriptor and ownership ledger are machine-local and excluded from the committed installation
receipt. Dist records the exact entry it last wrote under ignored `.devkit/transient/mcp/registrations.json`, with
host, destination, server key, owning checkout and launch descriptor. It never claims the complete host file.
Host files can contain tracked settings. Automatic reconciliation MUST NOT dirty a checkout: a tracked destination
is never modified, even when Git ignores its path. Return `MCP_REGISTRATION_UNAVAILABLE` with explicit CLI/PR
fallback and host-owned setup instructions. Do not weaken clean-tree checks, stage generated entries, use
skip-worktree/assume-unchanged, or rewrite tracked `.gitignore` to conceal the change.

An absent destination may be created only after it is already ignored or sync adds a narrowly scoped, owned entry
to clone-local Git `info/exclude`; never ignore an entire host directory. A pre-existing ignored directory already
satisfies this prerequisite. Existing untracked destinations are writable only when already ignored; visible
foreign untracked files are left unchanged with the same unavailable diagnostic, rather than silently hidden.
Preserve foreign settings in an eligible destination. The local ownership ledger records exact exclude entries it
created. Exclusions remain as clone-local setup after registration removal; report their retention and an explicit
manual cleanup instruction instead of exposing another worktree's generated or foreign file. Before adding a
pattern, inspect registered linked worktrees for currently visible foreign untracked files it would newly hide;
refuse the exclusion with an actionable diagnostic if any exist. A broad pre-existing ignore rule is user-owned,
never adopted or removed. Exclude changes use the common-Git-directory lock as well as the checkout registration
lock, in a fixed order; normal linked worktrees share that file. Existing patterns remain byte-preserved. A non-Git workspace
cannot satisfy the native Git workflow and receives an explicit unsupported registration diagnostic in this scope.

The generated absolute-path entry is local setup, not a tracked portable asset. Sync checks tracked/ignored state
again immediately before its registration write and aborts on changed ownership/state. Setup/remove use the same
cleanliness and ownership rules; they do not force-write tracked configuration. An independently managed existing
host registration may still provide the native route; status reports it without adopting or changing it.

Reconciliation uses the project lock, validates every destination before writes, rejects symlinks/nonregular files,
duplicate keys and malformed config, and atomically updates entries and the local ledger with recoverable journal
state. Dry-run/check compute the same plan without provider side effects, package installation or host launches.
No-op preserves bytes/mode. Only an exact previously owned entry can be updated or removed; unowned identical,
edited or duplicate entries are conflicts. A missing whole destination can be recreated; a missing owned entry in
an existing destination is a conflict. Foreign entries and metadata are preserved semantically.

Uninstall, explicit opt-out and selected-agent removal remove only exact owned entries on the next ordinary sync.
A missing provider with no ledger is simply absent; an unloadable installed provider is an error, never equivalent
to uninstall. Malformed ownership state refuses mutation. An interrupted operation is recovered before another
registration change; no successful transaction claim is made on partial state. Locked sync validates existing
registrations without altering shared host files; ordinary sync is the deterministic recovery for changed local
configuration. Registration changes remain separate from portable asset-receipt validation.

Sync inspects known same-name user/local/project layers read-only and reports collisions rather than silently
shadowing, replacing or adopting them. Codex ancestor and user declarations, and Claude local/user/managed
declarations, may affect effective selection. Unknown effective state is reported as unknown. Resolve existing
user-scoped devkit entries with the host's own tools, then sync; no automatic migration or global cleanup.
Status distinguishes desired/recorded/project/effective registration, package/runtime availability, connection,
form UI, trust and permissions. Writing config proves only registration; higher-priority settings and trust can
still disable it. Status redacts environment values and other servers' settings.

### Runtime lifetime and configuration binding

The launch descriptor separately names the retained interpreter/import installation, retained repository executor
root, and owning configuration workspace. Select a retained base or tool-installed runtime with the same required
service packages; validate its module availability and lexical venv path, including editable source locations.
A task worktree's interpreter or editable import path is never used for a server that can remove that worktree.
When no retained runtime exists, sync reports `MCP_RUNTIME_UNAVAILABLE` and leaves a new registration absent; it
never installs or searches arbitrary interpreters. Explicit setup can select a verified retained executable.

The owning configuration workspace is the checkout being synchronized, passed as an explicit server launch
argument; never derive it from client cwd, MCP roots or the executor's cwd. A linked checkout resolves the executor
base through verified common-Git-directory identity and requires the same clone. The executor's ordinary integration
safety checks still validate target branch and cleanup scope. Runtime binaries remain on disk after task removal.
The configuration path can disappear when its worktree is cleaned. Before deliberately removing that exact
owning workspace, validate its identity and local environment one final time. Only terminal cleanup already
included in the same in-flight approval may finish using that captured context after the expected self-removal;
this exception cannot perform a new merge/push, expand scope, survive a returned partial result, authorize resume,
or excuse an unexpectedly missing workspace. Reject later mutation/approval requests with
`MCP_WORKSPACE_UNAVAILABLE`; reconnect from a retained checkout. Read-only retained diagnostics remain available. No daemon, shared approval store or reconnect token is
introduced. Concurrent processes have independent confirmation authority and use existing domain locks; after
restart a request ID cannot resume another process's approval.

### Environment and approval restrictions

Consume the core resolver from `SPEC-local-config-execution-environment`: `[execution] environment` is `local` or
`cloud`, default `local`, with `.devkit/config.local.toml` copied by `devkit worktree start` before setup/first sync
and independent thereafter. No live parent fallback or automatic propagation is assumed. The accepted design's API
is a Development dependency and its implementation must be integrated/rechecked before environment work starts.

The agreed provisional core APIs are `read_effective_config(root)` and `resolve_execution_environment(root)`,
with the latter reporting the environment and its source. A valid workspace with no local overlay uses the shared
value/default; this is distinct from a missing or wrong workspace identity.

Resolve the owning configuration workspace on each invocation, before opening a form and after the reply before
mutation, including resume and later mutation steps. Malformed/missing required config identity fails closed, except the narrowly bounded same-call terminal cleanup
after expected self-removal described above. A
`cloud` result refuses interactive approval with stable `MCP_INTERACTIVE_UNAVAILABLE` and an action to use a local
interactive Host or an independently authorized explicit CLI/PR route. No wait, form, worktree creation, merge,
push or cleanup starts under that refusal. Guard after waiting for locks as well as after the form. A transition
after some authorized effects yields a partial domain result and stops remaining mutations; it does not claim
rollback. Do not erase already granted scope or convert refusal into new authority.

Add an explicit service execution classification, separate from MCP descriptive annotations: `read_only`,
`preflight`, `interactive`, `approved_resume`; default is interactive. Status is read-only; integration prepare is
preflight (it may fetch and retain state), integrate and handoff are interactive, and resume is approved_resume.
Cloud auto-registration uses a read-only profile exposing only declared read-only tools; no entry is created if
none exist. Local registration exposes installed tools. Both profiles reject interactive and resume invocation in
cloud even for stale local registrations and direct serve launches. The confirmation callback also enforces the
restriction; domains enforce it at their own mutation boundaries so resume cannot bypass it. The profile never
turns client-provided flags or annotations into authority. No universal claim that cloud supports stdio is made:
cloud host connectivity is separate, and an unavailable transport leaves explicit CLI inspection as recovery.

The environment is that of the calling Host/config workspace, not the provenance of the source branch. A local
Host may review and approve cloud-produced work. Workers return verified scope to their Host and never ask for
business approval themselves. Tool arguments cannot choose an execution environment or a different configuration
root. In local mode the actual negotiated client form capability remains required. Preserve accept+approve=true,
decline/cancel behavior, exact scope, stale-state guards and process-local resume authority. Test the SDK's
normalization of empty form capability and negotiated protocol versions instead of assuming every host supports
an identical elicitation version.

### Default workflow and fallback

Direct and local-orchestrated guidance prefers one Host-owned native approval when devkit MCP is connected. The
Host first validates worker boundaries, committed scope and required checks, presents the result, then calls the
approval tool; do not require an extra chat approval or `integration_prepare`. Trust/tool/sandbox prompts stay
independent and cannot be promised away. Guidance never changes host trust settings to make this route work.

Absent runtime, disconnected server, unavailable form or unsupported cloud transport yields an explicit recovery:
install/connect the runtime intentionally, or use the existing conversationally authorized CLI/PR route. A
previous user authorization can be used only when it already covers the exact action; missing UI is not approval.
No automatic policy dispatcher or unattended mutation authority is added. Handoff retains its effort choice and
never authorizes final integration. Worker contracts and integration/handoff guidance reflect Host ownership.

## 3. Implementation Scope and Acceptance Evidence

The `packages/` parent boundary is solely for the new `packages/devkit-mcp/`, affected pyprojects/READMEs/tests,
and imports of moved contracts; it does not permit unrelated package refactors. Update dist core/host/distribution,
agt integration and spec handoff plus relevant bundle skills/subagents, installation guides, root tooling and
architecture. `target-docs.md` names Living Spec targets. The new ADR supersedes only the MCP ownership/version
clauses of `ADR-dist-module-split` and `ADR-dist-command-composition`; hook, CLI-executable and receipt ownership
remain unchanged. Reconcile the explicit project-settings exception in `CAP-HOST-lifecycle-observation`.

Acceptance must demonstrate:

1. Built-wheel matrices: dist alone, runtime+dist, agt without SDK, agt[mcp], and spec+runtime. No circular dependency,
   duplicate installed path, missing direct dependency or import via the monorepo masks packaging faults. CLI
   discovery and server version identify devkit-mcp; dist remains the owner of the devkit executable/receipt.
2. Extraction preserves schema validation, service duplicate/load failures, stdout protocol isolation, native
   accept/decline/cancel/disconnect handling and missing-form refusal, under the supported installed SDK/protocol.
3. Repeated sync converges both host files and ownership state; dry-run/check write nothing; opt-out, uninstall,
   unsupported host, absent retained runtime, user shadowing, edited entry, duplicate key, file-mode preservation,
   external edit and journal recovery have explicit tests. Absent host files become locally excluded, existing ignored
   destinations remain eligible, and tracked/visible foreign untracked destinations remain byte-identical with
   actionable unavailable diagnostics. Exercise worktree start setup, native handoff and integration clean-state
   preflights for each case; no tracked ignore-file changes are allowed. Common exclude updates and per-checkout
   writes serialize. No tests or
   smoke checks edit real user host settings or trust stores.
4. Local-to-cloud changes before invocation, during form wait and during lock wait stop the next mutation;
   cloud stale/direct registrations and resume cannot obtain/use interactive approval. Read-only status works
   without elicitation capability. Prepare is not falsely advertised as the cloud read-only subset. Cross-worktree
   tests use different copied config values and verify the owning config path, not the retained executor's value.
5. Removing the task does not remove the executable/import source. Reconnect cannot import old process authority;
   concurrent server approval records remain independent. A vanished config workspace prevents new approval and
   resume; unexpected removal stops mutation, while only the declared same-call terminal cleanup may finish after
   deliberate removal of its own config workspace.
6. Real Codex CLI and Claude Code terminal sessions separately record registration, trust, discovery, native form,
   decline/cancel, post-approval effects and permission prompts with versions. Simulated transport tests alone do
   not establish UI support. If real-host evidence is unavailable, report it as unverified and do not claim that
   host is fully validated. No desktop/VS Code/SDK adapter is included.

Development keeps `dev_effort: medium`: cross-package review and separate reconcile verification are required,
but this work performs no release, data migration or advisory API change. Run relevant lint/types/tests via
`just test-affected`, package layering/dist-only checks, built-wheel smoke and governance checks. Update affected
selection so new runtime changes select its tests and domain consumers; preserve full fallback. Release-script
changes are validated without publishing. Extraction is the first internal stage; environment registration and
guard work follows the integrated configuration contract, then guidance and host evidence. This is one coherent
proposal, not permission for a partial extraction-only completion.

## 4. Lifecycle & Retirement Criteria

Ready for `plan-accept` when the PADR, evidence, cross-proposal dependency and challenger disposition are reviewed.
Acceptance selects the design; it does not prove runtime/UI behavior or start Development. No essential design
question remains for this turn beyond accepting or declining the proposal.

Scope excluded: coordination storage and generic shared-filesystem APIs (`PROP-worker-shared-state-mcp`),
policy-authorized unattended merge/cleanup (`PROP-policy-authorized-integration`), remote multi-host serving,
VS Code/SDK/desktop adapters, trust/sandbox bypass, global host configuration mutation and compatibility shims.
Future shared-state services can consume the runtime contract without moving their domain behavior into it.
