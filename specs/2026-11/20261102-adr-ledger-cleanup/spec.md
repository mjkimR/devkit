---
id: SPEC-adr-ledger-cleanup
title: Topic compaction groups and retired stale ADR clauses
summary: ADR compaction groups follow topics instead of the whole supersession closure, with cross-group partial supersession recorded on the replacements; a retiring ADR removes the native-approval and moved-ownership clauses that no longer hold.
status: planned
created: 2026-11-02
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-adr-ledger-cleanup] Topic compaction groups and retired stale ADR clauses

## 1. Problem Statement & Motivation

<Describe the problem, who has it and why it matters now.>

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Topic compaction groups and retired stale ADR clauses so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>
