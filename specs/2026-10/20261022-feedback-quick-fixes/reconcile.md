---
reconcile_id: REC-feedback-quick-fixes
feature: SPEC-feedback-quick-fixes
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconciliation

`CAP-DIST-sync-and-transactions` now states that `[presentation] language` accepts exactly `auto`, `en` or `ko` and
that any other string is `CONFIG_INVALID` with a `[FIX]` naming the accepted values; the `fallback` metadata of
`devkit config show` is documented as always `false`. `CAP-DIST-workspace-ownership`, `CAP-INT-mcp-services` and
`CAP-DLV-proposal-incubation` drop the unsupported-string English fallback from their language statements.
`CAP-DLV-delivery-workflows` records that worker nested-role read scopes name the worktree's startup skill and
instruction paths, and that a `[DONE]` `spike` is not Planning evidence. No workflow definition or engine behavior
changed.

`ADR-shared-language-preference-with-bounded-approval-content` keeps its original wording (ADRs are append-only and
outside this unit's write boundary); its unsupported-string fallback outcome is replaced by this spec under the
user's recorded plan-intent. A superseding ADR is left to the Host. The `docs/development/reference/` quick
references still mention the `fallback` field, which remains in the output, so they stay accurate.

Entrypoints: `CAP-DIST-sync-and-transactions` gains the presentation validator
`packages/devkit-dist/src/devkit_dist/features/project/repositories/local_config.py`; the other derived candidates
(projections, tests, hub files, guide references) were reviewed and not applied.

The module short names are a development-tooling convenience documented in the README, not a Living Spec contract.

## Source feedback

All four explicitly linked open direct-fix sources are `resolved` with a Disposition naming this spec and its
verification: `FB-presentation-language-silent-fallback`, `FB-module-name-discovery-before-checks`,
`FB-nested-role-skill-read-scope` and `FB-planning-stage-skips-unrecorded-spike`. No in-scope work is deferred.
