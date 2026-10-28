---
id: PLAN-worker-inspection-fixes
spec: SPEC-worker-inspection-fixes
---

# Worker inspection fix plan

## 1. Constitution & Invariant Review

No invariant changes. The existing read-only worker inspection contract in `CAP-DLV-delivery-workflows` retains its scope, stage and verdict semantics.

## 2. Architecture Overview & Impact

Worker input derivation skips absent optional reconcile only. Reuse derive_base with an empty worker list to resolve cumulative rules from the recorded branch/base checkout; audit derivation is unchanged. The use case adds rules_base; the CLI adds --rules-base and existing INPUT sentinels show provenance. No dependencies change.

## 3. Component & Interface Design

`InspectWorkerUseCase.execute(..., rules_base: str | None = None)` forwards the optional CLI value. `inputs.rules_base` carries resolved commit value and source (argument, branch-merge-base, or audit-base-fallback), independently of `inputs.base`; top-level rules_base names the rules command comparison commit. An explicit fallback applies only without a recorded branch or base-checkout branch. Invalid references remain invocation errors. No scope or ancestry behavior changes.

## 6. Verification & Test Plan

Permanent Red/Green integration tests cover optional/invalid reconcile and earlier-turn targets under separate bases. Existing dirty, stale and outside-scope tests remain. Test explicit overrides, invalid references, manual fallback, first-turn equality and compact/full/text evidence. Run just test-affected, lint/check for spec, sync check and cumulative governance. The initial Red run measures the recorded baseline before any production edit.
