---
id: PLAN-input-recovery-notices
spec: SPEC-input-recovery-notices
summary: "Use coded provider evidence for session input recovery and an existing proposal result notice for inactive milestone membership."
---

# Fix design

## 1. Constitution & Invariant Review

No architectural invariant changes. `ARCH-05-2-components` keeps readiness policy in devkit-spec and advisory
translation in devkit-agt. Integration tests exercise real Git/provider and filesystem/CLI boundaries.

## 2. Architecture Overview & Impact

The session readiness provider will emit a stable evidence code when session claims are incomplete or invalid.
The harness provider boundary will specialize `INTEGRATION_NOT_READY` recovery based on that code, without parsing
reason text. This avoids duplicating SDD claim validation in the harness or adding a persisted request schema.
A source refusal without the marker keeps its current fix. Claims stay bound into the request digest.

Proposal creation will resolve milestone identity before writes, inspect the resolved milestone status and append
a feature-owned NOTICE to `CreatedProposal.notices` for done/dropped only. The existing CLI serializes/renders it.
The notice belongs to the proposal feature; no milestone lifecycle operation is introduced.

## 6. Verification & Test Plan

For `SPEC-input-recovery-notices` AC-01/AC-02, add CLI regressions for absent claims during prepare and integrate,
using the real session provider and existing repository fixtures; preserve source-only guidance and successful retry
with the original digest. For AC-03/AC-04, parameterize status/alias and CLI JSON/text/strict cases, checking canonical
membership, notice code/level and unchanged milestone bytes. Keep invalid-ID no-write tests.

Run Red before any production edits, then the same regressions Green. Run affected integration suites, lint and type
checks for devkit/devkit-spec, `just test-affected` with its full fallback, and committed-head
`uv run devkit rules check --ci --base main`. Separate code and reconciliation reviewers verify cross-package impact.
