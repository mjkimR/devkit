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
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
---

# Reconciliation

`CAP-DIST-sync-and-transactions` keeps the English fallback that
`ADR-shared-language-preference-with-bounded-approval-content` decides for an unsupported `[presentation] language`
string and now states that the fallback is never silent: `devkit sync`, `devkit status` and `devkit config show`
return a `PRESENTATION_LANGUAGE_UNSUPPORTED` warning under `notices` for each configuration file whose value fell back,
with a `[FIX]` naming `auto`, `en`, `ko` and the file, and no exit-code change except under `--strict`; `config show`
lists `notices` beside `presentation_language`. `CAP-DIST-workspace-ownership`, `CAP-INT-mcp-services` and
`CAP-DLV-proposal-incubation` keep their fallback statements and name the warning. The three
`docs/development/reference/` quick references that describe the `fallback` field name the warning too.
`CAP-DLV-delivery-workflows` records that worker nested-role read scopes name the worktree's startup skill and
instruction paths, and that a `[DONE]` `spike` is not Planning evidence. No workflow definition or engine behavior
changed.

The unit conforms to the ADR: the user decision recorded with the return to build-verify
(`decisions/02-return-build-verify.yaml`) withdrew the earlier `CONFIG_INVALID` refusal, so no superseding ADR is
needed.

Entrypoints: `CAP-DIST-sync-and-transactions` gains the presentation resolver and warning helper
`packages/devkit-dist/src/devkit_dist/features/project/services/presentation.py`; the other derived candidates
(projections, tests, hub files, guide references) were reviewed and not applied.

The module short names are a development-tooling convenience documented in the README, not a Living Spec contract.

## Source feedback

All four explicitly linked open direct-fix sources are `resolved` with a Disposition naming this spec and its
verification: `FB-presentation-language-silent-fallback` (disposition updated to the visible-warning fix),
`FB-module-name-discovery-before-checks`, `FB-nested-role-skill-read-scope` and
`FB-planning-stage-skips-unrecorded-spike`. No in-scope work is deferred.
