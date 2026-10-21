---
id: PLAN-periodic-drift-reconciliation
spec: SPEC-periodic-drift-reconciliation
---

# Technical Plan: `SPEC-periodic-drift-reconciliation`

## Constitution & invariant review

None. `ADR-dual-source-of-truth-and-periodic-reconciliation` remains authoritative for human arbitration.
The current base still has no maintenance bundle or companions; the proposal premises hold.

## Components and design

Use an empty resource module, entry point and existing playbook manifest in packages/devkit-catalog.
The upkeep preset and implicit all select the single drift asset. No new runtime or dependencies.
The procedure carries bounded intake, evidence, batched decisions, workflow routing and verification;
ordinary Markdown reports avoid a persistence engine. Update catalog README and installation recommendations.
Reconcile the five targets in `PROP-periodic-drift-reconciliation-target`.

## Failure handling

Missing tools, unsupported claims and unavailable checks become coverage gaps. Pending user dispositions
prevent a fully reconciled claim. Revision changes require evidence revalidation; no automatic repair.

## Verification

Catalog discovery, opt-in sync, preset membership and independent lookup tests; lint-check/check for catalog;
just test-affected with fallback preserved; governance rules. Retain a real read-only batch and separate
seeded exercise for AC-02 through AC-05. Medium independent code review and reconcile verification.

## Assumptions

Initial upkeep has drift only because companion assets are absent. Host performs official sync and integration.
Imported FB-nested-role-skill-read-scope is observation only, outside direct-fix scope.
