---
reconcile_id: REC-gate-health-status
status: pending
targets:
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/gate/CAP-GATE-commit-gates.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
---

# Reconciliation: `SPEC-gate-health-status`

## Contract reflection

- `CAP-DIST-sync-and-transactions` owns optional status-check discovery, the typed advisory contract,
  deterministic ordering, atomic validation, isolated failure notices and unchanged JSON/strict semantics.
- `CAP-GATE-commit-gates` owns the provider registration, exact reuse of existing hook diagnosis and read-only
  applicability. The distribution reference documents usage and `STATUS_CHECK_EXTENSION_FAILED`.
- No architecture invariant, stored schema, rule execution, native host hook behavior or UX screen changes.
  The architecture already permits entry-point dependency inversion; no new durable domain term is introduced.

## Source feedback

`FB-gate-hook-problems-invisible-to-status` is resolved in its source file by the delivered implementation and
regressions, including actual pre-commit 4.1.0 force installation. No scope remains deferred.

## Baseline and outcome

At the same head, the overwritten-hook fixture runs with the status-check group disabled and enabled.
`test_baseline_with_provider_disabled_then_enabled` measures zero hook warnings disabled and exactly one
`GATE_HOOK_ENTRY_MISSING` enabled; hook/config bytes and modes remain identical. The dedicated gate status
advisory equals the general status advisory across overwritten, deleted/non-executable entry and hooksPath cases.
`test_real_pre_commit_force_install_exposes_existing_warning` reproduces actual `pre-commit install -f` locally.
The optional provider is present only in the built harness wheel; distribution-only tests pass with devkit-agt absent.

## Entrypoints

Keep distribution's existing installation-services doorway, which already covers the check loader. Add gate's
status use case as its third doorway. Reject broad cross-package feature-directory candidates: each capability
keeps its own behavior entrypoints rather than all paths joined mechanically from task boundaries.
