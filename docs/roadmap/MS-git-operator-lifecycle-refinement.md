---
id: MS-git-operator-lifecycle-refinement
title: Git-operator lifecycle refinement
summary: "Lowers the Host's interpretation load and lightens merging at the boundary between Host decisions, guarded lifecycle execution and worker input, while git-operator keeps its narrow role."
status: planned
created_at: 2026-10-30
depends_on: []
---

# [MS-git-operator-lifecycle-refinement] Git-operator lifecycle refinement

## Goal

Advances `ARCH-01-introduction-and-goals` §1.3 (Delivery Workflow Orchestration) from the resource-indexer consumer
pilot (`MAT-git-operator-consumer-pilot`) and this repository's own local-orchestrated runs. Lifecycle results,
acceptance routes, worker audit baselines, scope evidence and batch preparation become explicit, and a
conflict-free moved target no longer forces a manual merge-and-recheck cycle.

## Exit condition

- Every child proposal of this theme is completed or dropped.
- No completion report claims a token, cost or latency improvement without a measurement.

## Non-goals

- **Scope Excluded**: a daemon, persistent approval store, global repository lock or autonomous scheduler.
- **Scope Excluded**: operator source authoring, semantic decisions, approval grants, force operations or arbitrary
  remote deletion.
- **Scope Excluded**: new model routing, universal native-host guarantees or unmeasured token, cost or latency savings.

## Completion review

Decomposition: pending
Direct proposal work: pending

Confirm both with the current Backlog close candidate; record confirmed and status done together after the user's
confirmation. Missing assertions mean unconfirmed. Actual semantic scope changes reset both to pending; normal handoff does not.
