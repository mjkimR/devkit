---
id: FB-compacted-gate-promoted
title: Gate feedback, promoted
summary: Git commit gates, hooks, and lifecycle checks.
target: docs/capabilities/gate/
status: promoted
created_at: 2026-10-31
aliases:
  - FB-commit-gate-runs-no-rules-check
  - FB-projected-roles-need-a-session-in-the-project
  - FB-read-only-review-context-lock
  - FB-skill-budget-headroom
  - FB-worktree-sync-repoints-the-hook-interpreter
---

# [FB-compacted-gate-promoted] Gate feedback, promoted

## FB-commit-gate-runs-no-rules-check

- **Symptom**: The commit gate runs no spec rules here, so an error-severity violation was committed
- **Response**: `SPEC-commit-gate-rules-default` with devkit `707aa54` and `bc14046`
- **Reason**: devkit's built-in `rules-check` gate runs the rules on every commit by default, and this repository pins that devkit.

## FB-projected-roles-need-a-session-in-the-project

- **Symptom**: Projected role agents are unavailable when the host session is rooted outside the project
- **Response**: S-Lane
- **Reason**: `spec-delegate/references/hosts.md` states the session-root condition and the emulated fallback; `SPEC-codex-native-workers` covers role loading for workers.

## FB-read-only-review-context-lock

- **Symptom**: Required context loading attempts to write a transient lock during read-only review
- **Response**: packages/devkit-dist/src/devkit/distribution/installation/transaction.py
- **Reason**: a reader that cannot create or open the lock on a read-only file system reads without it; writers still fail

## FB-skill-budget-headroom

- **Symptom**: spec-delegate and spec skills sit at the 8192-byte budget
- **Response**: `SPEC-subagent-procedure-in-contract` (AC-08)
- **Reason**: `spec-delegate` and `spec` restructured with the skill-authoring playbook to 7418 and 7677 bytes, guarded by `tests/test_bundle_budgets.py`.

## FB-worktree-sync-repoints-the-hook-interpreter

- **Symptom**: devkit sync in a task worktree points the shared hooks' fallback interpreter at that worktree
- **Response**: `SPEC-hygiene-reliability`
- **Reason**: Automatic sync retains each valid shared fallback; explicit installs select a replacement interpreter.
