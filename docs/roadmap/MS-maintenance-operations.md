---
id: MS-maintenance-operations
title: Repository maintenance operations
summary: "Makes recurring repository maintenance (drift reconciliation, weekly reporting, review and refactoring) runnable as opt-in playbooks, manually or from an external scheduler, with durable execution history kept apart from code history."
status: active
created_at: 2026-10-22
depends_on: []
aliases:
  - MS-drift-reconciliation
  - MS-reporting-and-actionable-insights
  - MS-scheduled-jobs
  - MS-refactoring-and-prevention-rules
  - MS-maintenance-history
---

# [MS-maintenance-operations] Repository maintenance operations

## Goal

Advances `ARCH-01-introduction-and-goals` §1.1 (Asset Distribution & Guidance Delivery), §1.2 (Repository
Governance & Deterministic Verification) and §1.3 (Delivery Workflow Orchestration) by turning recurring repository
upkeep into evidence-based procedures an agent can run on request or from a schedule the user owns. The opt-in
`maintenance` bundle of `devkit-catalog` holds the procedures; devkit provides their retrieval contract, not a
scheduler.

## Exit condition

- Spec-code drift reconciliation, weekly reporting and a broad review and refactoring pass are independently
  invocable `maintenance` playbooks, each ending in explicit decisions or follow-ups backed by repository evidence.
- An external runner retrieves a selected playbook by its exact ID and follows it; scheduling stays outside devkit.
- Each maintenance run leaves a durable, revision-linked execution record kept apart from code history, which an
  agent can list and read without changing the local checkout.

## Non-goals

- **Scope Excluded**: A devkit scheduler, daemon or job registry; automatic code changes or integration from a
  maintenance run; mandatory rule growth for every cleanup finding.

## Completion review

Decomposition: pending
Direct proposal work: pending

Confirm both with the current Backlog close candidate; record confirmed and status done together after the user's
confirmation. Missing assertions mean unconfirmed. Actual semantic scope changes reset both to pending; normal handoff does not.
