---
id: PLAN-deterministic-milestone-completion
spec: SPEC-deterministic-milestone-completion
---

# Technical Plan: `SPEC-deterministic-milestone-completion`

## Constitution & Invariant Review

`ADR-milestone-closure-confirmations` supersedes only the closure review of `ADR-separate-unit-prerequisites-from-milestone-themes`, retaining its unit ordering, direct PROP membership and inherited transition/history policy. No runtime API or schema changes.

## Components and Design

Update the milestone template, Backlog reference, spec-next orientation and seeded roadmap README. Keep the detailed close procedure in a dedicated reference linked from Backlog to respect its existing context budget. Two plain body assertions are durable decisions, not parsed fields. Reset them before authorized membership mutations, coordinating through the Host when the milestone is out of scope. Update the three affected capability contracts and repository roadmap README during reconciliation.

The accepted simple model requires focused current evidence, not exhaustive historical branch enumeration. Keep existing done records unchanged. Missing evidence leaves the milestone open; unchanged approved evidence remains authorized after interruption. No dependencies are added.

## Verification

Add local/cloud guidance contract fixtures for AC-01 through AC-06 without implementing a semantic evaluator. Run relevant lint/type checks, just test-affected (preserving its full fallback), bundle budget checks and cumulative governance rules. Independent medium code and reconcile reviews verify instructions against requirements and the final diff.
