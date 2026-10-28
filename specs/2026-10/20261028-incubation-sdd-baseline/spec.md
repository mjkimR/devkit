---
id: SPEC-incubation-sdd-baseline
title: Adopt SDD from a verified implemented baseline
summary: "Establishes an evidenced retained-product baseline through an explicit SDD adoption playbook before activation, without reconstructing incubation delivery history."
status: in-progress
created: 2026-10-28
depends_on:
  - SPEC-incubation-lifecycle-policy
  - SPEC-incubation-development-guidance
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-incubation-sdd-baseline] Adopt SDD from a verified implemented baseline

## 1. Problem Statement & Motivation

Incubation can remain a complete development path. When the user chooses SDD, retained behavior, structure,
choices and verification need a truthful baseline before future changes inherit SDD obligations.
`ADR-adopt-sdd-through-an-evidenced-baseline-playbook` selects a focused playbook over a new runtime or retrospective Unit.
`SPEC-incubation-sdd-baseline-target` lists the current-contract reflection.
Planning evidence remains in `docs/materials/2026-10/20261028-incubation-sdd-baseline/`.

## 2. User Stories

- As an incubation user, I can choose SDD adoption after checking the implemented product I intend to retain.
- As the coordinating agent, I can expose missing evidence, preserve current documents and resume interrupted preparation.
- As a later maintainer, I can change the retained product through SDD without invented records for discarded experiments.

## 3. Non-Goals

- **Scope Excluded**: automatic graduation, a new baseline CLI/API/workflow, retrospective Units or approval history.
- **Scope Excluded**: policy-engine implementation, incubation discovery/roles/context format, a universal stack or application scaffold.
- **Scope Excluded**: automatic legacy containment, unrelated product corrections, history rewriting or a persistent execution service.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Voluntary entry

- **Given** an incubation project, including a large or long-running one,
- **When** ordinary work continues,
- **Then** no baseline transition starts automatically; explicit invocation or confirmation of `sdd-baseline` starts preparation with scope visible and approach unchanged.

### [AC-02] Retained baseline coverage

- **Given** implemented flows, current documents and optional live context,
- **When** preparation runs,
- **Then** an ordinary material report maps retained behavior, important structure, choices and verification to implementation/document/evidence locations; absent context is discovered without reconstructing history and accurate documents are reused.

### [AC-03] Evidence gaps block readiness

- **Given** a failed/skipped required check, undocumented retained behavior, unresolved mismatch or missing usage evidence,
- **When** readiness is assessed,
- **Then** the report identifies a gap and activation does not run; a format check alone is insufficient and scope narrowing requires the user's actual decision.

### [AC-04] Activation is bound to ready effects

- **Given** a ready report and exact source, retained scope and policy effects,
- **When** the user authorizes those effects,
- **Then** the authoritative approach is changed to SDD and selected guidance, inspection and next routing agree; package/asset selection alone never activates SDD and an existing decision for identical effects is reused.

### [AC-05] Stale evidence and partial failure

- **Given** changed relevant source or an installation/policy/sync failure,
- **When** preparation or activation resumes,
- **Then** affected evidence is revalidated, actual partial state and recovery are reported, unrelated edits remain and no failed transition is reported successful; the existing report is reused.

### [AC-06] Current state without invented history

- **Given** discarded experiments, current choices and any retained SDD history,
- **When** baseline documents are written,
- **Then** they describe current intended behavior and known reasons without historical Units, reconstructed approvals or invented rationale; existing SDD history is preserved.

### [AC-07] Delivered adoption path

- **Given** the installed playbook and integrated policy/guidance contracts,
- **When** a sample incubation app exercises success, missing evidence, source change and partial failure,
- **Then** its report, policy/asset state and next SDD route match AC-01 through AC-06, with real versus simulated decisions identified; asset inventory and existing brownfield-adoption regressions pass.

## 5. Implementation Assumptions

The policy prerequisite owns approach inspection and mutation; this playbook consumes that interface.
The guidance prerequisite owns live context; baseline reads its current facts without a parser or fixed filename requirement.
The first parallel turn implements playbook assets and isolated mechanical checks only. Actual adoption exercises,
shared documents and final reconcile wait for the Host to incorporate both prerequisite implementations.
