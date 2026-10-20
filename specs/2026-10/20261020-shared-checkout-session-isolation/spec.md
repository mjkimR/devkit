---
id: SPEC-shared-checkout-session-isolation
title: Non-blocking guidance for session branches in a shared checkout
summary: Adds concise guidance for --no-worktree branches in shared checkouts, leaving coordination to the direct user or local orchestration main agent without requiring worktrees or adding execution barriers.
status: in-progress
created: 2026-10-20
related_capabilities: [CAP-DLV-project-policy, CAP-WT-task-worktrees]
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-shared-checkout-session-isolation] Shared checkout session guidance

## 1. Problem Statement & Motivation

A branch switch in a shared checkout affects every session using that directory. Another session can therefore
commit to the task branch. Explain that limitation beside branch creation and assign coordination to the direct
user or local orchestration Host, preserving existing worktree and integration policy.

## 2. User Stories

- **US-1**: As an agent starting a session branch, I want to understand shared branch state and who coordinates it,
  so that I can choose a separate worktree when useful without assuming per-session isolation.

## 3. Non-Goals

- **Scope Excluded**: runtime notices, session detection, locks, additional approvals or refusals, mandatory
  worktrees for direct session tasks, foreign-commit detection and automatic mixed-branch recovery.

## 4. Acceptance Criteria & Behavioral Contracts

### Scenario 1: [AC-01] Shared branch state beside branch guidance
- **Given** the session branch guidance in git-policy.md and branch-only guidance in branches.md section 2,
- **When** an agent reads how to use `start --no-worktree`,
- **Then** both explain that switching branches changes the branch seen by every session in that directory and
  another session can commit to the checked-out task branch.

### Scenario 2: [AC-02] Coordination and isolation boundaries
- **Given** `CAP-DLV-project-policy` section 3 item 6 and `CAP-WT-task-worktrees` section 2a,
- **When** their shared-checkout guidance is read together with the two skill references,
- **Then** the direct user coordinates shared sessions and the local orchestration Host coordinates workers;
  workers still use worktrees, while a separate worktree remains an option for a direct session task.

### Scenario 3: [AC-03] Existing policy preserved
- **Given** the approved documentation-only scope,
- **When** the final diff is reviewed,
- **Then** only the four specified documents and this spec bundle change, without changing policy levels,
  command output, integration checks or approval requirements.

### Scenario 4: [AC-04] Verification
- **Given** the final documentation diff,
- **When** path and cumulative governance checks, lint, types and `just test-affected` run,
- **Then** all selected checks pass; no new test is added for this wording-only clarification.

## 5. Assumptions and Source Feedback

The four target paths and existing policy still match the accepted proposal at handoff. This clarifies existing
Git behavior and responsibility, so no ADR or production-code change is needed. Development effort is low.
`FB-no-worktree-session-branch-shared-checkout` is terminal promoted provenance; it needs no update or completion check.
