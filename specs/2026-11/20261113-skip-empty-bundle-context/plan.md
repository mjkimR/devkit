---
id: PLAN-skip-empty-bundle-context
spec: SPEC-skip-empty-bundle-context
---

# Technical Plan: `SPEC-skip-empty-bundle-context`

## 1. Constitution & Invariant Review

No structural invariant changes. Update the declared contracts in `CAP-DIST-context-and-playbooks`,
`CAP-DIST-workspace-ownership` and `CAP-DIST-agent-projections`. No new package, feature edge or ADR is needed.

## 2. Architecture Overview & Impact

Keep a shared source-presence predicate in distribution services/bundles/guidance.py. Inventory uses selected
source facts for skill prefixes and retains required bundle names for root guidance. Exact retrieval reads the
receipt and validated manifest under its existing lock. The result adds context.required while preserving argv,
bundle and policy. Generic playbook instructions retrieve metadata for discovery and honor the flag.

## 3. Component & Interface Design

`context.required: bool` is additive; true means execute argv unless context is already loaded. False permits
proceeding without a load. An empty or absent declared directory still counts. No receipt schema change.

## 5. Error Handling & Edge Cases

Preserve receipt/override/personal-render validation and error codes. Explicit get-context remains unchanged.
Do not read installed packages or document providers to infer the requirement. Templates count as sources.

## 6. Verification & Test Plan

Focused distribution integration fixtures cover AC-01 through AC-07: no sources, literal/template constitutions
and instructions, document-only bundles, missing/empty directories, runtime documents, aliases, mixed selection,
preset refresh and manifest tampering. Run `just lint-check devkit-dist`, `just check devkit-dist`,
`just test-affected` with its full fallback, build the wheel and validate rules and sync.
