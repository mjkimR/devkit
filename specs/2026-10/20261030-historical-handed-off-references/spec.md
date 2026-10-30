---
id: SPEC-historical-handed-off-references
title: Accept handed-off proposal IDs in work history
summary: Stop RULE-document-reference from reporting a handed-off PROP-<slug> as an unresolved ID in explicitly targeted work history, where handoff never rewrites references, when its SPEC-<slug> exists.
status: planned
created: 2026-10-30
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-historical-handed-off-references] Accept handed-off proposal IDs in work history

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
