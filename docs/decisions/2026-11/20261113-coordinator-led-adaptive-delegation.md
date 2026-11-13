---
id: ADR-coordinator-led-adaptive-delegation
title: Coordinator-led delegation without fixed child depth or budget
summary: "For adaptive development, we make the coordinator actively delegate useful work and remove fixed nesting and child-budget rules, retaining assignment authority checks."
status: accepted
created_at: 2026-11-13
spec: SPEC-adaptive-orchestration
supersedes: [ADR-skill-local-swarm-roles]
---

# [ADR-coordinator-led-adaptive-delegation] Coordinator-led delegation without fixed child depth or budget

## 1. Context & Problem Statement

Conditional delegation wording leaves the coordinator's responsibility unclear. A fixed two-level topology and
child-budget handoff duplicate execution restrictions while the assignment recorder rejects otherwise valid descendants.

## 2. Decision Drivers

- Keep the main agent focused on decomposition, coordination, integration and validation.
- Actively use subagents for useful separable work without per-dispatch user selection.
- Remove additional depth/budget restrictions without replacing them with generic host-configuration advice.
- Preserve scoped authority, ownership and verified completion.

## 3. Considered Options

- Clarify delegation while retaining the depth cap: resolves only the wording issue.
- Clarify delegation and remove the extra depth/budget rules: meets the requested policy with unchanged authority checks.

## 4. Decision Outcome

- The coordinator actively delegates useful separable work and owns integration and final validation.
  → `CAP-DLV-adaptive-development` rule 12 (SHOULD).
- Fixed nesting depth and child-budget requirements are removed from entry guidance, role payloads and swarm contracts.
  → `CAP-DLV-adaptive-development` rule 13 (MUST).
- Assignment recording permits deeper parent chains and excludes their ancestors from overlap checks, preserving
  immediate-parent scope/commit narrowing and child completion checks.
  → `CAP-DLV-adaptive-assignments` rules 4 and 5 (MUST).

Supersedes in part `ADR-skill-local-swarm-roles`: the fixed nesting-depth and Host-assigned child-budget clauses only.

## 5. Consequences

The coordinator chooses useful work distribution without a fixed team shape. Deeper assignments retain transitive
scope/commit boundaries. This changes neither host configuration nor execution permissions.

## 6. Confirmation

Adaptive bundle projection checks and assignment integration tests cover guidance and deeper chains. Actual model
orchestration quality requires usage evidence.
