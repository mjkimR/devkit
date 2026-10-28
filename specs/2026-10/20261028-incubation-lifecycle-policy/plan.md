---
id: PLAN-incubation-lifecycle-policy
spec: SPEC-incubation-lifecycle-policy
---

# Technical Plan

## 1. Constitution & Invariant Review

The shared reader remains in devkit-dist project; generic integration and omission reporting remain in devkit-agt. SDD judgments remain in devkit-spec. `ADR-own-development-approach-policy-outside-sdd` authorizes the contract; `ARCH-05-2-components` continues to govern layers. No core or public advisory/CLI changes are required.

## 2. Components & Interfaces

- Typed shared development approach reader accepts parsed configuration for snapshot reuse and root for normal inspection. Existing effective-config reporting owns defaults/source.
- Spec mutation use cases reject inactive lifecycle before writes. Guidance inspects approach before routing.
- Rule applicability uses a generic optional omission contract; only spec rules decide SDD ownership. Prior anchor ownership keeps comparison checks applicable after binding/anchor deletion.
- Project readiness reuses cumulative linter and explicit review/tests/lint claims; generic snapshot ownership detection refuses retained Unit work without lifecycle validation. Existing provider identity, digest, route and cleanup checks remain.
- Shared guides and capabilities reflect the consumer applicability matrix. No automatic development approach change occurs.

## 3. Error Handling & Verification

Invalid development config is DEVELOPMENT_CONFIG_INVALID; inactive lifecycle mutation is SPEC_LIFECYCLE_INACTIVE. Lifecycle omissions use SDD_LIFECYCLE_INACTIVE. A mismatched project provider uses INTEGRATION_APPROACH_MISMATCH and touched retained Units require INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED. Test common config without devkit-agt, SDD regressions, incubation rules, actual provider integration, snapshot boundaries, lint/types, affected tests, smoke and final sync/governance.
