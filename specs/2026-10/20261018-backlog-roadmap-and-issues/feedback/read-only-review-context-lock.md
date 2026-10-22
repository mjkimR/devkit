---
id: FB-read-only-review-context-lock
title: Required context loading attempts to write a transient lock during read-only review
scope: repo
kind: friction
category: instruction-conflict
target: devkit get-context and spec-delegate read-only support-role bootstrap
origin: agent
severity: workaround
recurring: true
status: promoted
created_at: 2026-10-18
---

# [FB-read-only-review-context-lock] Required context loading attempts to write a transient lock during read-only review

## 1. Friction / Question

- **Context**: An isolated code-reviewer must read the spec constitution while remaining read-only in a linked worktree.
- **Expectation**: Mandatory context bootstrap for a read-only role can read the installed guidance without changing repository state.
- **Actual**: get-context attempted to create .devkit/transient/lock and failed with a read-only filesystem error. The reviewer reported the same bootstrap limitation; a direct restricted-shell reproduction returned UNEXPECTED_ERROR.
- **Workaround**: Read the managed constitution and relevant instruction files directly. Review and independent reconciliation completed without granting the reviewers write access.
- **Suggestion**: Document a supported filesystem-only bootstrap for read-only roles, or let informational context reads avoid creating a writable transient lock. This is a separate tooling concern; the Backlog implementation needs no permission expansion.

## Diagnostic Details

- **Reproduction**: Run devkit get-context spec -w <worktree> with the worktree readable but not writable.
- **Expected / Actual**: Expected the installed constitution and instruction headers; actual UNEXPECTED_ERROR with OSError errno 30 while creating <worktree>/.devkit/transient/lock.
- **Versions**: devkit-agt 0.1.1, devkit-spec 0.1.0; feature review head 90c0012.
- **Conditions**: Codex workspace-write session, sibling linked worktree outside the default writable root, support roles constrained to read-only commands.
- **Workarounds Attempted**: Avoiding uv synchronization/cache writes did not remove the repository lock requirement. Direct managed-file reads succeeded.
- **Related Assets**: packages/devkit/src/devkit/distribution/cli/__init__.py, spec-delegate role bootstrap and the spec constitution context-first instruction.

## Evidence

```text
Required context bootstrap: devkit get-context spec once per agent context.
Code-reviewer reported a transient-lock creation failure under read-only restrictions.
Direct restricted invocation returned code UNEXPECTED_ERROR and OSError errno 30 for <worktree>/.devkit/transient/lock.
Managed spec/AGENTS.md and relevant instruction files remained readable and supported the review.
```

- **Disposition**: packages/devkit-dist/src/devkit/distribution/installation/transaction.py: a reader that cannot create or open the lock on a read-only file system reads without it; writers still fail
