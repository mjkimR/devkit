---
id: SPEC-local-orch-resource-manager
title: Reusable git-operator subagent for local orchestration
summary: Delegates lifecycle operations to one reusable git-operator per Host conversation and repository to reduce main-agent intervention and context load. Uses the user-selected lean preset without transferring prior Sol evidence to Terra.
status: in-progress
created: 2026-10-30
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-local-orch-resource-manager] Reusable git-operator subagent for local orchestration

## 1. Problem Statement & Motivation

Handed off from proposal PROP-local-orch-resource-manager on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-local-orch-resource-manager`
- Target Docs Blueprint: `PROP-local-orch-resource-manager-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

Local orchestration delegates Planning and Development turns but leaves worktree preparation, handoff, integration
execution and cleanup in the Host. Their operating references and intermediate output compete with discussion
and coordination. `CAP-DLV-delivery-workflows` and `ADR-orchestration-workers` define that boundary.

Adopt one reusable `git-operator` per Host conversation and repository. Create it on first use
and reuse it for later jobs. Use native subagent execution/continuation, without an asynchronous runtime of our own.
The intended benefit is less Host operational context and intervention across multiple units. Total-cost and
conversation-latency improvements remain unmeasured.

## 2. User Stories

- **US-1**: As the Host, I delegate recurring lifecycle operations to one reusable git-operator while retaining
  decisions, scheduling and result acceptance.
- **US-2**: As the repository owner, I receive verified effects and exact blockers without losing approval scope
  or having the Host reconstruct routine CLI commands.

## 3. Non-Goals

**Scope Excluded**: A persistent service, custom async scheduler, durable approval/recovery store, global lock,
general Git repair, arbitrary branch deletion, production-source fixes and lifecycle CLI engine changes.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Reuse and context recovery

- **Given** sequential lifecycle jobs in one Host conversation and repository
- **When** the Host dispatches them in local-orchestrated mode
- **Then** it reuses the exact git-operator identity through native continuation; after missing identity or context
  loss it starts a fresh instance from current CLI/Git observations and repeats current per-job authority.

### [AC-02] Routine guarded execution

- **Given** a ready job with exact repository, base, worktree, Unit, refs, intended effects and current authority
- **When** git-operator executes the job
- **Then** it uses existing guarded CLI operations with exact arguments and returns identity, observed refs,
  completed_effects, remaining_effects, checks, stable blocker codes and original CLI status/exit/effects separately.
  Its role status is exactly completed, needs_input or failed. Completed requires every requested effect and check.

### [AC-03] Preserve scope and authority

- **Given** missing authority, changed scope/refs, dirty resources, active writers or denied host permission
- **When** git-operator refreshes the pre-mutation state
- **Then** it preserves resources and returns the exact blocker to the Host; it grants no approval/publication,
  authors no production fixes, resolves no semantic conflict and makes no user/business decision.

### [AC-04] Partial and unknown recovery

- **Given** partial or unknown CLI effects, including a zero-exit partial cleanup
- **When** git-operator handles the result
- **Then** it inspects live state before attempting only a verified supported remainder within current authority,
  preserves recovery identity and completed effects, and never returns completed while requested effects remain.
  Normal integration includes cleanup and dispatches no redundant cleanup job.

### [AC-05] Selected configuration and bounded evidence

- **Given** git-operator with source level lean and existing project overrides
- **When** bundle contracts and host projections are verified
- **Then** Claude Code maps to Sonnet medium, Codex to gpt-6.1-terra medium and Antigravity to Flash with effort
  omitted, without changes to distribution presets. Development records repeated-job evidence, exercised hosts,
  missing metrics and a matched same-head role-disabled Host-burden comparison. Replay and mutation evidence are
  labeled separately; earlier Luna/Sol results are not validation of Terra.

## 5. Assumptions and Current-base Check

The accepted proposal premises match this worktree's accepted head and current CLI contracts. Existing integration
already owns cleanup, and existing lean projections supply the selected mappings. The implementation uses role
messages rather than a new persisted schema. Activity-effort is medium because this changes an accepted agent
contract with reversible local assets. No product screen changes apply.

## 6. Preserved Planning Evidence

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Planning Findings

`MAT-resource-manager-planning-evidence` preserves the method, inputs, returned JSON and limits.

- **Q1 — Adoption benefit:** Existing guarded CLI operations provide a useful delegation unit. Two live read-only
  model probes returned correct state summaries from separate contexts. This demonstrates query/summary feasibility,
  not a measured multi-unit benefit. Development compares a matched sequence with the role disabled at the same
  head as baseline; a worker need not check out another commit.
- **Q2 — Model level:** Both requested configurations (Luna and Sol) passed 12/12 contract-driven decision cases.
  Sol supplied full commands in all three execute cases; Luna did so in one and used permitted natural-language
  actions in two. This is not a correctness failure or mutation-reliability comparison. One Luna follow-up failed
  without a diagnostic before a changed-input retry succeeded. Tokens, reliable latency and total cost were unavailable.
- **Q3 — Context boundary:** Keep dispatch, approval, scheduling, result acceptance and semantic decisions in the
  Host. Move operating steps, logs and routine recovery inspection to the manager. The role interface draft in
  this bundle specifies per-job identity/authority and concise actual-effect results.
- **Q4 — Reuse:** Reuse the exact agent identity within the conversation/repository. After context loss or missing
  identity, start a fresh instance from CLI/Git observations and current Host authority. Codex read-only invocation
  and follow-up were exercised; Claude and Antigravity live execution was not.

The user selected the role name `git-operator` and default `level: lean`, replacing the earlier provisional
standard recommendation in `ADR-reusable-lifecycle-resource-manager`. Existing project overrides remain available.
`ADR-lean-subagent-level` already defines lean: Claude Code Sonnet with medium effort, Codex `gpt-6.1-terra` with
medium effort, and Antigravity Flash with effort omitted because its supported per-role schema cannot express it.
Lean makes no Flash high-effort guarantee and adds no prompt-based effort emulation.

The prior probe compared requested Luna and Sol configurations; it did not test Terra medium. Its results remain
historical evidence, not validation of the selected model. The choice is explicit user direction, not a measured
Terra reliability or cost conclusion. No model router, fallback controller or distribution engine change is needed.

### 3. Proposed Design & Impact

#### Delegated execution

- Add a `git-operator` role with `level: lean` as the normal helper for recurring `local-orchestrated` lifecycle jobs.
  Preserve one-shot Planning/Development workers.
- Delegate worktree creation/attachment and setup, handoff execution, integration preparation and already-authorized
  execution, exact merged-resource cleanup and recovery inspection.
- Use complete existing CLI operations. Normal integration already includes cleanup; do not append a redundant
  cleanup job. `CAP-INT-mcp-services` retains readiness, digest, route and partial-result semantics.
- Source-authoring fixes, semantic reconciliation and conflict resolution remain with the implementer or Host.
  The manager reports required source preparation and invents no production edits to make readiness pass.
- The Host keeps user decisions, unit scheduling, worker result acceptance and semantic conflict decisions.
  It quiesces writers before cleanup. The manager serializes conflicting jobs within the conversation, without
  claiming repository-wide mutual exclusion.

#### Job and result boundary

Each job supplies operation, repository/base/worktree identity, Unit/branch, current relevant refs and exact
Host-carried authority for its effects. Include the prepared digest where required and separate publication
authority for remote effects. Read-only preparation needs no mutation authority.

Refresh state before mutation. Return completed and remaining effects, observed refs, checks and stable blocker
codes. Agent memory is procedural continuity, not Git truth or approval authority. Inspect unknown/partial outcomes
before attempting only a supported remaining operation. Changed scope, dirty resources, active writers, semantic
conflicts and permission/runtime blockers return to the Host. Preserve original CLI status, exit code and effects
separately from the role status. Use completed only after all requested effects and checks are verified complete;
needs_input means the remainder requires Host decision/action; failed means an execution failure. A zero-exit
partial cleanup is never completed until its requested cleanup effects are verified complete.

Update affected Host-only invocation clauses through `ADR-reusable-lifecycle-resource-manager`; retain unrelated
authority and worker decisions in `ADR-host-cli-lifecycle-authority` and `ADR-orchestration-workers`. Also supersede
the scout-only source-preset/default-inheritance clause of `ADR-five-subagent-levels` for this role, preserving
preset mappings and unrelated distribution policy. Caller
guidance keeps approval/coordination boundaries while operation-specific references move to the role.

#### Acceptance evidence

- **AC1 — Reuse:** Sequential jobs in one conversation/repository reuse the same manager identity; a missing
  identity rebuilds current state without reusing prior effect authority.
- **AC2 — Routine completion:** A ready, authorized job invokes existing CLI with exact arguments and returns
  observed effects without making the Host reconstruct commands or read raw logs.
- **AC3 — Scope preservation:** Changed refs/scope, dirty resources, active writers or missing authority preserve
  resources and return the exact blocker. The manager grants no approval or publication rights.
- **AC4 — Partial recovery:** Inspect partial/unknown state before executing only a verified remaining operation
  within current authority. Preserve recovery identity and completed effects. Include a zero-exit CLI partial
  cleanup result and verify that role status cannot claim completed while requested effects remain.
- **AC5 — Evidence:** Check role/projection contracts and repeated jobs; record exercised hosts and missing
  metrics; distinguish replay from mutation evidence. Compare Host burden at the same head with the role disabled.

#### Non-goals

**Scope Excluded:** A persistent service, custom async scheduler, durable approval/recovery store, global lock
service, general Git repair agent, arbitrary branch deletion, production-source fixes and lifecycle CLI engine
changes. A concrete missing CLI boundary discovered later is a scope problem, not permission to bypass a guard.

### 4. Lifecycle & Retirement Criteria

The accepted direction and Development handoff retain `dev_effort: medium`. Historical Planning evidence does
not establish selected-model mutation reliability.

Validate the selected lean configuration during Development without rerunning the historical probe as part of
this Planning revision. Terra medium execution, total cost and latency remain unmeasured; Sol evidence does not
transfer to Terra. No total-cost, mutation-reliability or latency superiority is claimed.
On acceptance, hand off to one feature spec; on rejection, retain the draft until normal hygiene retires it.

