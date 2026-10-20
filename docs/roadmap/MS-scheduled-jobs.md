---
id: MS-scheduled-jobs
title: Scheduled repository jobs and activity execution
summary: "Explores optional scheduling for repository maintenance independently of manually invocable playbooks, with execution recovery and preserved approval boundaries; trigger integration remains a later design decision."
status: planned
created_at: 2026-10-18
depends_on: []
---

# [MS-scheduled-jobs] Scheduled repository jobs and activity execution

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification), §1.3 (Delivery Workflow Orchestration), and §3.4 (Platform Compatibility) by providing optional scheduling for repository maintenance without requiring a devkit background daemon. Maintenance playbooks are independently usable and verifiable through manual invocation; their delivery does not depend on this milestone. The scheduling mechanism and its integration with playbook invocation remain later design decisions.

## Exit condition

- Repository-owned job definitions declare the schedule, execution scope, and check or activity to invoke, with a documented runner integration and a verified recurring execution.
- A selected maintenance procedure demonstrates recurring execution through a documented runner integration. Its domain behavior remains owned by the maintenance playbook; scheduling adds invocation and execution tracking.
- Jobs support separately configured cadences and explicit sequencing or evidence dependencies so reports can consume completed hygiene and refactoring runs and identify unavailable inputs.
- Job execution handles overlapping invocations, missed runs, failures, and retries with explicit outcomes and recovery actions; repeated execution does not duplicate work already recorded for the same scheduled occurrence.
- Scheduled activities preserve their workflow approval and integration boundaries. A schedule authorizes invocation within the configured scope; it does not supply a user's decision at a gate.
- Each run records its identity, repository revision, timing, outcome, and resulting artifacts so reporting can consume the evidence and an agent can determine the next action.

## Non-goals

- **Scope Excluded**: A required devkit background daemon, a general-purpose distributed scheduler, bypassing workflow approvals for unattended execution, and defining maintenance procedures or making scheduler adoption a prerequisite for their manual use.
