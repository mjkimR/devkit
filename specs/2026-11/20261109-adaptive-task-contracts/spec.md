---
id: SPEC-adaptive-task-contracts
title: Adaptive task decomposition and role specialization
summary: "Strengthen adaptive task assignments and role checks while preserving optional delegation and caller authority."
status: in-progress
created: 2026-11-09
related_capabilities: [CAP-DLV-adaptive-development]
related_usecases: [UC-advance-an-idea]
workflow: sdd-spec-feature
---

# [SPEC-adaptive-task-contracts] Adaptive task decomposition and role specialization

## Problem Statement

Separate file scopes can share an unsettled interface. Adaptive assignments need ownership and handoff information
to avoid incompatible parallel work while retaining caller authority.

## User Stories

- As coordinator, I need to split work by independently checkable deliverables and dependencies.
- As a role executor, I need role-specific checks without acquiring additional authority.

## Non-Goals

- **Scope Excluded**: A runtime scheduler, agent bus, new public agent IDs, model routing, feature dependency edges,
  mandatory planning artifacts and claims of model performance.

## Acceptance Criteria

### [AC-01] Shared interface before concurrent writers

- **Given** two disjoint file assignments depend on an unsettled API.
- **When** the coordinator partitions the work.
- **Then** guidance assigns the interface and owner before dependent concurrent writes, supplies its identity to
  dependents and requires reassessment when it changes.

### [AC-02] Independent assignment handoffs

- **Given** independently checkable deliverables.
- **When** the coordinator delegates them.
- **Then** each assignment names one owner, dependency or none, completion evidence and expected handoff alongside
  existing authority and source identity.

### [AC-03] Direct or serial fallback

- **Given** an atomic task or unavailable isolation.
- **When** execution is chosen.
- **Then** direct or serial work preserves result evidence without requiring a team or persistent graph.

### [AC-04] Distinct bounded overlays

- **Given** an architect, builder, qa-tester or reviewer assignment.
- **When** its overlay is reviewed against its responsibility.
- **Then** it names distinct relevant checks and preserves the execution contract's permission and lifecycle limits.

### [AC-05] Asset verification and limits

- **Given** the consumer-facing installed assets.
- **When** packaging, self-containment, projection and three representative assignment fixtures are reviewed.
- **Then** checks pass and the report distinguishes contract review from observed live-agent behavior.

## Assumptions

Reuse the existing delegation payload. A prose handoff is sufficient; no persistent task graph is needed.
Review independent deliverables, disjoint files sharing an API and unavailable isolation. Record each fixture's
input, ownership, interface identity, dependency ordering, handoff, reviewer and unresolved gaps.
