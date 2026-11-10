---
id: SPEC-delivery-document-hygiene
title: Split delivery contracts by responsibility and trim reference duplication
summary: Separate delivery role and proposal lifecycle contracts into focused capabilities while preserving every existing guarantee, and trim duplicate distribution reference text without changing behavior.
status: planned
created: 2026-11-10
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-delivery-document-hygiene] Split delivery contracts by responsibility and trim reference duplication

## 1. Problem Statement & Motivation

<Describe the problem, who has it and why it matters now.>

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Split delivery contracts by responsibility and trim reference duplication so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## Agreed intent

Split the delivery workflow role/worker contracts and proposal lifecycle execution contracts into focused
capabilities. Retain the existing capability IDs as useful entry points, preserve normative guarantees, error
contracts and history, repair current references and ADR traces, and trim duplicate distribution reference text.
Fix the duplicated Scenario 32 number without deleting acceptance scenarios. Do not shorten the sync capability,
consolidated ADR or completed specs solely to meet line budgets. No runtime or agent-asset behavior changes.
