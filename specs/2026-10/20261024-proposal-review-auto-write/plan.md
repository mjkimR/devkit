---
id: PLAN-proposal-review-auto-write
spec: SPEC-proposal-review-auto-write
---

# Technical Plan: `SPEC-proposal-review-auto-write` Publish proposal review before acceptance

## 1. Constitution & Invariant Review

`ADR-proposal-acceptance` requires a source-bound review report published after the final Planning commit and before approval. It also makes the shared adapter the report store and keeps approval separate from report publication. This change clarifies and configures that sequence without changing the report schema or approval boundary.

`CAP-DLV-proposal-incubation` and `UC-incubate-and-hand-off-a-proposal` own the current proposal lifecycle contract and will be updated during Living Spec reconciliation. No architecture invariant or new ADR is required.

## 2. Architecture Overview & Impact

- `devkit-spec` owns `[tool.spec.proposal_review]` parsing and policy output.
- The spec bundle owns the proposal-review agent instructions. The instructions publish once before acceptance when automatic writing is enabled and consume the exact URI during acceptance.
- The existing shared artifact adapter remains the only report writer. Acceptance remains a reader and lifecycle operation.

## 3. Component & Interface Design

```toml
[tool.spec.proposal_review]
auto_write = true # default; false requires explicit pre-acceptance publication
```

Add a frozen `ProposalReviewConfig(auto_write: bool = True)` to the typed `SpecConfig`. Parse it in `read_spec_config`, reject unknown keys and non-boolean values with `SpecConfigError`, and include the default and setting in `devkit config template` and `devkit spec policy` output. Keep the field scoped to agent workflow behavior; it does not disable the report publication API.

Update `spec-review-proposal` and relevant acceptance instructions so they distinguish automatic report authoring/publication from explicit publication. Both paths publish before acceptance. The acceptance command receives the exact `report_uri` and source SHA and validates them; it never composes or writes a report.

## 4. Storage & State Management

No new storage is introduced. The shared adapter stores the immutable source-bound report. Acceptance reads and validates the report already published for the current source SHA.

## 5. Error Handling & Edge Cases

Invalid settings fail during policy parsing with `SPEC_CONFIG_INVALID`. A disabled setting does not bypass the report requirement. Missing, stale or invalid report URIs remain refusals; the agent must publish a current report before a new acceptance request.

## 6. Verification & Test Plan

- Unit tests for defaults, boolean values, malformed values and unknown proposal-review keys in `devkit-spec` configuration parsing.
- CLI tests proving `devkit spec policy` and `devkit config template` expose the effective setting.
- Bundle asset tests verifying both policy branches publish before acceptance and the acceptance instructions do not request report composition/publication.
- Existing source-bound report and native acceptance tests verify acceptance remains read-only with respect to the shared artifact adapter.
- Run `just lint devkit-spec`, `just check devkit-spec`, and `just test-affected` as applicable to the final diff.
