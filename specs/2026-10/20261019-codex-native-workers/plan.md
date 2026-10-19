---
id: PLAN-codex-native-workers
spec: SPEC-codex-native-workers
---

# Technical Plan: `SPEC-codex-native-workers`

## 1. Constitution & Invariant Review

None. `ADR-codex-native-worker-execution` authorizes the support contract while preserving
`ADR-worker-delivers-committed-result` and `CAP-DLV-delivery-workflows`. No renderer, runtime, schema or host setting
changes are required. The handoff's paths, interfaces and constraints match the inspected base.

## 2. Architecture Overview & Impact

- Worker contracts: Codex metadata and common worktree/approval/failure procedure (AC-01, AC-03, AC-04).
- `spec-delegate` and references: named/generic invocation, trust restrictions, capability fallback, payload and
  cumulative validation (AC-02 through AC-05). Keep detail in references within existing skill budgets.
- `spec-orchestrate` and worker records: pre-start capabilities and honest partial returns (AC-02, AC-04, AC-05).
- Role tests: parse the actual contracts and render actual projections; verify instruction branches and unchanged
  other-host metadata (AC-01 through AC-05).
- `CAP-DLV-delivery-workflows` and sync receipt: current behavior, limits and normal deployment.
- New dependencies: none. Existing distribution rendering stays read-only and authoritative.

## 3. Failure Modes

Unavailable role and explicit trust restrictions are separate conditions. Required missing capabilities stop
spawning; existing preferred/direct policy applies. Refused approval stops that operation; preservation is a
separately permitted operation. A failed record/commit produces an honest failed return and Host blocking rather
than a fabricated committed success. Only gate refusal retains the emergency bypass exception.

## 4. Verification & Test Plan

Run `just lint-check devkit-spec`, `just check devkit-spec`, targeted role/projection tests and bundle budgets;
run governance checks, normal `devkit sync`, status and sync-check. Run consumer smoke once for packaging/CLI/bundle
effects. A fresh nested code-reviewer and an independent reconcile-reviewer verify the medium-effort result.
The Host runs `just test` once on the reviewed final HEAD before integration; this worker does not claim that pass.
No unsafe live denial experiment is needed. Keep source sync and its receipt together in normal gated commits.
