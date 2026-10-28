---
id: PROP-incubation-sdd-baseline
title: Adopt SDD from a verified implemented baseline
summary: Establishes a verified current-state baseline for voluntary SDD adoption
  without reconstructing delivery artifacts for earlier incubation work.
status: reviewing
created_at: 2026-10-28
target_area: delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-idea-incubation
boundaries:
  owns:
  - packages/
  - docs/capabilities/
  - docs/usecases/
  - docs/architecture/
  - docs/decisions/
  - guides/
  excludes: []
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-incubation-lifecycle-policy
- PROP-incubation-development-guidance
---

# [PROP-incubation-sdd-baseline] Adopt SDD from a verified implemented baseline

## 1. Background & Hypothesis

MS-idea-incubation permits an app to remain in incubation. When the user chooses SDD, the retained implementation and current documents need a verified baseline. Existing spec creation and reconciliation can be reused where appropriate, without reconstructing earlier delivery history.

## 2. Technical Spike Questions

- **Q1**: What evidence and minimum current-state document set establish the retained baseline?
- **Q2**: How are unresolved behavior and missing usage or test evidence reported before claiming readiness?
- **Q3**: Which transition entry and existing SDD operations establish the baseline and route subsequent work?

## 3. Proposed Design & Impact

Provide voluntary adoption from the implemented product. Compare retained behavior, important structure, current decisions and verification methods to the implementation. Planning chooses the transition artifacts and reuse of existing reconciliation, without requiring historical proposals or Units.

Expected acceptance checks:

- Only an explicit user choice begins SDD adoption; size, elapsed time or experiment count do not force it.
- The baseline records retained current behavior and structure against actual implementation and verification evidence.
- Unresolved behavior and missing evidence are exposed before readiness is claimed.
- Subsequent changes follow selected SDD policies without backfilled approvals, Units or discarded-decision ADRs.

- **Scope Excluded**: Automatic graduation, reconstruction of experiment history, changes to incubation product-discovery behavior and a persistent autonomous execution service.

## 4. Lifecycle & Retirement Criteria

Planning settles the direction before acceptance and handoff to one feature spec. If Planning finds independently deliverable work requiring multiple specs, return this draft for decomposition. This draft records remaining milestone scope; it claims no implemented or verified behavior.
