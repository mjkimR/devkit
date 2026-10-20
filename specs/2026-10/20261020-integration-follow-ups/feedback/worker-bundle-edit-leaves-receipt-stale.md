---
id: FB-worker-bundle-edit-leaves-receipt-stale
title: A development worker that edits bundle assets cannot re-sync the receipt
scope: repo
kind: friction
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundle/subagents/development-worker.md (write boundaries, `.devkit/` denied)
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-20
---

# [FB-worker-bundle-edit-leaves-receipt-stale] A development worker that edits bundle assets cannot re-sync the receipt

## 1. Friction / Question (friction, question)

- **Context**: Development of SPEC-integration-follow-ups edited three devkit-spec bundle skill files
  (`spec-integrate/SKILL.md`, `spec/references/completion.md`, `spec/references/worktree.md`) inside the task boundary.
- **Expectation**: The worker commits a complete result; in this repository a commit that changes bundle assets also
  carries the re-synced `.devkit/installation.json` (its asset hashes).
- **Actual**: `devkit sync --check` reports `.devkit/installation.json` and the managed copies as changed, but the
  development-worker contract denies `.devkit/` as a write path, so the receipt stays stale. The commit gate and
  `devkit rules check --ci` accept the stale receipt, so nothing flags it before integration.
- **Workaround (or Interpretation Chosen)**: Left the receipt unchanged and handed the `devkit sync` to the Host in the
  reconcile record and the worker report.
- **Suggestion**: Either allow the worker to write the tracked receipt (`.devkit/installation.json`) when its task
  boundary includes bundle assets, as a named exception to the `.devkit/` denial, or have the Host's integration
  procedure (`spec-integrate`) state the re-sync step explicitly.

## Diagnostic Details

- **Reproduction**: edit a file under `packages/devkit-spec/src/devkit_spec/bundle/skills/`, then run `devkit sync --check`.
- **Expected / Actual**: a way to commit the matching receipt / the receipt is outside the write scope.
- **Versions**: unknown (worktree head of this unit).
- **Conditions**: native Claude Code development-worker in a task worktree.

## Evidence

```text
$ uv run devkit sync --check
[CHANGE: update .devkit/managed/spec/skills/spec-integrate/SKILL.md]
[CHANGE: update .devkit/installation.json]
development-worker.md, Write boundaries: "Denied: anything outside the worktree, ..., `.devkit/`, ..."
```

## Resolution

Directly resolved by `SPEC-worker-guidance-and-fixtures`: spec-integrate assigns official sync and receipt preparation to the Host after base incorporation and before final checks/approval, with base projection sync after landing.

Verification: Independent medium code review confirmed AC-03. This verifies the guidance fix; this worker does not claim Host synchronization has already executed.
