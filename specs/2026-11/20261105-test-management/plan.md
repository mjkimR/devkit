---
id: PLAN-test-management
spec: SPEC-test-management
---

# Technical Plan: test management

## 1. Constitution & Invariant Review

None of the architecture or accepted policy invariants change. Preserve `ARCH-05-2-components`,
`ADR-post-merge-verification`, `CAP-DLV-performance-pass` and `CAP-DLV-maintenance-history`.

## 2. Architecture Overview & Impact

Implement `SPEC-test-management` as content in the maintenance catalog bundle: one router and two conditional
references, manifest registration and testing preset. Existing selection/deployment/retrieval APIs suffice.
Update existing integration tests and catalog README. No runtime code, new package/layer/test tier or dependency
edge is introduced. Consumer changes remain separately authorized work.

## 6. Verification & Test Plan

Extend actual sync/search/retrieval integration tests for all/testing, existing presets and unselected consumers.
Check reference resolution, self-containment and byte budgets. Record expected/observed walkthrough actions for
prerequisite ordering, unattended decisions, the three repositories, a non-pytest example and inconclusive tuning.
Run `just test-affected --base 297f727d`, `just lint-check catalog`, `just check catalog` and rules. Existing
Planning evidence is context only; no application-suite or performance claim is made.
