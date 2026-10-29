---
id: SPEC-incubation-discovery-teams
title: Explicit incubation research entry and discovery teams
summary: "Provide an explicitly invoked research skill and optional discovery roles that compare early product directions and retain honest initial documents and a roadmap before development."
status: in_progress
created: 2026-10-29
related_capabilities: [CAP-DLV-idea-incubation]
related_usecases: [UC-incubate-an-idea]
workflow: sdd-spec-feature
---

# [SPEC-incubation-discovery-teams] Explicit incubation research entry and discovery teams

## 1. Problem and User Stories

Current incubation supports adaptive next actions but lacks a deliberate broad-research entry and assignments
for independent directions, cross-candidate criticism and initial document/roadmap synthesis. The approved design
is retained in `ADR-extend-incubation-with-optional-discovery-teams` and
`ADR-keep-discovery-plans-distinct-from-delivery-commitments`. This changes `UC-incubate-an-idea`.

- As a product owner with an ambiguous idea or early roadmap, I want to invoke a bounded research team and receive
  researched alternatives, a provisional direction and useful initial documents before authorizing development.
- As the coordinating agent, I want distinct optional role assignments, explicit evidence/authority boundaries
  and resumable current facts, without a runtime scheduler or a required team sequence.
- As an incubation consumer, I want the research entry installed without devkit-spec and without changing my
  effective approach or seeding product documents merely by selecting the bundle.

## 2. Non-Goals and Assumptions

Scope Excluded: an agent bus, scheduler, new wheel, model router, fixed hierarchy, mandatory role sequence,
automatic implementation, publication, SDD adoption, a new document kind/parser and feedback lifecycle changes.

The invoking Host is the master. Existing role IDs remain available; three distinct optional roles are added.
`invocation = "user"` uses existing distribution projection, rather than hand-authored native invocation fields.
No product UI or screens change. Product discovery still requires effective incubation; authoring this feature
in devkit's SDD checkout does not activate incubation there.

Quality walkthroughs establish bounded observed behavior only. No agent count, numeric score, token saving or
consensus proves global optimality. Missing execution evidence remains unverified.

## 3. Acceptance Criteria

### [AC-01] Explicit opt-in distribution

- **Given** docs/catalog are installed and incubation is explicitly selected.
- **When** the core preset is synchronized for supported hosts.
- **Then** both incubation entries and all six optional role contracts are deployed, with the research skill's
  native user-invocation settings where supported, while existing context and product documents are not seeded.

### [AC-02] Scope and approach before product actions

- **Given** a research request and known user goals/constraints, or an SDD/invalid effective approach.
- **When** the research entry starts.
- **Then** it reuses the known facts and asks only consequential missing decisions; SDD/invalid policy stops product
  writes and reports the existing configuration action without changing approach.

### [AC-03] Adaptive master and independent alternatives

- **Given** an open product/architecture direction with separable uncertainties.
- **When** the Host commissions research assignments.
- **Then** assignments name goals, source identity, evidence/read/write boundaries, permitted actions, expected
  returns and stopping conditions; materially distinct hypotheses develop before sharing peer conclusions.

### [AC-04] Grounded research and cross-candidate criticism

- **Given** competing evidence, unsupported claims or shared assumptions across candidate directions.
- **When** researcher/explorer/critic results are compared.
- **Then** source-supported observations, vendor claims, inference, contradictions and unknowns remain distinct;
  criticism names evidence and a failure condition, and zero findings does not require an invented objection.

### [AC-05] Proportionate documents and conditional roadmap

- **Given** compared evidence and a provisional or user-selected direction.
- **When** the planner drafts and the Host retains the result.
- **Then** product framing, evidence/alternatives, direction/architecture assumptions and an outcome/dependency
  roadmap are represented proportionately; recommendations do not become user decisions, current capabilities,
  invented dates, delivery Units or implementation authority.

### [AC-06] Role authority and bounded partial completion

- **Given** an unavailable role, an out-of-scope return, insufficient evidence or an exhausted research bound.
- **When** the Host validates the investigation.
- **Then** it rejects unsupported/out-of-scope results, retains partial evidence and missing coverage, and reports
  no fabricated role execution, native sandbox, token counter or permission.

### [AC-07] Resume and optional scale

- **Given** retained notes/current context, or a small existing question.
- **When** another context resumes or the coordinator chooses an assignment.
- **Then** current alternatives, evidence, actual decisions, unknowns and reopening conditions are recoverable,
  and no fixed role count, full document suite or critic round is required for a small action.

### [AC-08] Independent consumer and compatibility

- **Given** installed docs/catalog wheels without devkit-spec.
- **When** selection, sync, removal and re-selection run.
- **Then** the explicit research skill and six role projections remain available as selected, existing role IDs
  stay compatible, project-owned context and discovery notes survive, and no SDD commands/assets are required.

### [AC-09] Observed behavioral evidence

- **Given** matched bounded idea, architecture and conflicting-source discovery fixtures.
- **When** existing and candidate guidance are exercised with identified inputs/settings, including candidate
  delegation and fresh-context resume.
- **Then** retained evidence records actual role actions, outputs, checks and limits; synthetic return replays are
  labelled, and candidate distinctness, source support, commitments, resume fidelity and effort are assessed
  without claiming universal quality or treating keyword assertions as live research evidence.

## 4. Verification

Deterministic catalog integration/e2e checks cover distribution, invocation projection, role metadata and
preservation. Bounded agent runs and an independent review assess semantic criteria. Use repository lint/type
checks, `just test-affected` with its full fallback, affected consumer e2e and committed-snapshot rules.
