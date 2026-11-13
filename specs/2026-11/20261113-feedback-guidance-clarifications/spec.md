---
id: SPEC-feedback-guidance-clarifications
title: Clarify feedback-driven authoring guidance
summary: Clarify existing review evidence, commit timing, UX closure and project style-source procedures without adding verdicts or CLI mechanisms.
status: planned
created: 2026-11-13
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-feedback-guidance-clarifications] Clarify feedback-driven authoring guidance

## 1. Problem Statement & Motivation

<Describe the problem, who has it and why it matters now.>

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Clarify feedback-driven authoring guidance so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## Agreed scope

Clarify existing procedures for the five named sources. Preserve PASS/FAIL/SKIP, current task-coverage and commit boundaries, optional UX review and its two independent review rounds. Name build-verify for implementer closure and show how draft-fixed findings are reported there. Add no CLI, schema, new mandatory style file or preset. Explain existing resolved/waived finding fields in a new reconcile-check, preserving whole-round verification and non-waivable contract mismatches. Show source envelope and exact SHA for checks the reviewer did not rerun.

## Source feedback

- `FB-reconcile-check-no-per-finding-closure`: closing-record example using existing fields.
- `FB-envelope-check-status-vocabulary`: SKIP provenance example without a new verdict.
- `FB-specify-task-coverage-before-tasks`: complete Screens-to-plan/tasks commit sequence.
- `FB-ux-review-closure-stage-unnamed`: closing stage and previously folded findings.
- `FB-ux-writing-missing-style-file`: project-owned style source fallback within authorized scope.

The user selected direct fixes through spec/feedback-hygiene. Resolve only these five sources after implementation and verification; do not alter terminal or unrelated feedback. No dependencies on another active Unit are declared.
