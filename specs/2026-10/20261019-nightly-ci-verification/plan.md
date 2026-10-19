---
id: PLAN-nightly-ci-verification
spec: SPEC-nightly-ci-verification
---

# Technical Plan: `SPEC-nightly-ci-verification`

## 1. Constitution & Invariant Review

Record the lasting verification policy in `ADR-nightly-ci-verification`. No package layering or external API changes.

## 2. Architecture Overview & Impact

- `.github/workflows/nightly.yml` schedules the complete `ci.yml` with a cheap successful-head gate.
- `.github/scripts/nightly-ci.cjs` queries the latest successful wrapper run on the default branch through the Actions
  API (`actions: read`); emits `run_ci` for the dependent reusable CI job. The API error propagates.
- `.github/scripts/nightly-ci.test.cjs` uses Node's built-in test runner and a fake Actions client.
- Repository agent/development docs adopt affected-only local verification and explain the delayed discovery tradeoff.
- Shipped spec-plan/review/integrate instructions defer to repository verification policy and reuse valid results.
- No dependencies; Actions' existing Node runtime runs the gate.

## 3. Failure Modes

No previous success triggers full CI. Failed/cancelled runs do not advance the baseline. Read/API permission errors
fail the gate. Scheduled delays may postpone discovery; release full CI remains mandatory. Reverting the workflow
and guidance restores the previous policy; no persisted format changes.

## 4. Verification & Test Plan

- `node --test .github/scripts/nightly-ci.test.cjs`: unchanged/changed/first heads, failed predecessors, manual force,
  API errors and output/query wiring; parse workflow YAML and check reuse/release dependencies.
- `just test-affected` on the final content, `just lint-check`, `just check`, and cumulative governance checks.
- Independent medium code review and reconcile verification reuse results and request only missing/stale checks.
- No separate local full-suite run; selector full fallback remains authoritative.
