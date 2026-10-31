---
id: FB-compacted-worktree-dismissed
title: Worktree feedback, dismissed
summary: Task worktree management and environment isolation.
target: docs/capabilities/worktree/
status: dismissed
created_at: 2026-10-31
aliases:
  - FB-handoff-ordering-dependency-unchecked
  - FB-native-worker-command-scoped-approvals
  - FB-shared-agent-invocation-constant
  - FB-sync-locked-leaves-check-failing
---

# [FB-compacted-worktree-dismissed] Worktree feedback, dismissed

## FB-handoff-ordering-dependency-unchecked

- **Symptom**: An accepted proposal's ordering dependency on another repository is not checked before Development starts
- **Response**: Dismissed
- **Reason**: cross-repository coordination belongs to the Host's judgment for the particular task. No general repository-external prerequisite inspection, new worker instruction or automated gate is needed. Explicit dependencies in an agreed task still matter; this disposition declines a universal procedure rather than authorizing agents to ignore those dependencies.

## FB-native-worker-command-scoped-approvals

- **Symptom**: Native Codex worker completes sibling-worktree mutations through command-scoped approvals
- **Response**: Dismissed outcome
- **Reason**: dismissed. The observation records experimental spike evidence regarding native subagent execution across sibling worktrees in Codex. Host-level support for persistent scoped worktree access is an upstream Codex platform capability, not a devkit repository defect.

## FB-shared-agent-invocation-constant

- **Symptom**: The uv run devkit prefix is defined per package
- **Response**: Dismissed by the user's decision
- **Reason**: `devkit_dist.features.project.models.invocation` provides the shared constant and helper, and gate and workflow use the helper. The separate constant in `devkit_spec.base.errors` preserves the base-to-feature import boundary; `test_the_agent_invocation_matches_devkit_dist` checks its equality with the shared constant. Remaining literal duplication alone does not justify this follow-up.

## FB-sync-locked-leaves-check-failing

- **Symptom**: sync --locked in a fresh checkout leaves sync --check failing
- **Response**: Dismissed by the user's decision
- **Reason**: `CAP-MCP-runtime-registration` and `CAP-DIST-sync-and-transactions` intentionally leave real registration writes pending during locked restoration. A normal sync check includes those actual writes, so this observation does not establish a product defect. Explicit `uv run devkit sync --registrations-only` completes registration when a fresh checkout requires it; no change to locked behavior or new diagnostic mechanism is needed.
