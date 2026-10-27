---
id: PLAN-seeded-paths-in-boundaries
spec: SPEC-seeded-paths-in-boundaries
---

# Technical Plan: `SPEC-seeded-paths-in-boundaries` Seeded and synced paths in proposal boundaries

## 1. Architecture Overview & Impact
- Target Area: delivery/
- Wording only in the `spec` bundle's delegation text, its capability and its guidance test
  (`ADR-admit-change-sync-outputs`). No code, rule or CLI changes.

## 2. Component Breakdown & Interface Contracts

1. `spec-delegate` `references/payload.md`: rewrite the bundle-source bullet to admit the class (AC-01).
2. `subagents/development-worker.md.jinja`: rewrite step 5 (clean start as `sync_start`, commit every output, record
   `(sync output)`) and add the exception to the `.devkit/` denial (AC-02).
3. `spec-delegate` `references/worker.md`: add the `(sync output)` receipt check to Validate (AC-03).
4. `CAP-DLV-delivery-workflows`: rewrite the delegated bundle-source sentence (AC-04).
5. `test_delegation_sandbox_guidance.py`: pin the new sentences in place of the old (AC-05).
6. `devkit sync` after the bundle edits; commit `.devkit/installation.json`.

### Planned Boundaries:
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/worker.md`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja`
- `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`
- `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`
- `.devkit/installation.json`

### Excluded Boundaries:
- `docs/decisions/`
- `packages/devkit-spec/src/devkit_spec/features/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/proposal_boundaries/`

## 3. Verification & Test Plan
- `just test devkit-spec tests/integration/bundles/spec/test_delegation_sandbox_guidance.py` (AC-01 to AC-03, AC-05).
- `just test-affected`, `just lint-check devkit-spec`, `just rules-check`.
- `uv run devkit sync --check` exits `0` after the sync commit.
