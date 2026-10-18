---
id: MS-reporting-and-actionable-insights
title: Evidence-based reporting and actionable repository insights
summary: "Delivers periodic reporting through the shared job scheduler, with traceable findings, trends, and concrete follow-up recommendations across governance and delivery activities."
status: planned
created_at: 2026-10-18
depends_on: [MS-scheduled-jobs]
---

# [MS-reporting-and-actionable-insights] Evidence-based reporting and actionable repository insights

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification), §1.3 (Delivery Workflow Orchestration), and §2 (Agent-First Design Philosophy) by periodically turning check and activity evidence into reports that identify repository health, recurring problems, and the next engineering action. Reporting runs as a recurring job on `MS-scheduled-jobs`, covering hygiene findings, delivery progress, refactoring results, and job execution evidence.

## Exit condition

- Reporting executes on a configured cadence through the shared scheduler, records each run and report artifact, and is verified across successive scheduled occurrences.
- Reports identify their scope, repository revision, observation period, evidence sources, and missing or stale evidence; a missing run is distinguishable from a clean result.
- Reports distinguish deterministic rule violations from agent assessments and link findings to their source runs, documents, or code locations.
- Comparable reports show new, recurring, and resolved findings, including AI slop removal, commonization results, and the disposition of proposed prevention rules when refactoring evidence is available.
- Prioritized recommendations identify concrete next actions and reference existing feedback or proposals when available, preserving traceability without duplicating follow-up work.
- Reports provide bounded agent-facing output and a structured result consistent with `ARCH-08-1-agent-output` and `CAP-ADV-agent-advisory-protocol`, with detailed evidence available as artifacts.

## Non-goals

- **Scope Excluded**: An external analytics service, automatic outbound publication, and treating an agent assessment as a deterministic rule violation.
