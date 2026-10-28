---
id: SPEC-mcp-runtime-pending
title: Remove speculative MCP registration notices from general status
summary: Remove MCP_REGISTRATION_PENDING from general devkit status while preserving diagnostics from actual registration plans, including locked sync's notice for a concrete registration write it withheld.
status: planned
created: 2026-10-28
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-mcp-runtime-pending] Remove speculative MCP registration notices from general status

## 1. Problem Statement & Motivation

Handed off from proposal PROP-mcp-runtime-pending on 2026-10-28.
- **Preserved Materials**: `docs/materials/2026-10/20261028-mcp-runtime-pending`

### 1. Background & Hypothesis

General `devkit status` infers `MCP_REGISTRATION_PENDING` from provider entry-point presence and missing local
ownership. It does not load the provider, so it cannot distinguish actionable registration from unavailable runtime
or a provider that returns `None`. The latter occurs for a read-only profile with no exposed tools.
`FB-mcp-registration-pending-ignores-runtime` records the resulting unhelpful retry advice.

The user settled the direction: remove this speculative notice from general status entirely. Runtime availability
and actual registration planning remain the responsibility of explicit MCP and sync commands. The existing
provider-free status boundary stays intact. `ADR-remove-speculative-mcp-status-notice` records this narrow contract
simplification; `docs/materials/2026-10/20261028-mcp-runtime-pending/status-removal-evidence.md` identifies the affected seams.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Remove speculative MCP registration notices from general status so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

The direction has no unresolved questions. General status will not add an active-only check, runtime load/probe,
cache, TTL, fingerprint, persistence schema or replacement notice. Low Planning effort applies to this turn because
the user explicitly selected the complete bounded direction. Earlier support-role envelopes remain history of the
withdrawn observation design; they do not require that design to be implemented.

### 3. Proposed Design & Impact

Remove the general-status import and call of `registration_pending_notices`, and its associated notice assembly.
General status MUST NOT emit `MCP_REGISTRATION_PENDING`, regardless of receipt presence, optional package presence,
provider result or actual registration absence. It MUST NOT load a registration provider, invoke a runtime probe or
write registration state. Keep its other core, host-hook and gate-health diagnostics on their existing paths.
Removing this MCP-specific check also removes its ledger/destination inspection from general status; explicit
registration commands retain their validation and errors.

Remove `registration_pending_notices` and `unregistered_hosts` if their remaining callers are only the obsolete
status path and its tests. Preserve `_registration_pending` and `McpRegistrationPendingNotice`: locked sync uses
them after an actual provider plan has produced a host state of `write`. That concrete withheld-write notice and
its `uv run devkit sync --registrations-only` fix remain. Preserve `MCP_REGISTRATION_UNRECONCILED` and other existing
registration warnings/errors. Do not change registration planning, provider failure handling, explicit `mcp status`
or `mcp setup` behavior.

#### Development acceptance scenarios

- **AC-1**: Given a synchronized checkout with an absent project registration, when general status runs with (a)
  no optional provider installed, (b) an installed provider that would return `None`, (c) an installed provider that
  would raise `MCP_RUNTIME_UNAVAILABLE`, or (d) a provider that would plan a real missing registration, then its
  result contains no `MCP_REGISTRATION_PENDING`. Repeat the no-receipt case. Assert no provider load, runtime probe
  or registration write occurs, rather than merely asserting notice absence.
- **AC-2**: Given those four provider scenarios, when the existing registration planning/registrations-only path
  runs explicitly, then its real result is preserved: no-provider no-op, `None` with no desired registration,
  runtime-unavailable warning, or a concrete registration plan/action respectively. Existing explicit `mcp status`
  and `mcp setup` result, refusal and provider-failure tests remain valid when the runtime package is installed.
  Use fake providers and isolated repository fixtures; no real runtime installation or host-file mutation is needed.
- **AC-3**: Given a fresh checkout whose actual provider plan has a desired host state of `write`, when locked sync
  leaves that registration unwritten, then it still returns `MCP_REGISTRATION_PENDING` with its existing fix and
  writes no host entry. Given absent provider, `None` or runtime-unavailable instead, then it preserves the actual
  plan's no-op or warning and does not invent a withheld-write pending notice. Existing reconciliation refusals
  for changed registrations remain intact.
- **AC-4**: Given existing independent core, host-hook or gate-health findings, when general status runs, then those
  findings retain their existing reporting and exit semantics. No replacement MCP readiness or active-only check
  is introduced, and registration state is not consulted through a substitute path.
- **AC-5**: The MCP capability, distribution capability and distribution quick reference consistently state that
  general status omits speculative registration notices, explicit registration commands diagnose actual state, and
  locked sync retains its concrete withheld-write notice. No cache, TTL, fingerprint or observation-file contract
  is introduced.

Extend or replace the existing host onboarding and distribution reporting/output contract tests for this matrix.
Retain relevant provider-failure and locked-sync regressions. Run lint/type checks, `just test-affected` and
`just test-dist` in Development. This Planning turn changes proposal documents only and runs document/envelope
validation rather than executable implementation tests.

#### Living Spec targets and scope

Update `CAP-MCP-runtime-registration` to remove the provider-metadata pending check and distinguish general status
from explicit `mcp status`. Update `CAP-DIST-sync-and-transactions` to retain locked sync's actual-plan notice while
removing its general-status counterpart. Update the distribution quick reference's notice table and status prose.
The tiny PADR is the only decision to promote at handoff.

`size: S` and `task_kind: feature` reflect an agreed contract simplification within dist's existing status and
registration boundaries. Retain `dev_effort: medium` for the externally visible notification removal, preservation
matrix and documentation reconciliation. No runtime-provider code, registration storage format or general status
refactor is included.

### 4. Lifecycle & Retirement Criteria

The Host can present this committed direction for `plan-accept`; this worker performs neither acceptance nor
handoff. Development retires the proposal after AC-1 through AC-5 pass and the named Living Spec targets agree.

### 5. Planning Decisions

- Apply the user's settled direction: remove speculative MCP pending from general status; preserve real registration
  planning diagnostics and locked sync's concrete withheld-write notice.
- Withdraw the bounded runtime-observation PADR because no observation mechanism remains. Its file is deleted and
  no reference to it remains in the current proposal. Earlier envelopes remain immutable Planning history.
- Replace the observation comparison material with focused removal evidence. Add the distribution capability to
  Development's exact documentation scope because it currently promises the general-status notice.
- No new business questions remain. Acceptance and handoff are separate Host actions.

### Source feedback

`FB-mcp-registration-pending-ignores-runtime` remains the promoted source. This proposal owns its recorded behavior;
Planning does not claim the behavior fixed and does not edit the source feedback.

