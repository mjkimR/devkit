---
id: SPEC-retained-runtime-receipt
title: Diagnose a retained MCP runtime older than the receipt it reads
summary: When a retained MCP service refuses a source receipt that its own older reader cannot parse, integration reports the runtime version mismatch with a stable code and a restart directive instead of a bare RECEIPT_INVALID, without weakening receipt validation.
status: planned
created: 2026-10-22
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---
<!-- devkit:skeleton -->

# [SPEC-retained-runtime-receipt] Diagnose a retained MCP runtime older than the receipt it reads

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
