---
reconcile_id: REC-formal-doc-padding-trim
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/designs/delivery/DESIGN-proposal-handoff/design.md
    resolution: modified
  - file: docs/designs/delivery/DESIGN-workflow-stage-evaluation/design.md
    resolution: modified
  - file: docs/designs/distribution/DESIGN-distribution-file-directory-replacement/design.md
    resolution: modified
  - file: docs/designs/distribution/DESIGN-distribution-transactions/design.md
    resolution: modified
  - file: docs/domain/delivery/DOMAIN-delivery-relationships.md
    resolution: modified
  - file: docs/domain/delivery/DOMAIN-feedback-lifecycle.md
    resolution: modified
  - file: docs/domain/distribution/DOMAIN-bundle-selection-and-installation.md
    resolution: modified
  - file: docs/domain/distribution/DOMAIN-override-lifecycle.md
    resolution: modified
  - file: docs/operations/OPS-assignment-attention-routing.md
    resolution: modified
  - file: docs/operations/OPS-distribution-sync.md
    resolution: modified
  - file: docs/operations/OPS-host-hook-dispatch-routing.md
    resolution: modified
  - file: docs/operations/OPS-mcp-runtime-refusals.md
    resolution: modified
  - file: docs/operations/OPS-search-mode-and-model-routing.md
    resolution: modified
related_designs: [DESIGN-proposal-handoff, DESIGN-workflow-stage-evaluation, DESIGN-distribution-file-directory-replacement]
related_domains: [DOMAIN-delivery-relationships, DOMAIN-feedback-lifecycle, DOMAIN-bundle-selection-and-installation, DOMAIN-override-lifecycle]
related_operations: [OPS-assignment-attention-routing, OPS-distribution-sync, OPS-host-hook-dispatch-routing, OPS-mcp-runtime-refusals, OPS-search-mode-and-model-routing]
---

# Formal document padding trim reconciliation

## Authoring contract

`ADR-formal-document-closings` records the decision. `CAP-DOCS-documentation-ownership` §3.3 rule 2 restates its
closing clauses (design: `## Authority boundary` naming the rules it explains and their owners, then
`## Update triggers`; domain and operations: `## Update triggers`, preceded by a boundary only for owners the table
and body do not name and for what the evidence cannot conclude; the no-row fallback under `## Routing`) and cites
the ADR. §3.3 rule 4 adds the same-kind fold (delete the folded document, keep its ID as an alias of the receiving
one), which `living-spec-writing` shared step 6 carries. §3.1 rules 5 and 7 are one Fact-type routing rule with the
15-row table Q3 settled, identical to the `living-spec-writing` table (pinned by
`test_formal_doc_checkpoints_guidance.py`); the old rule 8 is rule 7 and cites rule 5. No document cited §3.1 rules
by number (`rg` over `docs/`, `packages/`), so the renumbering breaks no reference. §3.2 lost its closing paragraph,
which `architecture-writing` "Responsibility boundary" states; §3.3 lost "This migration transfers..."; §4 names the
templates and writing instructions without restating their layout. §3.1 rule 6 and the §3.3 closing lines on
operations authority stay, since the narrowed boundaries rely on them.

The implementation is the docs bundle: `templates/{design,domain,operations,capability,usecase,ux,milestone}.md` and
`instructions/{design,domain,operations,living-spec,document,usecase,ux}-writing.md`; each statement above was
compared with those files at the reviewed head. `ADR-problem-first-formal-document-openings` and
`ADR-linked-domain-relationship-views` already carry their "Superseded in part" pointers from the handoff commit.

## Handoff mechanism move (Q8)

`CAP-DLV-proposal-lifecycle` lost four mechanism clauses and kept their outcomes: §4.1 step 5 no longer says the
merge is "planned in one preflight pass" (the conflict bullet still refuses every conflict before the first write);
the rollback paragraph keeps "removed when empty" without "followed back"; §4.3 keeps "each changed file is replaced
atomically" without naming `extract_links` and `relocate_links`; the dropped-record bullet loses "before ordinary
relocation". §4.1 now names `DESIGN-proposal-handoff` as the explanation of the order. The design states each moved
fact (phase 2 step 3, phase 3 rollback, phase 4 passes 1 and 2) and cites §4.2 for the body classification instead of
restating its table. The code review checked each against `handoff.py`, `specs.py` `roll_back` and the rules
library `relocation.py`. `ADR-proposal-handoff` §4 and §6 name the merge rules, the residual window and the result
fields, all still in the capability. No `.py` or `.ts` file reads the capability.

## Formal documents

- Designs: `DESIGN-proposal-handoff` (helpers in words, Q8 mechanism, `spec-next` check moved into the rewriting
  phase; the ADR-promotion row of the worked example is left to the sibling unit), `DESIGN-workflow-stage-evaluation`
  (helpers in words, two restated `CAP-DLV-human-interaction` §5 clauses cited instead, rerun command kept as an update
  trigger), `DESIGN-distribution-file-directory-replacement` (lead takes the folded problem sentence, boundary takes the
  `ARCH-05-4-distribution-components` §3 pointer, `aliases` holds the folded ID, `related_capabilities` added).
- Fold: the bundle DESIGN-distribution-transactions is deleted (target listed above as removed). Its old ID resolves
  to `DESIGN-distribution-file-directory-replacement` (`devkit docs resolve`, exit 0). Current referrers repointed:
  `CAP-DIST-sync-and-transactions` §3 and the resolved feedback `FB-viewer-adopts-bundle-grammar` (one line, edited by
  hand). Completed specs, reconcile records and materials keep the old ID and resolve it through the alias. Its
  `ARCH-06-runtime-view` §1 "not prerequisite" pointer is dropped. The viewer test `FormalReading.test.ts` reads five
  chapters and follows capability → detail → capability.
- Domain: owner-per-question and stock boundary lines removed in `DOMAIN-delivery-relationships` and
  `DOMAIN-bundle-selection-and-installation` (both gain `related_capabilities`, the latter `related_designs`, which
  carries its former route to the design); `DOMAIN-feedback-lifecycle` and `DOMAIN-override-lifecycle` keep only owners
  their tables do not name.
- Operations: each no-row fallback now sits under `## Routing`; `OPS-distribution-sync` merges its `RECOVERY_BLOCKED`
  to `HALT` rule into that fallback; boundaries keep only what the evidence cannot conclude and owners outside the
  table and body.

## Entrypoints

`devkit spec entrypoints derive` proposes every bundle template, instruction and test for each changed capability and
design; all are rejected. The capabilities and designs changed only in wording, the bundle files are not where their
reading starts, and the designs keep their existing entrypoints. DOMAIN and OPS are ineligible.

## Source feedback

`FB-proposal-lifecycle-capability-holds-mechanism-detail`: resolved by this spec with a Disposition (Q8 move landed,
verified by the code review and the `rg` checks of AC-08).

## Deferred work

None.
