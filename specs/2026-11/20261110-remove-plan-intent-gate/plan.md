---
id: PLAN-remove-plan-intent-gate
spec: SPEC-remove-plan-intent-gate
---

# Technical Plan: `SPEC-remove-plan-intent-gate`

## 1. Constitution & Invariant Review

`ADR-remove-plan-intent-gate` replaces the identified gate-dependent clauses while preserving other authority.
The generic workflow engine in devkit-agt is unchanged. No new dependency, storage schema or feature edge is needed.

## 2. Architecture Overview & Impact

- Bundle definitions keep intent stage IDs/checks and remove their human gate declarations.
- Proposal acceptance drops its missing-intent special case. Handoff selects only plan-accept records.
- Delivery handoff requires completed plan-accept, not plan-intent.
- Policy inspection omits the retired key, warns through SPEC_APPROVAL_KEY_IGNORED and retains custom gates.
- Skills, constitution and Living Spec describe explicit instruction authority without replacement bookkeeping.

## 3. Component & Interface Design

Existing commands and result fields remain. An accept --check result has no pending intent entry.
Handoff carried_gates contains only gate:plan-accept. Retired configuration is accepted as ignored at the SDD policy
boundary, including off; generic workflow configuration remains untouched. Historical decision loading is unchanged.

## 6. Verification & Test Plan

- AC-01/03: deployed workflow validation, new Unit evaluation, XL eligibility and legacy-record next/rules regression.
- AC-02: proposal acceptance, handoff record and composed delivery tests; required plan-accept and custom-gate behavior.
- AC-04: policy CLI default/custom/retired ask-auto-off tests and strict warning behavior.
- AC-05: guidance distribution tests, source/deployed search, docs rules and independent reconcile review.
- Run just lint-check spec, just check spec, rules --ci against a74c84af, sync --check/generated check and
  just test-affected --base a74c84afc72b193f32131242b223b76539500ba0 --tier all synchronously with full fallback.
