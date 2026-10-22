---
id: SPEC-merge-not-ff-auto
title: Auto advisory mode for WORKTREE_MERGE_NOT_FF
summary: Set actor to Actor.TOOL for MergeNotFastForwardError so AAP derives AUTO mode, allowing agents to absorb routine target advances autonomously without unnecessary user interruptions.
status: in-progress
created: 2026-10-22
related_capabilities:
  - CAP-WT-task-worktrees
  - CAP-INT-mcp-services
related_usecases:
  - UC-run-parallel-work-safely
workflow: sdd-spec-feature
---

# [SPEC-merge-not-ff-auto] Auto advisory mode for WORKTREE_MERGE_NOT_FF

## 1. Problem Statement & Motivation

When integrating development units under `dev-integration=auto` or requesting `spec_plan_accept` for planning branches while the base branch has advanced, `integration_integrate` and `finish --merge` refuse with `WORKTREE_MERGE_NOT_FF` (`FB-merge-not-ff-asks-the-user`).

Previously, `MergeNotFastForwardError` subclassed `_Interaction` (`actor = Actor.USER`), causing the Agent Advisory Protocol to assign `mode = ActionMode.INTERACTION` ("Stop and ask the user. Do not retry"). However, merging the moved base into the task branch is the documented first step of `spec-integrate` ("Merge the base, never rebase ... repeat after an integration refused on a later target"). Stopping to ask the user on every routine base advance introduces unnecessary friction during active multi-unit development.

## 2. Source Feedback

- [FB-merge-not-ff-asks-the-user]: WORKTREE_MERGE_NOT_FF asks the user to approve the routine base merge.

## 3. User Stories

- **US-1**: As an AI coding agent integrating an approved branch, I want `WORKTREE_MERGE_NOT_FF` to give an `AUTO` directive so that I can autonomously merge the moved base into the task worktree, re-verify, and retry the integration without interrupting the user.
- **US-2**: As a developer/user, I want actual merge conflicts to remain `INTERACTION` (`WORKTREE_MERGE_CONFLICT`) so that I am only interrupted when a genuine design choice or manual resolution is required.

## 4. Non-Goals

1. **Scope Excluded**: Silently performing 3-way merges inside the integration command without raising an error. Scope Excluded: `spec-integrate` requires re-verifying the merged result before landing on the base.
2. **Scope Excluded**: Changing the advisory mode of `MergeConflictError` (`WORKTREE_MERGE_CONFLICT`), which must remain `INTERACTION`.

## 5. Acceptance Criteria & Behavioral Contracts

### [AC-01] MergeNotFastForwardError actor is Actor.TOOL
- **Given** an activity branch that lags behind the base branch HEAD
- **When** `finish(..., merge=True)` or `plan_finish(...)` raises `MergeNotFastForwardError`
- **Then** `error.actor` is `Actor.TOOL` and `error.mode` derives to `ActionMode.AUTO`.

### [AC-02] Advisory rendering emits AUTO action directive
- **Given** a `WORKTREE_MERGE_NOT_FF` refusal rendered to stderr or reported in advisory JSON
- **When** the error is formatted by devkit CLI or MCP
- **Then** `[ACTION]` begins with `AUTO — Run the [FIX] command once, then retry the operation once.` and `mode` is `"AUTO"`.

### [AC-03] Fix instruction preserves SHA-safe merge guidance
- **Given** `MergeNotFastForwardError.fix`
- **When** inspecting the fix instruction
- **Then** it instructs merging the target branch into the task branch in its worktree without rebasing.

### [AC-04] Living Spec documents ERROR (AUTO) mode for WORKTREE_MERGE_NOT_FF
- **Given** `CAP-WT-task-worktrees` and reference documentation
- **When** inspecting the `WORKTREE_MERGE_NOT_FF` error description
- **Then** the advisory level and mode are documented as `ERROR (AUTO)`.
