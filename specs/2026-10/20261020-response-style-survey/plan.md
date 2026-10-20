---
id: PLAN-response-style-survey
spec: SPEC-response-style-survey
---

# Technical Plan: `SPEC-response-style-survey`

## 1. Constitution & Invariant Review

None. Follow the four accepted response-style ADRs and `CAP-DIST-manifest-spec`'s existing guidance cap.
Keep the opt-in manifest, language variable and distribution engine unchanged.

## 2. Architecture Overview & Impact

Replace the response-style Jinja skill body and its single guidance pointer with the accepted draft.
Adjust existing catalog deployment tests and consumer smoke assertions to verify the new rendered content.
Reflect the contract in `CAP-DIST-content-packages`. No dependencies or runtime interfaces change.

## 3. Implementation Choices and Failure Modes

Use the accepted draft's original wording, clarifying that arrow points are the ordinary default and required
formats take precedence. Preserve both language branches and short Korean guidance. Test deployed text and
projection equality rather than suggesting model adherence can be proven by substring assertions.
A stale local receipt requires Host sync during integration; this worker does not edit managed assets.

## 4. Verification & Test Plan

- AC-01/AC-02: independent review against the four authored examples and preservation obligations.
- AC-03/AC-04: catalog deployment tests for auto/ko, native projections, rendered content and byte count;
  consumer smoke verifies wheel installation and selection lifecycle.
- Run `just lint-check catalog`, `just check catalog`, `just test-affected`, `just smoke` and governance checks.
- Mandatory medium independent code review and separate reconcile verification cover bundle/smoke impact.
- Record checks actually run without claiming measured conversational superiority or verified host compaction.
