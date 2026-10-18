---
id: MS-scheduled-jobs
title: Scheduled repository jobs and activity execution
summary: "Provides the shared scheduling foundation for periodic hygiene, reporting, and refactoring jobs, with observable execution and recovery while preserving activity approval boundaries."
status: planned
created_at: 2026-10-18
depends_on: []
---

# [MS-scheduled-jobs] Scheduled repository jobs and activity execution

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification), §1.3 (Delivery Workflow Orchestration), and §3.4 (Platform Compatibility) by providing a shared scheduling foundation for periodic repository maintenance without requiring a devkit background daemon. Hygiene, reporting, and refactoring are all recurring jobs on this foundation. Hygiene runs deterministic checks (`CAP-GOV-evaluation-lifecycle`); reporting and refactoring also require agent investigation and judgment. Their specialized outcomes are defined by `MS-reporting-and-actionable-insights` and `MS-refactoring-and-prevention-rules`.

## Exit condition

- Repository-owned job definitions declare the schedule, execution scope, and check or activity to invoke, with a documented runner integration and a verified recurring execution.
- Periodic hygiene runs through the shared scheduler. Reporting and refactoring use the same job contract and execution records; each is verified as a recurring job in its own milestone.
- Jobs support separately configured cadences and explicit sequencing or evidence dependencies so reports can consume completed hygiene and refactoring runs and identify unavailable inputs.
- Job execution handles overlapping invocations, missed runs, failures, and retries with explicit outcomes and recovery actions; repeated execution does not duplicate work already recorded for the same scheduled occurrence.
- Scheduled activities preserve their workflow approval and integration boundaries. A schedule authorizes invocation within the configured scope; it does not supply a user's decision at a gate.
- Each run records its identity, repository revision, timing, outcome, and resulting artifacts so reporting can consume the evidence and an agent can determine the next action.

## Non-goals

- **Scope Excluded**: A required devkit background daemon, a general-purpose distributed scheduler, and bypassing workflow approvals for unattended execution.
