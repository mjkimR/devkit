---
id: PLAN-mcp-runtime-pending
spec: SPEC-mcp-runtime-pending
---

# Technical Plan: `SPEC-mcp-runtime-pending`

## 1. Constitution & Invariant Review

`ADR-remove-speculative-mcp-status-notice` authorizes revising the general-status clauses of `CAP-MCP-runtime-registration` and `CAP-DIST-sync-and-transactions`. The provider-free boundary and package layering of `ARCH-05-2-components` remain intact.

## 2. Architecture Overview & Impact

Remove the status import/call/notice assembly and its now-unused `registration_pending_notices` and `unregistered_hosts` helpers. Keep `_registration_pending` and `McpRegistrationPendingNotice`, because locked sync uses a real provider plan's `write` state. This deletes the sole general-status path to registration ledger/destination inspection without adding a substitute. Keep runtime warnings, provider failures and explicit registration operations unchanged.

## 6. Verification & Test Plan

AC-01 uses four fake provider outcomes with and without a receipt, asserting no provider load/probe/apply or ownership/destination inspection. AC-02 and AC-03 use actual registration planning and locked sync with fake outcomes, retaining existing refusal, provider-failure and registrations-only tests. AC-04 uses existing core/host/gate status regressions in the affected suite. AC-05 compares the three Living Spec targets.

Run focused registration/output tests, `just lint-check dist`, `just check dist`, `just test-affected` (retain its full fallback), `just test-dist`, and `uv run devkit rules check --ci --base main`. No build inputs change. Before/after is the deterministic pending-notice count named in the spec; no timing claim is made.
