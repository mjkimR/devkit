---
id: PROP-mcp-runtime-pending
title: Report MCP registration pending only when runtime state warrants it
summary: "Suppress repeated MCP registration pending notices after a recent runtime-unavailable registration attempt, using an ignored advisory observation with input invalidation and a 300-second lifetime while status remains provider-free."
status: reviewing
created_at: 2026-10-28
target_area: capabilities/mcp/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/features/host/
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - packages/devkit-dist/tests/integration/features/host/
    - packages/devkit-dist/tests/integration/features/distribution/
    - docs/capabilities/mcp/
    - docs/development/reference/distribution.md
  excludes:
    - packages/devkit-mcp/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-mcp-runtime-pending] Report MCP registration pending only when runtime state warrants it

## 1. Background & Hypothesis

`status` emits `MCP_REGISTRATION_PENDING` for an eligible missing project registration even when the proposed fix,
`uv run devkit sync --registrations-only`, reports `MCP_RUNTIME_UNAVAILABLE`. The pending check deliberately reads
provider entry-point metadata without loading the provider. `CAP-MCP-runtime-registration` and
`ADR-mcp-runtime-and-shared-artifacts` keep runtime selection in the optional provider.

A recent negative registration observation can suppress this unhelpful retry without making status select a
runtime. The observation cannot prove current runtime availability. It therefore needs both input invalidation
and a hard expiry. `PADR-bounded-runtime-unavailable-observation` selects the bounded compromise.

## 2. Technical Spike Questions

- **Q1, settled**: Can status establish runtime availability without loading the provider? No. Candidate probes,
  service versions, imported paths and linked-worktree rejection belong to the provider. A dist-only filesystem
  fingerprint is incomplete. The evidence and alternatives are in `materials/runtime-observation-options.md`.
- **Q2, settled**: What invalidates a negative observation? A changed observation key, unreadable key inputs,
  malformed observation, a future timestamp or age of at least 300 seconds invalidates it. A completed normal
  registration attempt always re-probes and replaces or clears the observation.
- **Q3, settled**: Does runtime installation restore pending immediately? Observable key changes do. Repairs that
  leave the key unchanged restore pending on the first status at least 300 seconds after the observation. This
  maximum stale window is part of the proposed behavior, not a claim of immediate runtime detection.

## 3. Proposed Design & Impact

### Advisory observation

Add a dist-owned, optional ignored file at `.devkit/transient/mcp/runtime-observation.json`. It records only the
last completed default-selection registration attempt that reported `MCP_RUNTIME_UNAVAILABLE`: schema version,
normalized workspace identity, observation-key digest, observed UTC time and the fixed outcome
`runtime-unavailable`. Do not store host entries, environment values, probe stdout or ownership claims there.
Keep the strict ownership ledger and its schema unchanged.

The observation is advisory input only. Status and locked/dry-run/check operations MUST NOT write or renew it.
They MUST NOT import `devkit_mcp`, load the registration provider, invoke a candidate interpreter or launch a host
because of this feature. A missing, expired, invalid, unreadable, tracked, unignored, symlink or nonregular
observation is a cache miss.
A malformed ownership ledger retains its existing error. Host-destination errors on the existing validation paths
retain their behavior; the observation MUST NOT mask them. With no ownership record, the existing pending check
does not parse a destination, and this feature does not expand that validation contract.

Only ordinary nonlocked sync and registrations-only sync opt into creating negative observations. Keep `plan`
read-only: carry the attempt outcome and observation context in `RegistrationPlan`, then process observation
intent in dist's apply path even when registration `changes` is empty. The unavailable-runtime/empty-ledger case
MUST persist without requiring any host-file or ledger change. Do not put the only cache writer behind the
existing no-changes early return. Observation handling is separate from the host transaction branch; locked mode
skips all observation writes, including clearing.

Create reusable negatives only for default executable selection, the effective persisted environment and the
configured host selection. A temporary environment or host selection used by ordinary sync MUST NOT create a
reusable negative. A completed overridden attempt clears a previous observation instead. Registrations-only sync
uses its default persisted configuration. Runtime setup/remove retain their existing calls into dist apply:
successful completion may clear a previous observation, but cannot create a negative. Setup's runtime-unavailable
refusal stays before every write. A default-successful attempt clears the observation when no runtime-unavailable
outcome remains, including provider absence, opt-out and cloud profiles with no exposed tools. A failed or refused
attempt does not create or renew it. Registration attempts always invoke normal planning; the cache never skips
probes. No excluded `devkit-mcp` caller change is needed.

Persist with safe atomic replacement under the existing clone-then-project locks and lifecycle guards. Check the
cache's parent path safety and require an untracked, ignored destination before any write or removal. If the
destination exists, require a regular file; otherwise require safe absence. Do not follow symlinks or install an ignore rule for this advisory file. Reading an
unusable observation or failing to create one falls back to ordinary pending behavior and a diagnostic log,
without changing the registration result. A failed replacement leaves no fresh observation: any prior readable
record can remain usable only until its original expiry. A failed clear likewise can leave the previous negative
usable until its original expiry; it MUST NOT renew its timestamp. Successful clear restores the baseline check.
The observation is outside the ownership journal: a partial cache write is a cache miss and cannot authorize
recovery or host-file mutation. Size is bounded at 64 KiB and the schema rejects unknown fields. No TTL setting or
new public CLI surface is introduced.

### Observation key and bounded validity

Compute the same key before and after the provider attempt. Persist a negative only when both keys match.
Recompute the key from current trusted inputs rather than following any path supplied by the observation:

- Normalized workspace path, common Git directory identity (path, device and inode), workspace directory identity
  and the ordered registered worktree paths, including retained executor identity. Refuse cache reuse when these
  identities cannot be read consistently.
- Shared and local configuration file bytes, including absence, plus the normalized configured host selection and
  effective `mcp.register` and execution environment. Any configuration-byte change invalidates the observation.
- Sorted installed registration-provider and host-service entry-point metadata: name, value, distribution name and
  version. Include the running dist version; a missing required metadata field disables cache reuse.
- The running interpreter and retained executor's default `.venv/bin/python` paths: existence, symlink target,
  resolved path and device/inode/mode/size/mtime/ctime tuple (excluding access time), plus
  `sys.prefix/pyvenv.cfg` and the retained executor's `.venv/pyvenv.cfg` bytes where present. These are early
  invalidation signals, not a reimplementation of runtime selection or a complete dependency fingerprint.

A usable observation has `0 <= now - observed_at < 300 seconds` and an equal key. Future timestamps, nonfinite
values, unsupported schemas and changed/unreadable inputs are cache misses. Reads never slide the expiry.
Candidate creation/replacement and configuration changes invalidate on the next status. A package/import repair
that changes none of these signals can be hidden for the remaining lifetime, at most 300 seconds under the
system clock. No recursive environment scan or interpreter probe is added to status.

### Pending selection and output

Run the existing provider-present, register-enabled, destination-eligibility and ownership validation first.
Filter the resulting missing eligible hosts only when a valid negative observation matches their configured
registration context. Preserve the existing aggregate `MCP_REGISTRATION_PENDING` notice and its fix when no valid
negative applies. Do not invent a current `MCP_RUNTIME_UNAVAILABLE` result from historical evidence. The registration
attempt continues to return its existing runtime-unavailable warning; status emits no replacement warning during
the valid observation window. Status output fields and exit codes stay unchanged.

### Verification scenarios for Development

- **AC-1**: Given an installed provider and eligible missing configured registration with no observation, when
  status runs, then it emits `MCP_REGISTRATION_PENDING` with the existing registrations-only fix and never loads
  the provider. Existing fresh-checkout behavior remains covered.
- **AC-2**: Given a completed default registration attempt reports `MCP_RUNTIME_UNAVAILABLE`, when status repeats
  with the same key at ages 0 and 299 seconds, then pending is absent and neither status nor cache reads change
  any file. Registration still returns the runtime warning.
- **AC-3**: Given that observation, when status runs at age 300 seconds, with a future timestamp, changed shared or
  local configuration, host selection, provider/service metadata, worktree identity, or default interpreter
  creation/replacement, then the observation is ignored and pending returns for still-eligible missing hosts.
- **AC-4**: Given a runtime repair that leaves the key unchanged, when the clock reaches expiry, then pending
  returns; when registration is explicitly retried before expiry, then the provider is probed and a successful
  result clears the observation. No observation can prevent a registration attempt.
- **AC-5**: Given dry-run, check, locked restoration, runtime setup/remove, temporary host/environment overrides,
  provider failure or lifecycle refusal, when the route runs, then it creates or renews no reusable negative
  observation. Completed mutating setup/remove and overridden attempts clear an existing one; read-only and locked
  routes do not. An unavailable setup still refuses before any write. An ordinary or registrations-only sync
  with no host/ledger changes still persists a completed default negative. Cache writes cannot alter assets,
  receipt, host entries or exclusions beyond their pre-existing registration behavior.
- **AC-6**: Given absent, malformed, oversized, symlink, nonregular, tracked, unignored or unreadable optional
  observation, when status or a registration route uses it, then the cache falls back without changing registration
  results. A malformed ownership ledger and malformed owned host destination still raise their existing errors
  even with a valid negative; an unowned malformed destination retains the existing pending-check behavior.
  Given a readable unexpired observation whose directory becomes nonwritable, when replacement or clearing fails,
  then the original timestamp stays unchanged and any suppression ends at the original expiry.
- **AC-7**: Given opt-out, removed provider, an already matching registration, a tracked/visible destination or an
  unsupported host, when status runs, then current eligibility behavior remains intact and the cache grants no
  ownership. A partial/interrupted observation write cannot change the registration journal's recovery behavior.

Use fake clocks and fake provider outcomes; do not install a runtime or modify real host registration files in
verification. Extend the existing host onboarding and distribution reporting/output contract integration tests.
Run lint/type checks, `just test-affected`, and `just test-dist` in Development to retain dist-only support.
These scenarios specify observable behavior; they do not claim timing or operation-count improvement.

### Living Spec targets and boundaries

Update `CAP-MCP-runtime-registration` with historical-observation semantics, invalidation and the 300-second
stale bound. Keep its provider-free and runtime-selection ownership contracts. Update the distribution quick
reference's pending-notice explanation. Promote the PADR at handoff through the existing workflow.

Development is confined to the declared host/distribution code, their existing integration test parents and the
named MCP contract/reference. No runtime-provider code or general plugin policy changes are required. The design
retains `dev_effort: medium`: one package's bounded status/registration behavior, with focused cache and integration
coverage and independent review.

## 4. Lifecycle & Retirement Criteria

Planning is ready for the Host's direction decision once the options, support envelopes, folded findings and
proposal checks are committed. Acceptance and handoff belong to the Host. No implementation is authorized here.

Development retires this proposal after the handoff spec satisfies AC-1 through AC-7 and reconciles the named
Living Spec targets. Strict immediate detection of every runtime repair is excluded from this direction; adopting
it would require reopening the provider observation contract rather than claiming a complete dist fingerprint.

## 5. Planning Decisions

- Recommend a 300-second maximum negative observation with early input invalidation; keep runtime validation in
  the provider. `PADR-bounded-runtime-unavailable-observation` records alternatives and consequences.
- Use a separate expendable advisory file rather than adding negative ownership entries to the ledger.
- Preserve unknown first-run availability: a fresh checkout still reports pending until a registration attempt
  supplies evidence. The runtime warning is not replayed as a current status fact.
- Challenger P2 findings were folded: explicit no-op writer modes and setup refusal, unchanged host-validation
  scope, and failed-clear expiry semantics. `envelopes/reverify-01.yaml` records self-verification.
- No unresolved business questions remain; the Host's `plan-accept` decides this bounded direction.

## Source feedback

`FB-mcp-registration-pending-ignores-runtime` is the promoted source. This proposal owns its recorded behavior;
Planning does not mark the observation fixed and does not modify the source feedback.
