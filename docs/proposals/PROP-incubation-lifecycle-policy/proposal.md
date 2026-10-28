---
id: PROP-incubation-lifecycle-policy
title: Make development approach policy consistent across SDD consumers
summary: Defines an inspectable development approach and aligns lifecycle enforcement,
  CLI preconditions and integration readiness while retaining document and project
  checks.
status: draft
created_at: 2026-10-28
target_area: delivery/
priority: medium
size: L
planning_effort: medium
dev_effort: medium
milestone: MS-idea-incubation
boundaries:
  owns:
  - packages/devkit-spec/
  - packages/devkit-docs/
  - packages/devkit/
  - packages/devkit-dist/
  - docs/capabilities/
  - docs/usecases/
  - docs/architecture/
  - docs/decisions/
  - guides/
  excludes: []
task_kind: feature
workflow: sdd-proposal
---

# [PROP-incubation-lifecycle-policy] Make development approach policy consistent across SDD consumers

## 1. Background & Hypothesis

MS-idea-incubation separates reusable document checks from SDD obligations. Independent document distribution supplies the formats; it does not define runtime lifecycle policy. CAP-DLV-project-policy currently owns SDD policy, and delivery integration and governance consumers must agree with installed guidance.

## 2. Technical Spike Questions

- **Q1**: Where does the authoritative development-approach setting live, and how is it inspected without requiring the SDD package?
- **Q2**: Which command preconditions, lifecycle rules and integration checks apply in incubation, and how are omitted checks distinguished from passed checks?
- **Q3**: Are temporary overrides necessary, and how do repositories retaining SDD preserve their current enforcement?

## 3. Proposed Design & Impact

Define one coherent approach-selection contract and align its command, rule, integration and guidance consumers. Planning chooses the configuration owner and interface; this draft selects neither a schema nor a blanket bypass. Document-only distribution must be integrated before Development.

Expected acceptance checks:

- An incubation selection is inspectable and consistent across CLI, active rules and installed guidance.
- Document identity, format and reference validation and independent project checks remain runnable.
- Offered operations work without SDD Units where appropriate; omitted SDD checks are reported distinctly.
- A repository retaining SDD preserves existing gates and lifecycle enforcement.

- **Scope Excluded**: Product discovery skills, a framework scaffold, baseline adoption and changes to generic distribution semantics.

## 4. Lifecycle & Retirement Criteria

Planning settles the direction before acceptance and handoff to one feature spec. If Planning finds independently deliverable work requiring multiple specs, return this draft for decomposition. This draft records remaining milestone scope; it claims no implemented or verified behavior.
