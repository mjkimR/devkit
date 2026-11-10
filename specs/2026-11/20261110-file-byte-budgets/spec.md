---
id: SPEC-file-byte-budgets
title: Measure file hygiene budgets in bytes
summary: Replace line-count hygiene budgets with raw byte budgets, retaining the rule ID, warning phase and consolidated-record eligibility while migrating settings and current guidance.
status: planned
created: 2026-11-10
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-file-byte-budgets] Measure file hygiene budgets in bytes

## 1. Problem Statement & Motivation

<Describe the problem, who has it and why it matters now.>

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Measure file hygiene budgets in bytes so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## Agreed intent

Replace the line-based RULE-file-length hygiene metric entirely with raw file byte counts read through the
snapshot-aware cache. Keep the stable rule ID, extension/path targeting and warning-only hygiene phase. Use a
49,152-byte default, a 65,536-byte repository CAP override and a 65,536-byte optional repository consolidated
record budget with unchanged alias eligibility and max precedence. Replace max_lines and consolidated_max_lines
with max_bytes and consolidated_max_bytes; old keys fail the existing typed settings validation without silent
conversion. Make file-level warnings report actual and selected limit bytes at line 1. Migrate current settings,
examples, playbooks and tests. Add an ADR partially superseding the metric/setting/repository-threshold clauses of
ADR-consolidated-record-budgets while retaining its eligibility and pure settings-resolution decisions. Historical
completed specs and old decision outcome text remain history; add the matching partial pointer. No hard gate,
tokenizer, automatic splitting, generic rule-engine redesign or change to file ownership.
