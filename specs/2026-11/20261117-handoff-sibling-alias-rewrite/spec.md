---
id: SPEC-handoff-sibling-alias-rewrite
title: Handoff rewrites alias references to already handed-off proposals
summary: The proposal handoff commit is refused when the carried files cite a sibling proposal that was handed off after this proposal's Planning merged; rewrite such alias references to their current IDs inside the handoff transaction.
status: planned
created: 2026-11-17
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-handoff-sibling-alias-rewrite] Handoff rewrites alias references to already handed-off proposals

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
