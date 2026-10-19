---
id: PLAN-autonomy-between-approval-gates
spec: SPEC-autonomy-between-approval-gates
---

# Technical Plan: `SPEC-autonomy-between-approval-gates`

## 1. Constitution & Invariant Review

No accepted decision is reversed. Clarify the existing no-Development-direction-gate rule in
`CAP-DLV-delivery-workflows` and retain `ADR-integration-approval-asserted` authority limits and review-loop stops.

## 2. Impacted Components

- New autonomy ADR: rationale, design rule and escalation boundaries.
- `devkit-spec` bundle constitution: concise operational rule referencing the ADR.
- `CAP-DLV-delivery-workflows`: matching durable execution and tool-design contract.

No schema, code, dependencies or workflow definition changes. Low effort is sufficient for the agreed wording;
self-review compares all three documents with the existing gates, authority and review rules.

## 3. Verification

Review AC-01 through AC-03 against the actual diff; run document governance checks, `git diff --check` and
`just test-affected`. No new tests for a documentation clarification. Sync managed assets only through
`devkit sync`, never by editing projected files. Preserve unrelated base-checkout changes.
