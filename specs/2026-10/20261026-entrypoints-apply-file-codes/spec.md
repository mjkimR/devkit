---
id: SPEC-entrypoints-apply-file-codes
title: Entrypoints apply accepts or refuses file codes
summary: devkit spec entrypoints derive --apply --code <file> applies nothing and exits 0 when the file lies under a directory candidate; accept such a file or refuse each unmatched --code with a stable code.
status: planned
created: 2026-10-26
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-entrypoints-apply-file-codes] Entrypoints apply accepts or refuses file codes

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
