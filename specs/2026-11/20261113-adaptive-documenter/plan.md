---
id: PLAN-adaptive-documenter
spec: SPEC-adaptive-documenter
---

# Technical Plan: SPEC-adaptive-documenter

## 1. Constitution & Invariant Review

None. Preserve CAP-DLV-adaptive-development timing, role authority and Host context ownership. This overlay uses existing execution contracts; no ADR is needed.

## 2. Architecture Overview & Impact

Add skill-local roles/documenter.md under adaptive-dev. Reuse swarm-worker and installed-role path resolution. Connect references/documents.md and references/delegation.md. Reflect the role in CAP-DLV-adaptive-development and the package README. No runtime or dependency changes.

## 6. Verification & Test Plan

Extend existing consumer projection and role-path tests for AC-01. Review the overlay and delegation against AC-02 without duplicating prose in substring tests. Run adaptive bundle integration tests, just lint-check, just check, just test-affected and devkit rules check --ci --base main. Projection establishes no native invocation guarantee.
