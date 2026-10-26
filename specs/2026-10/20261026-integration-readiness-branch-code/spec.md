---
id: SPEC-integration-readiness-branch-code
title: Integration readiness loads branch rules with branch code
summary: Integration readiness and the CI rules snapshot load a branch's new bundled rule with the base checkout's installed code, so a branch adding a rule whose implementation lives in package code is refused; evaluate it with the code being landed.
status: planned
created: 2026-10-26
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-integration-readiness-branch-code] Integration readiness loads branch rules with branch code

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
