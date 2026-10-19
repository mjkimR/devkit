---
id: SPEC-summary-length-guard
title: Reject oversized document summaries before creation
summary: Document creation commands reject summaries longer than 300 characters before writing files, matching the document summary rule.
status: planned
created: 2026-10-19
related_capabilities: []
related_stories: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-summary-length-guard] Reject oversized document summaries before creation

## 1. Problem Statement & Motivation

<Describe the problem, who has it and why it matters now.>

## 2. Defect Characterization

- **Current behavior**: <trigger, environment and the observed wrong result, with evidence>
- **Expected behavior and its basis**: <the result the existing contract requires, citing its capability, story, ADR or test>
- **Behavior to preserve**: <call paths, input boundaries and contracts that must keep working, with their tests>
- **Reproduction conditions**: <the command, data and environment that reproduce the defect>

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>
