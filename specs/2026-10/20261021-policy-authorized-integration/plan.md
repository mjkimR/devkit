---
id: PLAN-policy-authorized-integration
spec: SPEC-policy-authorized-integration
---

# Technical Plan: `SPEC-policy-authorized-integration`

## Constitution & Invariant Review

`ADR-policy-authorized-local-integration` supersedes the gate-only restriction of `ADR-integration-approval-asserted` for explicit shared auto and local execution. Other authority and host boundaries remain.

## Components and Interfaces

- Integration providers validate shared ask/auto policy and preserve the existing effective digest.
- IntegrationService prepares the immutable request, refuses auto publication and prospective revocation, derives policy authority without confirmation, and reuses the existing execution and resume engine.
- Readiness provider keeps all completion, finding, receipt and result checks.
- Source bundle guidance and Living Spec explain policy authority and distinct host permissions.
- No dependency or schema version changes, durable journal or caller authority tokens.

## Failure Modes

Changed policy, identities and cleanup scope invalidate retained requests. Auto-to-ask prospective policy is refused before mutation. Permission failure preserves partial progress; restart never reconstructs authority from files.

## Verification

Service regressions cover AC-01 through AC-05, transport without elicitation and live Codex CLI/Claude Code smoke cover AC-06, and diff review plus rules cover AC-07. Run lint, type checks and `just test-affected` with its full fallback. Live host evidence is mandatory and cannot be replaced by unit tests. Medium independent code review and reconcile verification apply.
