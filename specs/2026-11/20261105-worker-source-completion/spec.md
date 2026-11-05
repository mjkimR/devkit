---
id: SPEC-worker-source-completion
title: Preserve source feedback completion scope
summary: Worker inspection retains the completion scope of explicitly linked feedback that was open at the audit base.
status: planned
created: 2026-11-05
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-worker-source-completion] Preserve source feedback completion scope

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
