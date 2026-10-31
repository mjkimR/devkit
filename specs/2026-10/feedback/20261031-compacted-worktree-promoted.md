---
id: FB-compacted-worktree-promoted
title: Worktree feedback, promoted
summary: Task worktree management and environment isolation.
target: docs/capabilities/worktree/
status: promoted
created_at: 2026-10-31
aliases:
  - FB-fresh-worktree-environment-bootstrap
  - FB-gate-answers-carry-conversation-transcripts
  - FB-no-worktree-session-branch-shared-checkout
  - FB-policy-change-in-a-task-branch
  - FB-pr-remote-and-squash-integration
---

# [FB-compacted-worktree-promoted] Worktree feedback, promoted

## FB-fresh-worktree-environment-bootstrap

- **Symptom**: Fresh worktree has synchronized assets but no runnable project environment
- **Response**: .devkit/config.toml
- **Reason**: `[worktree] setup = "just init"` provisions the workspace environment (`uv sync --no-active --all-packages`) in every new task worktree before its first devkit command.

## FB-gate-answers-carry-conversation-transcripts

- **Symptom**: Gate answers and assumptions carry conversation transcripts instead of a user flag
- **Response**: S-Lane `f116d59` (`src/devkit_spec/bundle/AGENTS.md`, `skills/spec/SKILL.md`, `skills/spec-next/references/workflow-signals.md`, `skills/spec/references/worktree.md`, workflows, `CAP-DLV-delivery-workflows`, `ARCH-06-runtime-view`)
- **Reason**: records name the authority (`--by user`) and carry no conversation, following authority-only reporting.

## FB-no-worktree-session-branch-shared-checkout

- **Symptom**: A --no-worktree session branch in the shared base checkout picked up another session's commit
- **Response**: `SPEC-shared-checkout-session-isolation`
- **Reason**: brief documentation guidance only. Direct users and local orchestration main agents own checkout coordination; mandatory worktrees and additional execution barriers and unconditional runtime notices are excluded.

## FB-policy-change-in-a-task-branch

- **Symptom**: A Git policy change made in a task branch does not govern that task's finish
- **Response**: src/devkit_spec/bundle/skills/spec/references/worktree.md
- **Reason**: S-Lane; policy is read in the base, so a policy change lands there first

## FB-pr-remote-and-squash-integration

- **Symptom**: Extend integration service and worktree cleanup for PR remote operations and squash/rebase merges
- **Response**: `SPEC-integration-pull-request-cleanup`
- **Reason**: remote/PR authority and cleanup after a no-ff merge, preserving source SHAs. Squash/rebase support is excluded from the promoted scope.
