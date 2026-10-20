---
id: PROP-local-config-execution-environment
title: Local configuration and execution environments
summary: "Add ignored checkout-local configuration overlays and an explicit cloud execution environment, with creation-time worktree copying and shared receipt preservation."
status: accepted
created_at: 2026-10-20
target_area: distribution/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-dist/src/devkit/core/
    - packages/devkit-dist/src/devkit/distribution/
    - packages/devkit-dist/tests/
    - packages/devkit/src/devkit/worktree/
    - packages/devkit/tests/worktree/
    - packages/devkit/tests/rules/
    - docs/capabilities/distribution/
    - docs/capabilities/worktree/
    - docs/development/reference/distribution.md
    - docs/architecture/ARCH-05-4-distribution-components.md
    - guides/
  excludes:
    - packages/devkit-advisory/
    - packages/devkit-spec/src/devkit_spec/mcp.py
task_kind: feature
workflow: sdd-proposal
---

# [PROP-local-config-execution-environment] Local configuration and execution environments

## 1. Background & Hypothesis

Shared configuration cannot express personal preferences and execution-environment constraints without changing
tracked repository files. A response-style language preference is one concrete consumer; a cloud run that cannot
request interactive approval is another. Introduce `.devkit/config.local.toml` as an ignored local overlay while
keeping `.devkit/config.toml` the shared configuration. Manage `/config.local.toml` in `.devkit/.gitignore` without
replacing unrelated ignore entries.

This supplies the configuration contract consumed by `PROP-standalone-devkit-mcp`. Execution environment describes
runtime constraints; it does not grant approval or turn an ask policy into automatic execution.

## 2. Technical Spike Questions

The Planning recommendation is specified below and in
`PADR-separate-shared-configuration-from-local-execution-and-rendering`. Repository evidence and alternatives
are in `materials/configuration-evidence.md`. Acceptance remains a user decision.

- **Q1: Effective configuration.** A core accessor validates a restricted overlay; governance remains shared.
- **Q2: Worktree semantics.** Copy the source local file before setup and first sync; each worktree then owns
  its independent configuration snapshot.
- **Q3: Rendered artifacts and receipts.** Shared inventory stays reproducible; an ignored local render ledger
  covers only approved human-readable asset kinds and their ignored projections.
- **Q4: Environment controls.** `sync --cloud` and `sync --local` persist only after successful sync. Ordinary
  sync preserves the saved choice; planning modes are read-only. Environment is read from the explicitly bound execution workspace.

## 3. Proposed Design & Impact

### Configuration schema and readers

`devkit-dist` owns both schemas, following `ADR-dist-config-receipt-ownership` and
`ADR-dist-foundation-ownership`. Add core APIs `read_effective_config(root)` and
`resolve_execution_environment(root)`. Core owns parsing, overlay eligibility and
source provenance without importing distribution or harness. Existing `read_project_config(root)` remains
explicitly shared-only for policy readers and snapshots. Distribution's runtime readers move to the new accessor;
shared inventory planning uses the shared accessor explicitly. Do not silently reinterpret a raw shared read as
an effective-policy read.

Local schema is an optional `schema = 1` and only `[execution] environment = "local" | "cloud"`,
`[mcp] register = true | false`, `[playbooks]` search settings, and `[bundles.<bundle>.variables]` scalar
template inputs. The shared schema gains `execution` and `mcp` too; registration defaults true, with its actual
registration reconciliation owned by `PROP-standalone-devkit-mcp`. Other local keys, including `agents`, `presets`, `guidance_block`, `override_drift`, `rules`,
`workflow`, `gates`, `worktree`, `integration`, and `tool`, fail with `CONFIG_LOCAL_KEY_FORBIDDEN` (exit 2).
A local overlay cannot disable a rule, alter a gate, change integration policy or replace a command.
Malformed TOML, wrong types, unsupported schema, symlinks and nonregular config files fail as `CONFIG_INVALID`
(exit 2) with the actual source path. Every present local file is validated even when a particular consumer does not use its values.
Unknown bundle inputs are validated when the bundle is selected, as today.

Merge order is manifest/defaults, the current project's shared config, then its local config. Merge tables recursively; scalars and arrays replace whole values; type mismatches fail
validation instead of coercion. Current permitted local settings have no array-valued fields; the generic merge
rule does not authorize an otherwise forbidden array. Missing local files mean no preference override.
`execution.environment` follows the same replacement rule and defaults to `local`.

Expose `devkit config show --effective [--format json]`: one result identifying effective configuration and
per-key source paths, including the effective execution environment. It is read-only;
TOML content is not a secret store. Existing `add`, `remove`, selection flags and `config template` write shared
config only; no general local setters or local template expansion are added. Users edit local preferences directly;
`sync --cloud|--local` are the only new local-writing commands. Runtime readers validate local config, including
ordinary sync and `get-context`; governance readers keep using shared config.

### Execution environment and worktrees

`devkit worktree start` copies the source project's `.devkit/config.local.toml` to the corresponding project
path in a newly created worktree after Git checkout and before setup or the first locked sync. Copy the complete
validated file with its file mode; never copy symlinks. Source is the explicit start caller's project in the retained
base checkout: current `start` refuses nested worktree creation, and this feature retains that refusal. Missing
source means no destination file and default/shared resolution. A malformed source fails before creating the
worktree. Failure while copying leaves the created worktree with an actionable recovery error and runs no setup or
sync. Once created, the files are independent: edits/deletion in one do not propagate to another.

Attach/resume of an existing worktree preserves its existing local file byte-for-byte, including an intentional
absence. It never overwrites or repopulates from the current base snapshot. A copy failure reports the exact source
and destination and instructs a deliberate manual copy before retrying setup; recovery never guesses whether an
absent existing file was intentional. Direct `git worktree add` and independent clones do not copy local config;
the caller must provision it explicitly. There is no promise of cloud inheritance outside `devkit worktree start`.
The existing local CLI is the copy owner; no new worktree command, registry or ongoing synchronization is needed.

The core resolver reads only its explicit project root and returns `local|cloud` plus the selecting source. Root
binding is separate from an absent local file: a valid bound project without local config uses shared/default values;
a missing or invalid bound project is an error. Cloud means interactive approval is unavailable, never that an ask
policy becomes auto. Local does not prove host interactivity. There is no process-wide environment variable or
cloud latch in this design.

A retained-base MCP server binds its owning configuration workspace separately from the interpreter/runtime root
and integration base. It rereads that workspace before approval and before mutation/resume. The tool caller cannot
choose an environment argument. A local Host may approve integrating a source branch produced in cloud; source
provenance is not the execution environment. `PROP-standalone-devkit-mcp` owns binding, registration, host-capability
checks and approval enforcement, and consumes the resolver rather than parsing TOML itself.

`devkit sync --cloud` and `devkit sync --local` are mutually exclusive; they stage the respective value in the
current checkout's local file and override a shared environment value by ordinary precedence. Ordinary sync retains
existing values. Explicit return to local is `devkit sync --local`. This is an environment selection, never an
approval-policy change or a claim of sandbox enforcement. A missing/deleted local file resolves according to shared
config/defaults; host capabilities still independently determine whether interaction is possible.

### Transactions, ignore management and read-only modes

Sync holds the existing project lock and plans the selected environment in memory. On a writing sync, local
config, local ledger, generated outputs and shared changes commit through the existing journal together. Any
pre-commit planning or transaction failure leaves the prior saved environment and files intact. Post-sync extension
warnings retain the committed environment, matching the existing transaction boundary. The sync invocation plans against its requested effective environment; a failed invocation reports failure and
does not silently retry with a different environment.

`--dry-run` and `--check` plan the selected value without persistence, lock-state changes aside, and include the
pending local-config change in their result. `--check` exits 1 if that change or any ordinary sync change is needed.
`--no-save` suppresses both shared selection persistence and environment persistence. `--locked` may save an ignored
local choice and rebuild eligible ignored output if the shared receipt and every tracked destination remain fixed;
otherwise `RECEIPT_STALE` writes nothing. CLI arguments never silently rewrite shared `execution`.

A writing sync manages exactly `/config.local.toml` in `.devkit/.gitignore`, appending it when absent and preserving
all unrelated lines. The existing managed/transient seeding contract otherwise stays intact. Refuse a tracked local
file or a tracked local output, or an effective negation that leaves either unignored, with
`CONFIG_LOCAL_NOT_IGNORED` (exit 2) before applying the transaction. Diagnose with source paths and the exact ignore
or index action the user must take; never alter the Git index. Check/dry-run report the proposed ignore edit;
locked sync refuses it as a tracked change. Tests cover an existing custom ignore file and a later negation.

### Personal rendering without shared drift

Plan a canonical shared inventory from shared configuration only. `.devkit/installation.json`, guidance blocks,
seeded files and their hashes continue to describe those bytes. Build a second in-memory inventory with effective
variables and compare it to the canonical inventory. A local change may alter bytes only in assets of kind `skill`,
`instruction`, `subagent`, or `playbook`, and only at ignored, untracked managed/native destinations. Changing asset
selection, file paths/modes, bundle manifests, constitutions, rule/workflow/gate content, hooks, guidance or seeded
files through local variables fails `CONFIG_LOCAL_RENDER_FORBIDDEN` (exit 2) before any write. A bundle variable
that also changes guidance therefore cannot be set locally until its author separates that shared use.

Write the differing content to the normal ignored asset destinations and record only changed hashes in
`.devkit/transient/local-render.json`, bound to the canonical receipt digest and effective variable digest. The
existing deployed ledger continues recording actual disk bytes for conflict detection. Distribution runtime
reading/status/context validates the canonical receipt plus this local ledger; the core canonical receipt loader,
rule discovery, workflow/gate engines and snapshot checks keep the shared receipt contract. Missing/stale ledger or
changed effective variables yields `CONFIG_LOCAL_RENDER_STALE` (exit 1, run sync) rather than falling back to
unverified local bytes. Missing local-render outputs use the normal sync repair path. Hand edits still conflict.
Local preferences removed by an ordinary sync restore canonical bytes and remove obsolete ledger entries.

Before writes, capture shared/local inputs and recheck their digests; if they changed during planning, return
`CONFIG_LOCAL_CHANGED` (exit 1, rerun) with no writes. Reads validate their chosen snapshot under the project read
lock; a later mutation rereads it. No cache of local files may permanently mask an environment change.

The response-style language template currently changes the skill only, so
`[bundles.response-style.variables] language = "ko"` is the first acceptance fixture. No template source change
or special response-style setting is necessary. Projects tracking native projections must first ignore/untrack the
affected projections themselves; this feature refuses to create personal tracked changes.

### Acceptance evidence and delivery boundaries

- **AC1:** An absent local file preserves current preferences and canonical bytes. Invalid local files
  and forbidden governance keys fail with the specified codes and paths, including settings unused by the immediate reader. Tests exercise recursive merge, whole-array replacement in the merge utility and field validation.
- **AC2:** A personal language override updates ignored skill output and its local ledger; shared config, canonical
  receipt and root guidance are byte-identical. Locked sync succeeds when the ignore entry already exists. An
  affected tracked projection, rule template or guidance template refuses before writes.
- **AC3:** Shared config writers preserve local bytes. `--cloud`, `--local`, `--no-save`, ordinary sync, check,
  dry-run, locked refusal, failed transaction and post-sync warning follow the persistence matrix above. Existing
  `.devkit/.gitignore` comments/rules survive; negated ignores and tracked local files refuse.
- **AC4:** Worktree fixtures cover copying before setup/sync, exact bytes/mode, missing/invalid source, partial
  copy failure, existing destination preservation, intentionally missing destination on attach, linked-caller refusal,
  nested project paths and independent changes after creation. Direct Git worktrees receive no automatic copy.
  Explicit resolver roots cover a retained-base server bound to a task checkout and a missing bound root.
- **AC5:** Context/status reject stale local render evidence, detect edited files and recover through sync. Removing
  the preference restores shared bytes. Snapshot rule checks produce the same result with/without personal language;
  executable asset kinds cannot be personalized. Distribution-only installation remains functional.
- **AC6:** A local file changed while planning aborts with no writes. Runtime configuration inspection identifies
  the effective value and selecting source; local environment alone conveys no approval authority.

Implementation adds the core resolver/accessors, distribution local validation/readers/writers and render ledger,
worktree copying, and focused tests. Relevant existing parents are declared in `boundaries`; new core modules,
ledger tests and docs may be created there. Update `CAP-DIST-sync-and-transactions`,
`CAP-DIST-workspace-ownership`, `CAP-WT-task-worktrees`, `ARCH-05-4-distribution-components`, the distribution
reference and consumer guidance. Verify lint/type checks, `just test-affected`, distribution-only tests where core
imports change, and the targeted snapshot regression. Development remains medium: reversible local work with a
mandatory independent code review and reconcile check; no released external API is being migrated.

Scope excluded: MCP extraction/registration/approval enforcement; shared worker storage; host trust or sandbox
changes; arbitrary local governance overrides; secrets management; local bundle selection; personalized tracked
artifacts; a generalized runtime settings plugin mechanism. `PROP-standalone-devkit-mcp` owns approval enforcement
using this configuration. Its independent extraction can proceed in parallel; environment-dependent behavior waits
for this contract's implementation and shared integration tests.

## 4. Lifecycle & Retirement Criteria

Remain reviewing until the user decides `plan-accept`. The recommendation becomes a Development input only after
acceptance and explicit handoff. No environment or approval policy is changed during Planning. The local resolver
and shared/local rendering boundary must be implemented before the dependent MCP environment behavior is declared
complete. Planning's artifact checks are not implementation verification.
