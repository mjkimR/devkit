---
id: FB-mcp-registration-pending-ignores-runtime
title: MCP_REGISTRATION_PENDING repeats when the MCP runtime is unavailable
scope: repo
kind: suggestion
category: tool-error
target: devkit_dist.features.host.usecases.registrations.unregistered_hosts; devkit status
origin: agent
severity: noise
recurring: false
status: promoted
created_at: 2026-10-27
---

# [FB-mcp-registration-pending-ignores-runtime] MCP_REGISTRATION_PENDING repeats when the MCP runtime is unavailable

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `unregistered_hosts` reports every eligible host without a matching ledger entry and never
  loads the registration provider, so it cannot tell that the retained MCP runtime is unavailable. `devkit status`
  then emits `MCP_REGISTRATION_PENDING` on every run, while its `[FIX]` (`uv run devkit sync --registrations-only`)
  only produces `MCP_RUNTIME_UNAVAILABLE`; `plan()` classes the same host as `runtime-unavailable`.
- **Proposed Procedure**: record the runtime-unavailable outcome of the last registration attempt in the local
  ledger, and have `unregistered_hosts` skip hosts whose last attempt found no runtime (or emit the runtime notice
  instead of the pending one).
- **Expected Benefit**: no repeated notice an agent cannot clear.
- **Cost & Risk**: a ledger field; must not hide a later fixable state.
- **Attempted**: hypothesis; found in the onboarding-polish review.

## Diagnostic Details

- **Reproduction**: devkit-mcp installed without a retained runtime; `uv run devkit status` repeats the notice.
- **Expected / Actual**: expected the runtime problem once; actual a pending notice on every run.
- **Versions**: branch `dev-onboarding-polish`.
- **Conditions**: provider installed, runtime missing.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `CAP-MCP-runtime-registration`, `docs/development/reference/distribution.md`.

## Evidence

```text
status notices: MCP_REGISTRATION_PENDING (every run); sync --registrations-only: MCP_RUNTIME_UNAVAILABLE
```

## Disposition

- **Disposition**: `SPEC-mcp-runtime-pending`: promoted by the user's decision for Planning of the recorded behavior and its contract constraints.
