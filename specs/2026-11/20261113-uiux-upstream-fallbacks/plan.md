---
id: PLAN-uiux-upstream-fallbacks
spec: SPEC-uiux-upstream-fallbacks
---

# Technical Plan: `SPEC-uiux-upstream-fallbacks`

## 1. Constitution & Invariant Review

None. Preserve `ADR-impeccable-question-relay`, `ADR-impeccable-session-authority` and
`ADR-uiux-task-approved-run`. This is one catalog bundle and capability area, with no runtime, package, layer,
dependency or feature-edge change. The three mitigations restate the existing capability's honest coverage and
consumer-authority limits for concrete upstream failures; they do not override an upstream check.

## 2. Architecture Overview & Impact

- Add one direct conditional read in the app-uiux-improve entry for Impeccable briefing and failure handling.
- Add references/impeccable-limits.md in the same skill with target evidence, actual capability/stop-condition brief
  fields, unsatisfied-probe fallback and installed-interface-first audit reporting.
- Leave the orchestration procedure intact: its file is already 12,280 of the allowed 12,288 bytes. A one-level
  entry-linked reference keeps conditional material out of every inline run without changing current safeguards.
- Strengthen existing bundle integration assertions and installed-wheel projection coverage; add no test tier.
- Reflect retained behavior in `CAP-DLV-uiux-improvement` and `UC-improve-an-interface-and-user-flow`.
- Update exactly the three Source feedback Dispositions after verification, recording local mitigation and the
  upstream-runtime limitation rather than claiming a fix.

## 3. Component & Interface Design

The entry reads the new reference when preparing an Impeccable brief or encountering detector, autonomy-probe or
audit-persistence limits. The reference remains local, one level deep, with no author-repository IDs or new command.
The actual installed upstream interface remains authoritative. A negative detector requires independent target
inspection; a required unavailable probe remains unsatisfied; unsupported persistence becomes report-only output.
All continuations keep the already selected task route and permissions.

## 6. Verification & Test Plan

- AC-01 to AC-04: focused integration file checks each mitigation and preserved boundaries, exact projected asset
  set and source-to-projection bytes. Measure baseline and changed instruction coverage for the three failures.
- AC-04: selected installed-consumer E2E builds real wheels and syncs the conditional reference without agt/docs/spec.
- AC-05: source-feedback status/Disposition inspection and workflow/source-feedback rules; no upstream send or trial.
- Native checks: `just lint-check devkit-catalog`, `just check devkit-catalog`,
  `just test-affected --base 5cab6156a60de1a2a2845e38fc19bda92961c90e --tier all`, and
  `uv run devkit rules check --ci --base a6872bf5ef7d99a10e8bc3799f88b615c03fd47e`.
- Run sync after source changes and record outputs. Run the medium initial independent code review; implement the
  Living Spec/reconcile and verify exact single-area semantic agreement. Repeat only checks affected by fixes.
- Source identity is each last work commit plus the recorded precommit tracked diff. No live upstream or host test
  is required, and instruction assertions establish no model or upstream-runtime guarantee.
