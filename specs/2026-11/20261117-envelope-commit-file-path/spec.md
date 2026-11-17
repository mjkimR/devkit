---
id: SPEC-envelope-commit-file-path
title: Envelope commit accepts a workspace-relative --file path
summary: devkit workflow envelope commit joins a workspace-relative --file path to the unit directory and its fix repeats the failing path; accept a path that already starts with the unit directory and name a working form in the fix.
status: planned
created: 2026-11-17
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-envelope-commit-file-path] Envelope commit accepts a workspace-relative --file path

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
