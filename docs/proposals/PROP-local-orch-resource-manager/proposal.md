---
id: PROP-local-orch-resource-manager
title: Reusable git-operator subagent for local orchestration
summary: "Delegates lifecycle operations to one reusable git-operator per Host conversation and repository to reduce main-agent intervention and context load. Uses the user-selected lean preset without transferring prior Sol evidence to Terra."
status: accepted
created_at: 2026-10-29
target_area: delivery/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/
    - packages/devkit-spec/tests/integration/bundles/spec/
    - docs/capabilities/delivery/
    - docs/capabilities/integration/
    - docs/usecases/delivery/
    - docs/architecture/ARCH-04-1-ecosystem-boundaries.md
    - docs/steering/glossary.md
    - docs/decisions/
  excludes:
    - packages/devkit/src/devkit_agt/features/
    - packages/devkit-dist/src/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-local-orch-resource-manager] Reusable git-operator subagent for local orchestration

## 1. Background & Hypothesis

Local orchestration delegates Planning and Development turns but leaves worktree preparation, handoff, integration
execution and cleanup in the Host. Their operating references and intermediate output compete with discussion
and coordination. `CAP-DLV-delivery-workflows` and `ADR-orchestration-workers` define that boundary.

Adopt one reusable `git-operator` per Host conversation and repository. Create it on first use
and reuse it for later jobs. Use native subagent execution/continuation, without an asynchronous runtime of our own.
The intended benefit is less Host operational context and intervention across multiple units. Total-cost and
conversation-latency improvements remain unmeasured.

## 2. Planning Findings

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
standard recommendation in `PADR-reusable-lifecycle-resource-manager`. Existing project overrides remain available.
`ADR-lean-subagent-level` already defines lean: Claude Code Sonnet with medium effort, Codex `gpt-6.1-terra` with
medium effort, and Antigravity Flash with effort omitted because its supported per-role schema cannot express it.
Lean makes no Flash high-effort guarantee and adds no prompt-based effort emulation.

The prior probe compared requested Luna and Sol configurations; it did not test Terra medium. Its results remain
historical evidence, not validation of the selected model. The choice is explicit user direction, not a measured
Terra reliability or cost conclusion. No model router, fallback controller or distribution engine change is needed.

## 3. Proposed Design & Impact

### Delegated execution

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

### Job and result boundary

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

Update affected Host-only invocation clauses through `PADR-reusable-lifecycle-resource-manager`; retain unrelated
authority and worker decisions in `ADR-host-cli-lifecycle-authority` and `ADR-orchestration-workers`. Also supersede
the scout-only source-preset/default-inheritance clause of `ADR-five-subagent-levels` for this role, preserving
preset mappings and unrelated distribution policy. Caller
guidance keeps approval/coordination boundaries while operation-specific references move to the role.

### Acceptance evidence

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

### Non-goals

**Scope Excluded:** A persistent service, custom async scheduler, durable approval/recovery store, global lock
service, general Git repair agent, arbitrary branch deletion, production-source fixes and lifecycle CLI engine
changes. A concrete missing CLI boundary discovered later is a scope problem, not permission to bypass a guard.

## 4. Lifecycle & Retirement Criteria

Planning recommends adoption with `dev_effort: medium`. The role contract, ownership boundary and selected
model default are ready for `plan-accept`; acceptance and Development handoff remain Host/user decisions.
No production agent assets or lifecycle behavior changed in Planning.

Validate the selected lean configuration during Development without rerunning the historical probe as part of
this Planning revision. Terra medium execution, total cost and latency remain unmeasured; Sol evidence does not
transfer to Terra. No total-cost, mutation-reliability or latency superiority is claimed.
On acceptance, hand off to one feature spec; on rejection, retain the draft until normal hygiene retires it.
