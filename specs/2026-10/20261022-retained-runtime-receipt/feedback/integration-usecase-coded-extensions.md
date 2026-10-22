---
id: FB-integration-usecase-coded-extensions
title: The integration use case names few of the executor's coded refusals and their recoveries
scope: repo
kind: suggestion
category: spec-ambiguity
target: UC-drive-development-to-integration
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-integration-usecase-coded-extensions] The integration use case names few of the executor's coded refusals and their recoveries

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `UC-drive-development-to-integration` lists some coded extensions at steps 7 and 8
  (`WORKTREE_PR_POLICY`, `WORKTREE_BLOCKED`, `INTEGRATION_TARGET_MOVED`) but leaves other executor refusals with a
  distinct recovery to `CAP-INT-mcp-services`: `INTEGRATION_NOT_READY`, `INTEGRATION_RECEIPT_CONFLICT`, and now
  `INTEGRATION_RECEIPT_READER_CHANGED` (CLI route from the source's code under separate authority; restarting does
  not help) and `MCP_RUNTIME_STALE` (restart or reconnect the retained service).
- **Proposed Procedure**: add step-7 extensions for the refusals whose recovery differs from "resolve and integrate
  again", each citing `CAP-INT-mcp-services` or `CAP-MCP-runtime-registration`, or state in the use case that coded
  executor refusals are listed in the capability.
- **Expected Benefit**: a Host following the use case finds the recovery of a refusal without searching the
  capability, and does not try a restart or a conversational approval where neither applies.
- **Cost & Risk**: a longer use case that must track new codes; stating the delegation to the capability avoids that.
- **Attempted**: hypothesis; raised as a P3 by the reconcile check of `SPEC-retained-runtime-receipt` and waived
  there because `docs/usecases/` was outside that development turn's write scope.

## Evidence

- `SPEC-retained-runtime-receipt` envelope `reconcile-check-01.yaml`: the use case's extensions at step 7 omit the two
  new codes; its steps and postconditions stay correct.

## Disposition

- **Disposition (resolved)**: `SPEC-superseded-reference-cleanup` adds extensions 7f (`INTEGRATION_RECEIPT_READER_CHANGED`: a
  restart does not help; the CLI route from the source's code under separately granted authority) and 7g
  (`MCP_RUNTIME_STALE`: restart or reconnect the retained service) with scenarios 17 and 18 to
  `UC-drive-development-to-integration`, and states that the coded executor refusals it does not name are listed in
  `CAP-INT-mcp-services`. Verified against both capabilities in its `reconcile.md`, `devkit rules check` and the
  `reconcile-check` envelope.
