---
id: SPEC-conditional-proposal-prune
title: Plan proposal cleanup only when applicable
summary: Omit inapplicable proposal-prune effects for spec-only units while preserving exact prepared cleanup identity and retry validation.
status: planned
created: 2026-11-13
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-conditional-proposal-prune] Plan proposal cleanup only when applicable

## 1. Problem Statement & Motivation

<Describe the problem, who has it and why it matters now.>

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Plan proposal cleanup only when applicable so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## Agreed scope

Omit the proposal-prune cleanup target for spec-only activity with no applicable proposal cleanup. Keep it for real proposal handoff/empty-directory cleanup. Preserve exact scope/digest, source/target revision validation and cleanup retry identity across landing; use stable committed/request evidence rather than a filesystem-only predicate that changes after merge. Keep other scope/branch/worktree cleanup and all refusal checks. This is an output/applicability improvement, not a new cleanup mechanism or weakened approval.

## Source feedback

- `FB-integration-prune-without-proposal`: plan only applicable proposal cleanup.

The user selected a direct fix through spec/feedback-hygiene. Resolve this source only after implementation and verification. No dependencies on another active Unit are declared.
