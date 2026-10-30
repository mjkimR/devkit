---
id: UC-adopt-sdd-from-adaptive-development
aliases:
  - UC-adopt-sdd-from-incubation
title: Adopt SDD from an adaptive-development product
summary: "An AI coding agent verifies the user's retained adaptive-development product, prepares current-state evidence and documents, then activates SDD for subsequent work under an exact-effects user decision."
area: delivery
primary_actor: AI coding agent
supporting_actors:
  - Product owner
status: active
created_at: 2026-10-28
capabilities:
  - CAP-DLV-sdd-baseline-adoption
  - CAP-HARN-agent-guidance
entrypoints:
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/sdd-baseline/SKILL.md
---

# [UC-adopt-sdd-from-adaptive-development] Adopt SDD from an adaptive-development product

## 1. Goal

- **Goal**: Establish a truthful baseline of the product the owner intends to preserve, so later changes can use SDD.
- **Trigger**: The product owner explicitly requests or confirms baseline adoption.
- **Preconditions**: The actor can inspect the repository and execute its available verification commands.

## 2. Main Success Scenario

1. The agent starts the explicitly requested baseline procedure without activating SDD (`CAP-DLV-sdd-baseline-adoption`, rules 1–2).
2. The agent identifies current source, approach, retained product scope, exclusions and existing evidence (`CAP-DLV-sdd-baseline-adoption`, rules 2–3).
3. The agent compares retained behavior, structure and choices against implementation and current documents (`CAP-DLV-sdd-baseline-adoption`, rules 3 and 6).
4. The agent runs the relevant independent checks and representative user flows, correcting the authorized current documents (`CAP-DLV-sdd-baseline-adoption`, rules 4–5).
5. The agent presents the evidenced ready baseline and exact activation effects (`CAP-DLV-sdd-baseline-adoption`, rules 5 and 8).
6. The product owner authorizes those same source, scope and effects, or the agent reuses their existing explicit decision (`CAP-DLV-sdd-baseline-adoption`, rule 7).
7. The agent applies the authorized policy effects and verifies observed consistency and subsequent SDD routing (`CAP-DLV-sdd-baseline-adoption`, rules 9–10).

## 3. Extensions

- **1a.** no explicit request: ordinary adaptive development continues; this use case does not start.
- **2a.** already SDD: the agent routes the request to ordinary reconciliation or brownfield adoption; this use case ends without another graduation.
- **2b.** absent live context or spec assets: the agent discovers current facts and presents the needed installation/selection effects while keeping adaptive development; resumes at step 3 after authorized preparation.
- **4a.** missing/failed/skipped evidence or mismatch: the agent records the gap and presents correction, user-decided scope change or deferral; resumes at step 3 after correction, or ends in adaptive development without readiness.
- **5a.** changed relevant source: the agent invalidates affected observations and resumes at step 3; stale evidence does not activate SDD.
- **6a.** effects not authorized: the agent leaves adoption unactivated; this use case ends. A necessary provider change is an activation effect rather than an implicit settings rewrite.
- **7a.** partial installation/update/sync failure: the agent reports actual partial state and supported recovery; resumes at step 3 after source/evidence revalidation or ends with no successful-adoption claim.

## 4. Postconditions

- **Success guarantee**: The selected retained product has truthful current documents and observed evidence; approach,
  selected guidance and subsequent routing agree on SDD. No retrospective delivery records were invented.
- **Minimal guarantee**: Unrelated edits and existing SDD history remain. Unresolved gaps stay visible; failed activation
  reports actual partial state without assuming rollback or claiming success.

## 5. Acceptance Criteria by Example Mapping

Rules: explicit entry; staged preparation; retained evidence; gaps block readiness; exact-effects authority;
freshness; partial-state recovery; subsequent SDD routing (`CAP-DLV-sdd-baseline-adoption`).

### Voluntary entry and already-SDD handling

- **Given** ordinary adaptive development without adoption intent, or an already-SDD repository,
- **When** the agent determines the applicable path,
- **Then** it does not start automatic graduation and uses existing reconciliation for the already-SDD case.
- **Covers**: 1a, 2a.

### Successful retained baseline

- **Given** a runnable local-note app with current documents and observed checks,
- **When** the agent completes preparation and applies the owner's exact-effects decision,
- **Then** inspection and sync agree on SDD and the subsequent requested change reaches ordinary SDD routing without a baseline Unit.
- **Covers**: main success scenario.

### Missing context or installation preparation

- **Given** no live context or missing spec assets,
- **When** the agent discovers facts and performs authorized asset preparation,
- **Then** implementation and user input supply current facts while the effective approach remains adaptive-dev.
- **Covers**: 2b.

### Required evidence gap

- **Given** a passing document-format check but unexecuted required usage evidence,
- **When** readiness is assessed,
- **Then** the report remains gap and no activation occurs.
- **Covers**: 4a.

### Changed source

- **Given** previously verified app source that then changes,
- **When** the agent rechecks the affected flow,
- **Then** it records the new source identity and any actual failure as a gap before activation.
- **Covers**: 5a.

### Unapproved provider effect

- **Given** a ready baseline whose necessary missing-provider configuration or project-to-spec switch is not authorized,
- **When** activation effects are considered,
- **Then** no successful activation is claimed and the mismatch is reported for the owner's decision.
- **Covers**: 6a.

### Partial sync failure

- **Given** an authorized policy edit followed by an actual sync failure,
- **When** recovery is reported,
- **Then** actual partial approach/selection state is visible, no rollback is assumed and supported correction plus revalidation precedes completion.
- **Covers**: 7a.
