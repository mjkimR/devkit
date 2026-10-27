---
id: FB-integration-reissues-merge-after-unknown-outcome
title: Integration CLI reissues a merge after an unknown outcome and ignores a closed pending PR
scope: repo
kind: friction
category: tool-error
target: devkit integration integrate (devkit_agt.features.integration usecases service and pull_request)
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-27
---

# [FB-integration-reissues-merge-after-unknown-outcome] Integration CLI reissues a merge after an unknown outcome and ignores a closed pending PR

## 1. Friction / Question (friction, question)

- **Context**: The review-refactor run removed the MCP-native integration path (`resume`, in-process `_records`
  retention). Its tests were moved to the CLI path (`prepare` + `execute_cli` with a digest), where every invocation
  is a fresh process.
- **Expectation**: An integration whose pull-request merge outcome was unknown is not merged twice, and a pending PR
  that was closed meanwhile is refused (`CAP-INT-mcp-services`).
- **Actual**: On a fresh CLI invocation after an unknown merge outcome, the fake GitHub provider recorded a second
  merge call while the PR stayed open; a closed pending PR is not refused on a fresh call. Only the removed
  in-process retention prevented these; the CLI never had it.
- **Workaround (or Interpretation Chosen)**: None in code; the pre-existing CLI behavior is unchanged by the
  refactor and recorded here.
- **Suggestion**: Persist the integration request's merge attempt (PR number, head, merge call issued) in the
  integration receipt or a clone-local record, and have a fresh `integrate` reconcile against the PR state (merged,
  closed, still open) before issuing a merge.

## Diagnostic Details

- **Reproduction**: `packages/devkit/tests/integration/features/integration/test_pull_request.py` fake provider: an
  unknown merge outcome followed by a fresh `execute_cli` call; `merge_calls == 2`.
- **Expected / Actual**: expected one merge call or a refusal; actual a second merge call.
- **Versions**: branch `dev-review-refactor`.
- **Conditions**: pull-request route; GitHub returns an indeterminate merge result (timeout or 5xx).
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `CAP-INT-mcp-services`, `ADR-host-cli-lifecycle-authority`,
  `docs/materials/2026-10/20261027-review-refactor-code-pass/report.md`.

## Evidence

```text
Change B1 subagent report: "After an unknown PR merge outcome, a fresh CLI call issues the merge again:
the fake recorded merge_calls == 2 while the PR stayed open." "A closed pending PR is not refused on a fresh call."
```
