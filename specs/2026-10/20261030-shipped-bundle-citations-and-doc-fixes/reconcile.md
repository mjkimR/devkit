---
reconcile_id: REC-shipped-bundle-citations-and-doc-fixes
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    resolution: modified
---

# Reconciliation: `SPEC-shipped-bundle-citations-and-doc-fixes`

`CAP-DIST-content-packages` section 1 states the repository convention for shipped bundle text next to the bundle
source layout convention: no backticked document ID that resolves to a document of this repository, except IDs of
documents a shipped bundle seeds; placeholders and examples that resolve to nothing are allowed and the
repository-only `devkit-dev` bundle is exempt. The rule ends with its enforcing test,
`tools/devkit-dev/tests/integration/test_bundle_citations.py`, which matches its three parts: backticked spans only,
the seeded-ID exception, and discovery equal to every `bundle.toml` under `packages/*/src/`. The `authoring`
bundle's `agent-asset-writing` instruction states the same rule for any bundle author without naming this
repository's documents.

`CAP-DIST-sync-and-transactions` now names `devkit sync --locked` first and a plain sync only after
`RECEIPT_STALE` for `CONFIG_LOCAL_RENDER_STALE`, the same remedy as the `LocalRenderStaleError` fix,
`CAP-DIST-context-and-playbooks` and `docs/development/reference/distribution.md`. No behavior changed.

`UC-plan-and-hand-off-a-proposal` gains extension 6a (moved base refused before the acceptance commit with
`SPEC_PROPOSAL_APPROVAL_NOT_READY` or `WORKTREE_MERGE_CONFLICT`, recovery by a base merge into `plan-<slug>`,
`devkit rules fix`, commit and rerun), extension 7g (conflict-free moved base lands without a merge into
`plan-<slug>`, result fields `target_sha`, `landed_sha` and `disclosure`) and scenarios 24 and 25. Both follow
`CAP-DLV-proposal-planning` (composed acceptance paragraph and the `SPEC_PROPOSAL_APPROVAL_NOT_READY` row) and the
e2e tests in `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py`
(`test_accept_cli_integrates_a_moved_target_without_a_base_merge`,
`test_accept_cli_refuses_a_target_change_to_the_proposal_before_the_acceptance_commit`,
`test_accept_cli_refuses_reference_drift_on_the_prospective_result`). Composed acceptance keeps refusing every
conflict; unit integration preparation is untouched.

No impact elsewhere: `CAP-GOV-rule-authoring` keeps the descriptor contract the advisory `unique_code` guide no longer
cites (the guide now names its own `FACTS` descriptor in `rule.py`); `CAP-GOV-rules-engine` names the
`agent-asset-writing` instruction only by name; `ARCH-05-2-components` already places repository-wide scans with the
`devkit-dev` tool. No glossary term is introduced. Nothing in the agreed scope is deferred.

## Source feedback

- `FB-bundle-text-document-id-citations`: resolved. The convention is stated in `agent-asset-writing`
  (Self-Containment) and `CAP-DIST-content-packages`, and `test_bundle_citations.py` pins it over every shipped
  bundle; it failed on the base's `CAP-GOV-rule-authoring` citation and passes after the rewording.
- `FB-sync-capability-render-stale-remedy-generic`: resolved by the proposed parenthetical in
  `CAP-DIST-sync-and-transactions`, verified against the advisory fix and `CAP-DIST-context-and-playbooks`.
- `FB-proposal-usecase-moved-base-acceptance`: resolved by extensions 6a and 7g and scenarios 24 and 25, verified
  against `CAP-DLV-proposal-planning` and the e2e tests named above.

## Entrypoints

No entrypoint is added: the three targets changed wording only, and the new test is not a doorway file.
