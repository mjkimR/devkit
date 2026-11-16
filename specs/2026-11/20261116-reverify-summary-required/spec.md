---
id: SPEC-reverify-summary-required
title: envelope reverify requires a summary that envelope commit accepts
summary: Makes devkit workflow envelope reverify refuse or fill a missing summary so every envelope it writes passes envelope commit, closing FB-reverify-writes-envelope-commit-refuses.
status: planned
created: 2026-11-16
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-reverify-summary-required] envelope reverify requires a summary that envelope commit accepts

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
