---
reconcile_id: REC-formal-docs-feedback-handoff
status: resolved
targets:
  - file: docs/domain/delivery/DOMAIN-feedback-lifecycle.md
    resolution: modified
  - file: docs/designs/delivery/DESIGN-proposal-handoff/design.md
    resolution: modified
---

# Reconcile: `SPEC-formal-docs-feedback-handoff`

## Living Spec changes

The change is documentation only: it creates the two formal documents of the spec, each a `modified` target above.

| Document | Reader question answered | Owners cited, not restated |
| --- | --- | --- |
| `DOMAIN-feedback-lifecycle` | What each feedback status means, how promoted, resolved, dismissed and forwarded differ, who changes a status and when, and what the recording lookup does per status | `CAP-DOCS-document-model` (Feedback lifecycle), `CAP-DLV-proposal-planning` §3.1, `CAP-DLV-delivery-workflows` (Source feedback at completion), `CAP-HARN-agent-guidance` (Feedback capture policy, §4.5), `ADR-feedback-lifecycle-ledger`, the spec bundle's `spec-feedback` skill, `feedback-hygiene` playbook and `source-feedback.md` reference, glossary |
| `DESIGN-proposal-handoff` | How `devkit spec proposal handoff` turns an accepted proposal into a spec unit, in source order, on the real handoff commit `93e72152c` | `CAP-DLV-proposal-lifecycle` §4.1 to §4.3, §4.6, §4.8 and Host-authorized proposal lifecycle CLI, `CAP-DLV-proposal-planning`, `CAP-DLV-spec-bundles`, `CAP-COLL-work-scope-registry`, `ADR-proposal-handoff`, `DOMAIN-delivery-relationships` |

Placement: `DOMAIN-feedback-lifecycle` sits in `docs/domain/delivery/` because feedback statuses are changed by
delivery activities (capture, Backlog triage, completion, handoff) owned by delivery and harness capabilities; only
the status vocabulary sits in the documents area, and `DOMAIN-delivery-relationships` holds the neighbouring
concepts.

Source agreement: every step of the design was checked against `handoff_proposal` and its helpers, `prepare` and
`HandoffUseCase` in `native_handoff.py`, `HandoffProposalUseCase`, `carry_proposal_body`, the four rewrite passes
and `auto_register`. The projected dependency graph check runs as the last preflight, after the body carry, because
it validates the rendered `spec.md`; the design states that order. The worked example predates the own-path boundary
omission (`cc42066c8`), and the design names that difference.

Capabilities, use cases, architecture, reference, steering, glossary and ADRs are unaffected: no normative statement
moves (`CAP-DOCS-documentation-ownership` §3.1) and no code changed. The existing formal documents
`DOMAIN-delivery-relationships` and `DESIGN-workflow-stage-evaluation` are unchanged; the new documents link to them
as related entries. No operations document is affected: neither document routes a symptom. No index or README needed
an update, since formal documents are discovered by ID and kind.

## Entrypoints

`DESIGN-proposal-handoff` names its mechanism files in `entrypoints`: the proposals and delivery `handoff.py`,
`native_handoff.py`, and the `body.py`, `rewrite.py` and `history.py` services. The domain entry has none, as
`domain-writing` requires.

## Owner gaps and source feedback

Over-detail found in an owner is recorded, not edited:
`FB-proposal-lifecycle-capability-holds-mechanism-detail`. No source feedback was carried into this unit.
