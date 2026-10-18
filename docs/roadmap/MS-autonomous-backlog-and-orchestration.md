---
id: MS-autonomous-backlog-and-orchestration
title: Backlog subagent roles and multi-unit orchestration maturity
summary: "Adds dedicated Backlog subagent roles for feedback triage and request decomposition and hardens multi-unit execution across local-orchestrated and cloud-pr delivery modes."
status: planned
created_at: 2026-10-18
depends_on: []
---

# [MS-autonomous-backlog-and-orchestration] Backlog subagent roles and multi-unit orchestration maturity

## Goal

Advances `ARCH-01-introduction-and-goals` §1.3 (Delivery Workflow Orchestration) and §1.7 (Task Worktrees) by introducing isolated Backlog subagent roles (`triage` and `decomposer`, noted as follow-ups in `ADR-roadmap-in-repository`) and hardening multi-unit orchestration (`CAP-DLV-delivery-workflows`, `CAP-WT-task-worktrees`) across `local-orchestrated` and `cloud-pr` execution modes.

## Exit condition

- Backlog feedback triage and draft decomposition can be delegated to dedicated subagents with verified write boundaries and provenance preservation (`decomposed_from`, feedback promotion).
- Multi-unit `local-orchestrated` and `cloud-pr` runs execute, recover from worker problem records, and integrate across supported hosts with deterministic scope isolation (`CAP-COLL-work-scope-registry`).

## Non-goals

- **Scope Excluded**: External tracker synchronization or outbound issue generation (`ADR-roadmap-in-repository`), and replacing user-owned gates (`plan-intent`, `plan-accept`, and milestone transitions).
