---
id: PLAN-verification-execution-ownership
spec: SPEC-verification-execution-ownership
---

# Technical Plan: `SPEC-verification-execution-ownership`

## 1. Architecture Overview & Impact

This changes agent guidance and its tests, with no Python runtime or feature-edge changes. Keep the general
executor contract of `CAP-HARN-isolated-execution`; clarify caller responsibilities in `CAP-HARN-agent-guidance`,
`CAP-DLV-delivery-workflows` and `CAP-DLV-test-management`. Record the cross-bundle responsibility choice in an
ADR without replacing the original executor decision, which already assigns direct Host launch.

## 2. Component Breakdown & Interface Contracts

- Scope the orchestration reference and completion link to the local-orchestrated Host after landing.
- Put native synchronous verification in the worker contract; payloads carry native checks, not the Host lifecycle.
- Apply the same boundary to maintenance recommendations and devkit AGENTS/testing guidance.
- Add a client guide with owner-qualified examples, native-command preservation and managed/manual upgrade steps.
- Test local/cloud rendered documents and worker projections; tests establish instructions, not live agent compliance.

## 3. Verification & Test Plan

Run relevant bundle regression tests, full required lint/types/rules and `just test-affected --base 5b5a6017` with
its full fallback. Run any necessary selected E2E natively and synchronously in this worktree. Do not use exec.
Host owns final landed verification. Commit required sync outputs after selected source-bundle changes.
