---
reconcile_id: REC-consolidation-terminology
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-consolidation-terminology.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-feedback-lifecycle-ledger.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-decision-ledger.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-retire-native-approval-and-moved-ownership-clauses.md
    resolution: modified
  - file: docs/decisions/README.md
    resolution: modified
---

# Reconciliation: `SPEC-consolidation-terminology`

## Contract comparison

The change renames one term and its identifiers; no behavior changes. `CAP-HARN-agent-guidance` names the `spec`
bundle's playbooks `adr-consolidation` and `feedback-consolidation` in its asset and playbook tables and describes
the record form as a consolidated record; the bundle's `bundle.toml` carries those asset IDs, each playbook's
frontmatter `name` matches and its `aliases` holds the former ID, which `devkit playbook get spec/adr-compaction`
and `spec/feedback-compaction` resolve (`ADR-playbook-retrieval`); the bundle tests pin the IDs, the manifest entries
and the aliases. `CAP-DOCS-document-model` keeps its consolidation-group and pointer MUST clauses with the term
replaced; nothing in `devkit_docs` code names the term. `CAP-DLV-delivery-workflows` names the
`feedback-consolidation` playbook in its feedback lookup paragraph. The 25 records under `specs/*/feedback/` carry
`FB-consolidated-<area>-<status>` IDs with the former ID as their first alias, the form the `feedback-consolidation`
playbook now prescribes; `devkit rules fix` rewrote the references of current documents and `devkit docs resolve` of
a former ID prints its alias.

`ADR-consolidation-terminology` records the rename with its reason and traces its clauses to the two capabilities.
`ADR-feedback-lifecycle-ledger`, `ADR-decision-ledger` and `ADR-retire-native-approval-and-moved-ownership-clauses`
changed wording only (titles, summaries and clauses with the term replaced; the retired alias IDs, the historical
proposal IDs and one rejected option's literal `compacted` kept as history); the review's word diff confirmed no
clause was added, dropped or reordered. The glossary gains **Consolidation**, distinct from Compact output and from
shortening; `docs/decisions/README.md` names the `adr-consolidation` playbook in its ledger paragraph; `Compact output`, the `compact` subagent level, `devkit_agt.features.compact`, context compaction and
history compaction keep their wording (the review found and the implementer restored one context-compaction clause
the bulk rename had caught).

No use case changes: `UC-route-development-intent` and `UC-resolve-stale-activity-branches` name only
`feedback-hygiene`; no architecture document names the term in the record-merging sense. Completed spec bundles,
their envelopes and `docs/materials/` keep the old wording as history (Non-Goal 3).

## Deferred work and source feedback

No source feedback; the change answers the user's direct decision. Nothing is deferred; the ADR names no follow-up.

## Entrypoints

`devkit spec entrypoints derive` proposes bundle playbook, skill and test paths and feedback records for the three
capabilities; all rejected (content, records and tests, not doorways). Entrypoints stay unchanged.

## Verification and retained work

`just test devkit-spec` 1639 passed, `just test devkit-dist` 1292 passed, `just test-affected` 1578 passed at build;
`just test devkit-spec bundles` 731 passed after the review fixes; `uv run devkit rules check` errors=0 warnings=0;
`uv run devkit sync --check` clean; `uv run devkit generated check` stale=0. Code review round 1 (REVISE: one P2,
three P3) is closed in `reverify-01`.

Reconcile check round 1 (independent `reconcile-reviewer`, `reconcile-check-01`) confirmed the targets and the
no-impact claims and found two P2 and two P3 reflection gaps without contradiction: the changed `docs/decisions/README.md`
was not a target, the new ADR's record-naming clause carried a trace to a table that does not restate it, two traces
were imprecise, and two glossary identifiers lacked code spans. All four are applied by the implementer and
self-verified in `reconcile-check-02`.
