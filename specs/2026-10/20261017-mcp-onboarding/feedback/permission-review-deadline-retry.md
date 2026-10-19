---
id: FB-permission-review-deadline-retry
title: Automatic permission review deadlines interrupted local verification
scope: upstream
kind: friction
category: tool-error
target: Codex exec_command automatic permission approval review
skill: spec-review
agent: codex
origin: agent
severity: workaround
recurring: true
status: dismissed
created_at: 2026-10-17
---

# [FB-permission-review-deadline-retry] Automatic permission review deadlines interrupted local verification

## 1. Friction / Question

- **Context**: Verifying an approved feature in a policy-required linked worktree outside the default writable root.
- **Expectation**: An escalated verification request should return an approval decision or a promptly actionable failure.
- **Actual**: Automatic permission review timed out for a validation/commit request and a consumer smoke request.
  The diagnostic stated that the timeout did not establish that the action was unsafe and allowed one retry.
- **Workaround**: Inspected repository state to establish which operations ran, then retried bounded commands.
  Validation, commits and smoke completed successfully without changing the implementation scope.
- **Suggestion**: Preserve a clear distinction between a rejected action and an approval-review timeout, and surface
  whether the requested process started so callers can safely resume work without redundant confirmation.

## Diagnostic Details

- **Reproduction**: Observed two escalated exec requests during local validation; no synthetic reproduction attempted.
- **Expected / Actual**: A completed approval decision was expected; the tool returned a review-deadline error.
- **Versions**: Codex backend/reviewer version unknown; repository Python packages do not own the approval service.
- **Conditions**: Workspace-write sandbox, automatic approval reviewer, task worktree outside the base writable root.
- **Workarounds Attempted**: Read-only Git state inspection and allowed retries; checks and commits subsequently succeeded.
- **Related Assets**: exec_command, automatic permission review, and the spec worktree procedure.

## Evidence

```text
Two exec requests returned: automatic permission approval review did not finish before its deadline.
The diagnostic allowed one retry and said timeout alone does not imply an unsafe action.
Subsequent commands completed lint/type/governance checks, feature commits and consumer smoke.
```

- **Disposition**: dismissed. The observation concerns intermittent deadline timeouts in the external OpenAI Codex automatic permission approval review service during exec calls. devkit repository packages do not operate the external approval review backend.

