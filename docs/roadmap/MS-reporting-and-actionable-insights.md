---
id: MS-reporting-and-actionable-insights
title: Weekly reporting and actionable repository insights playbook
summary: "Delivers a manually invocable weekly reporting playbook covering completed work, ADR changes, repository health, and actionable follow-ups, with evidence and an explicit publication step."
status: planned
created_at: 2026-10-18
depends_on: []
---

# [MS-reporting-and-actionable-insights] Weekly reporting and actionable repository insights playbook

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification), §1.3 (Delivery Workflow Orchestration), and §2 (Agent-First Design Philosophy) by providing a maintenance playbook that turns a week's repository evidence into a report of completed work, decisions, repository health, and next actions. The playbook can be invoked manually without a scheduler.

Delivery belongs to the opt-in `maintenance` bundle in `devkit-catalog`, containing three independently invocable
playbooks: `weekly-report`, `drift-reconciliation`, and `review-refactor`. This milestone owns `weekly-report`.
The bundle offers `reporting` (weekly report), `upkeep` (drift reconciliation and review/refactoring), and `all`
(all three, the default) presets. Selecting or invoking one playbook does not require invoking the others; bodies
remain loaded on demand. The three playbooks share one bundle rather than separate bundles or packages.

## Exit condition

- `weekly-report` is distributed as a playbook asset of `maintenance` in `devkit-catalog`, with its applicable preset selections, package validation, and bundle recommendation documentation verified. The bundle's target composition is the three playbooks above; this milestone verifies its own contribution without waiting for the others to be implemented.
- A reporting playbook defines its inputs, observation period and timezone, evidence collection, report generation, publication, and completion evidence; a manual run demonstrates the path.
- Reports summarize completed work, added or changed ADRs, important behavior changes, unresolved problems, and next actions, linking claims to commits, work units, decisions, or check results.
- Reports identify their scope, repository revision, observation period, evidence sources, and missing or stale evidence; unavailable maintenance results are distinguishable from clean results.
- Available hygiene, drift reconciliation, and review/refactoring results are summarized without requiring those activities to run first. Comparable reports distinguish new, recurring, and resolved findings when evidence permits.
- Prioritized recommendations reference existing feedback or proposals when available, preserving traceability without duplicating follow-up work.
- Report generation and publication are separate steps. The playbook identifies the publication destination and required authorization, records the artifact and publication outcome, and defines how reruns handle an existing report for the same period. Missing publication configuration leaves a generated report with an explicit pending publication outcome.
- Agent-facing command output follows `ARCH-08-1-agent-output` and `CAP-ADV-agent-advisory-protocol`, with detailed evidence available in the report artifact.

## Non-goals

- **Scope Excluded**: Scheduler implementation or trigger design, an external analytics service, publication without the configured authorization, and treating an agent assessment as a deterministic rule violation.
