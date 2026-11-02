---
id: FB-pr-auto-admin-refusal-point
title: The PR route refuses --auto and --admin paths after approval, not before it
scope: repo
kind: question
category: docs-mismatch
target: ADR-local-and-pull-request-integration
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-02
---

# [FB-pr-auto-admin-refusal-point] The PR route refuses --auto and --admin paths after approval, not before it

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-adr-normative-outcomes` restated the GitHub adapter limits of `ADR-local-and-pull-request-integration`
  in `CAP-INT-mcp-services`.
- **Expectation**: The ADR says "any path that would need `--auto` or `--admin`" is refused before the confirmation.
- **Actual**: The code reaches these cases only after approval. Pending checks return `INTEGRATION_CHECKS_PENDING`, a
  merge that only an admin could make ends as `INTEGRATION_MERGE_REFUSED` at the merge call, and unreadable classic
  protection is disclosed, not refused.
- **Workaround (or Interpretation Chosen)**: `CAP-INT-mcp-services` states what the code does: the route MUST NOT
  enqueue, auto-merge or admin-merge. The ADR sentence was split into its own unmarked item.
- **Suggestion**: Decide whether the ADR's "before the confirmation" for these paths is retired through a new ADR, or
  whether the prepare step should detect and refuse them.

## Diagnostic Details

- **Reproduction**: Read the refusal points in the PR integration use case and repository adapter.
- **Expected / Actual**: Expected a refusal in prepare; observed a refusal at or after the merge call.
- **Versions**: base `fceda9d2`.
- **Conditions**: `pull_request` integration route through `gh`.
- **Workarounds Attempted**: The capability restates the code's behavior.
- **Related Assets**: `packages/devkit/src/devkit_agt/features/integration/usecases/pull_request.py` (lines 395-419),
  `packages/devkit/src/devkit_agt/features/worktree/repositories/pull_request.py` (lines 260-261),
  `CAP-INT-mcp-services`.

## Evidence

```text
ADR Decision Outcome: "Also refused before the confirmation: any path that would need `--auto` or `--admin`."
usecases/pull_request.py:395-407 returns INTEGRATION_CHECKS_PENDING after approval; 412-419 maps HTTP 403/405/409/422
from the merge call to INTEGRATION_MERGE_REFUSED.
```
