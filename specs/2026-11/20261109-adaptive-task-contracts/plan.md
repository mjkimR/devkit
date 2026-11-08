---
id: PLAN-adaptive-task-contracts
spec: SPEC-adaptive-task-contracts
---

# Technical Plan: `SPEC-adaptive-task-contracts`

## 1. Constitution & Invariant Review

No architectural invariant changes. Existing caller authority and isolated-writer boundaries remain in force.
No feature dependency edge is introduced.

## 2. Architecture Overview & Impact

Extend the adaptive bundle's delegation and orchestration references and four role overlays. The swarm planner
retains read-only authority while describing dependencies. Update `CAP-DLV-adaptive-development` and
`UC-advance-an-idea` with retained behavior. No runtime API or storage changes.

## 6. Verification & Test Plan

Review three concrete assignment fixtures and all four overlays against AC-01 through AC-04. Check installed
consumer assets and run catalog integration packaging/projection tests for AC-05. Run `just lint-check`,
`just check`, `just rules-check` and `just test-affected`; report live agent execution as unverified.
