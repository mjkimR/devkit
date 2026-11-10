---
id: SPEC-remove-plan-intent-gate
title: Remove the plan-intent gate
summary: "Remove duplicate task-intent approval from SDD while preserving explicit task authorization, later approval boundaries and historical workflow records."
status: in-progress
created: 2026-11-10
related_capabilities: [CAP-DLV-delivery-workflows, CAP-DLV-proposal-planning, CAP-DLV-project-policy, CAP-HARN-agent-guidance]
related_usecases: [UC-route-development-intent, UC-plan-and-hand-off-a-proposal, UC-drive-development-to-integration]
workflow: sdd-spec-feature
---

# [SPEC-remove-plan-intent-gate] Remove the plan-intent gate

## 1. Problem Statement & Motivation

Explicit task instructions already authorize their stated scope. The SDD intent gate adds a decision record,
commit and acceptance/handoff special cases without deciding another question. `ADR-remove-plan-intent-gate`
authorizes its removal and identifies five partially replaced decisions.

## 2. User Stories

- As a developer, I start explicitly requested SDD work without recording the same intent again.
- As a maintainer, I retain readable historical records and the later approval boundaries.

## 3. Non-Goals

- **Scope Excluded**: changing the generic gate engine or custom workflow gate semantics.
- **Scope Excluded**: changing plan-accept, proposal-handoff or dev-integration policies.
- **Scope Excluded**: rewriting historical specs/materials or splitting unrelated documentation.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Ungated intent retains eligibility and stage identity

- **Given** the six deployed SDD workflow definitions.
- **When** validating and evaluating requested work.
- **Then** no definition declares or requests plan-intent; existing intent stage IDs, non-gate checks and returns remain.
- **And** proposal size XL still blocks Planning, and bugfix Red/Green order and other gates remain.

### [AC-02] Acceptance and handoff need only their own approval

- **Given** an otherwise eligible proposal without an intent record under ask or auto acceptance policy.
- **When** accepting and handing it off through the public operations.
- **Then** acceptance succeeds without pending intent, and handoff requires and carries only plan-accept.
- **And** missing plan-accept still refuses composed handoff; custom gates retain generic behavior.

### [AC-03] Valid historical records remain readable

- **Given** a live or completed Unit with a valid existing plan-intent decision and historical intent-stage records.
- **When** workflow next and document rules read it after the gate removal.
- **Then** the record remains unchanged and causes no unknown-gate failure; no migration runs.

### [AC-04] Retired configuration is visible without active authority

- **Given** default policy or configured plan-intent ask, auto or off and a custom gate.
- **When** inspecting policy.
- **Then** active output contains the three later boundaries and the custom gate, without plan-intent.
- **And** a configured retired key returns SPEC_APPROVAL_KEY_IGNORED with removal advice; default policy has no such warning.

### [AC-05] Guidance and contracts agree on authorization

- **Given** source and deployed guidance, Living Spec and the four English handbook pages.
- **When** routing work or escalating session depth to spec.
- **Then** explicit instructions authorize scope without an intent approval; escalation reason is recorded in spec.md.
- **And** workflow stage IDs and historical files are preserved, and all remaining approval boundaries stay explicit.

## 5. Assumptions & Retained Decisions

- Planning was accepted at ac35be47 and handed off from a74c84af; evidence is retained under
  `docs/materials/2026-11/20261110-remove-plan-intent-gate/`.
- Retain ungated intent stages to preserve recorded stage names and return targets.
- Classify this as feature, spec depth Development, medium effort; no new feature dependency is needed.
- Legacy compatibility had static evidence in Planning and requires executable regression coverage here.
- No timing or performance improvement is claimed. Explicit instructions remain the authorization boundary.
