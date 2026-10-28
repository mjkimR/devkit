---
id: SPEC-worker-inspection-fixes
title: Inspect partial worker turns with independent audit and governance bases
summary: Fixes scope inference before reconciliation exists and separates the accepted-turn write audit from cumulative feature governance without weakening either check.
status: planned
created: 2026-10-28
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-worker-inspection-fixes] Inspect partial worker turns with independent audit and governance bases

## 1. Problem Statement & Motivation

<Describe the problem, who has it and why it matters now.>

## 2. Defect Characterization

- **Current behavior**: <trigger, environment and the observed wrong result, with evidence>
- **Expected behavior and its basis**: <the result the existing contract requires, citing its capability, use case, ADR or test>
- **Behavior to preserve**: <call paths, input boundaries and contracts that must keep working, with their tests>
- **Reproduction conditions**: <the command, data and environment that reproduce the defect>

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## Source feedback

- `FB-worker-inspect-partial-turn-scope`: infer declared unit/task scope before optional reconcile exists; retain malformed-record diagnostics and stage requirements.
- `FB-worker-inspect-scoped-reconcile-base`: keep last-accepted turn write auditing distinct from cumulative feature rules comparison, with explicit input/provenance and tests.
