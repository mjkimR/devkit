---
id: MS-backlog-subagent-roles
title: Backlog triage and decomposer subagent roles
summary: "Adds dedicated Backlog subagent roles for feedback triage and request decomposition, so Backlog work can be delegated with verified write boundaries and preserved provenance."
status: done
created_at: 2026-10-18
depends_on: []
aliases:
  - MS-autonomous-backlog-and-orchestration
---

# [MS-backlog-subagent-roles] Backlog triage and decomposer subagent roles

## Goal

Advances `ARCH-01-introduction-and-goals` §1.3 (Delivery Workflow Orchestration) by introducing isolated Backlog
subagent roles (`triage` and `decomposer`, noted as follow-ups in `ADR-roadmap-and-milestones`), so feedback triage
and draft decomposition no longer fill the coordinating session's context.

## Exit condition

- Backlog feedback triage and draft decomposition can be delegated to dedicated subagents with verified write
  boundaries and provenance preservation (`decomposed_from`, feedback promotion).

## Non-goals

- **Scope Excluded**: External tracker synchronization or outbound issue generation (`ADR-roadmap-and-milestones`),
  and replacing user-owned gates (`plan-intent`, `plan-accept`, and milestone transitions).
- **Moved out**: Hardening multi-unit `local-orchestrated` and `cloud-pr` execution was split from this theme on
  2026-10-26. It is a separate concern of `CAP-DLV-delivery-workflows` and `CAP-WT-task-worktrees`, not Backlog work.

## Completion review

Decomposition: confirmed
Direct proposal work: confirmed

Confirm both with the current Backlog close candidate; record confirmed and status done together after the user's
confirmation. Missing assertions mean unconfirmed. Actual semantic scope changes reset both to pending; normal handoff does not.
