---
reconcile_id: REC-adr-ledger-cleanup
status: resolved
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-mcp-runtime-and-shared-artifacts.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-proposal-acceptance.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-decision-ledger.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-document-system.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-group-compaction-by-topic.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-retire-native-approval-and-moved-ownership-clauses.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-steering-documents.md
    resolution: modified
---

# Reconcile: `SPEC-adr-ledger-cleanup`

## Compaction grouping (AC-01)

- `ADR-group-compaction-by-topic` supersedes the closure sentence of `ADR-decision-ledger`, which carries pointer
  lines under its heading and at the Compaction item.
- `CAP-DOCS-document-model` §Decision supersession states each of the new ADR's five traced clauses as a MUST:
  - groups are formed by topic;
  - a wholly superseded ADR joins its superseder's group;
  - crossing partial supersessions are handled on the replacements;
  - a kept ADR's `supersedes` is renamed to the replacement;
  - a replacement lists in `supersedes` each kept ADR that a member partially superseded.
- The `adr-compaction` playbook (spec bundle, not Living Spec) applies these rules in Steps 1 to 3, and
  `test_playbook_discovery_guidance.py` asserts them. The review verified the kept-ADR rule against
  `decision_supersession.py`.

## Retired clauses (AC-02)

`ADR-retire-native-approval-and-moved-ownership-clauses` retires the following clauses. Each target stays `accepted`
and carries pointer lines under its heading and at each affected item.

- In `ADR-proposal-acceptance`:
  - the native lifecycle approval clause;
  - the viewer exception clause;
  - the native form rendering consequence.
- In `ADR-mcp-runtime-and-shared-artifacts`, three parts of the Host-approval clause:
  - native confirmation as the normal route;
  - CLI/PR authorization as mere recovery;
  - no extra approval after native confirmation.
- In `ADR-document-system`:
  - the spec bundle's rule-asset distribution clause;
  - document templates and the docs skeleton in the devkit-spec methodology list (lifecycle templates stay).
- In `ADR-steering-documents`:
  - the `get-context spec` listing;
  - the steering list reaching role contracts through the spec context, with its guidance-test assertion.

The same targets also received editorial repairs, which change no decision:

- the `ADR-proposal-acceptance` summary no longer names native approval;
- `ADR-document-system` names the selected preset `docs = ["core", "docs-skeleton"]`.

No capability changes for AC-02. The current rules already live in these documents:

- `CAP-DLV-proposal-planning` (accept command);
- `CAP-INT-mcp-services` (Host conversational decision);
- `CAP-VIEW-repository-viewer` (working tree);
- `CAP-DOCS-document-model` and `CAP-DIST-context-and-playbooks` (docs bundle ownership and `context_documents`).

## Source feedback (AC-03)

- `FB-native-approval-adrs-without-pointers`: `resolved`, verified by `devkit rules check`, review-01 and its
  reverify rounds.
- `FB-adr-ownership-moves-without-pointers`: `resolved` on the same basis, after the templates scope was narrowed.
- `FB-integration-adr-chain-uncompacted`: stays `open`. The following `adr-compaction` run resolves it.

## Entrypoints

No capability or use case entrypoint changes; the change is documentation and guidance.
