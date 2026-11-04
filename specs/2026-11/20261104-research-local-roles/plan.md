---
id: PLAN-research-local-roles
spec: SPEC-research-local-roles
---

# Technical Plan

## 1. Constitution & Invariant Review

Preserve research authority, optionality, explicit invocation and material ownership. Supersede only registered
research-role distribution clauses of `ADR-adaptive-development-and-research` in a scoped ADR.

## 2. Architecture Overview & Impact

Move role bodies into skill-local `roles/` without native subagent metadata. Remove subagent manifest assets.
Use general subagents with explicit role paths and minimal assignments; host execution settings are no longer
supplied by these role documents. Keep permissions factual and report unavailable delegation.
No new feature edge or dependency is introduced.

## 6. Verification & Test Plan

Update catalog integration and wheel-consumer checks for all host projections, upgrade cleanup, stale policy
settings and material preservation. Run `just lint-check catalog`, `just check catalog`, `just test-affected`
and repository governance checks. Review invocation guidance and reconcile affected contracts and migration guides.
