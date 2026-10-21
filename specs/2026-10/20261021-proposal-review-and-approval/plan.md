---
id: PLAN-proposal-review-and-approval
spec: SPEC-proposal-review-and-approval
---

# Technical Plan: `SPEC-proposal-review-and-approval` Proposal review reports and unified plan-accept MCP approval

## 1. Architecture Overview & Impact
- Target Area: capabilities/delivery/

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-spec/src/devkit_spec/`
- `packages/devkit-viewer/src/devkit_viewer/`
- `docs/capabilities/delivery/`
- `docs/capabilities/viewer/`
- `docs/development/reference/`
- `packages/devkit-spec/tests/`
- `packages/devkit-viewer/tests/`
- `packages/devkit-viewer/frontend/`
- `packages/devkit/src/devkit/integration/`
- `packages/devkit/tests/integration/`
- `docs/capabilities/integration/`
- `docs/capabilities/harness/`
- `docs/decisions/`

### Excluded Boundaries:
- `packages/devkit-dist/src/devkit/distribution/`

## 3. Verification & Test Plan
- Run focused report/form/composition fault-injection tests, lint/type checks, `just test-affected --base main` and cumulative governance checks. Viewer frontend changes also run lint/check/test/build.

## 4. Invariant Review and Implementation Decisions

The immutable shared adapter is implemented on the current base; its API matches the accepted design. Keep report semantic authorship with the agent and validate structural coverage in the domain service. Integration owns a typed process-local composition seam and existing readiness/cleanup guards; spec owns acceptance and exact delta checks. Revalidate all scope after form replies and before effects. Partial progress is preserved and requires fresh remaining-effects approval. No durable authority or fake affirmative confirmation is permitted. The narrow viewer read exception requires a new superseding ADR; Git endpoints and no-write protections remain.

## 5. Components and Failure Handling

Add report publication and exact validation in devkit-spec, exposed through CLI and fresh MCP service factories. Add plan-accept orchestration and adapt standalone handoff to report validation. Integration composition binds the invocation to an immutable prepared request and exact acceptance descendant. Return observed progress after every partial failure without rollback. Viewer uses only the configured local adapter and sanitizes report rendering. Update source skill assets and let the Host sync projections.
