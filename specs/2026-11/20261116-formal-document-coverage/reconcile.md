---
reconcile_id: REC-formal-document-coverage
status: pending
targets:
  - file: docs/designs/delivery/DESIGN-workflow-stage-evaluation/design.md
    resolution: modified
  - file: docs/domain/distribution/DOMAIN-override-lifecycle.md
    resolution: modified
  - file: docs/operations/OPS-assignment-attention-routing.md
    resolution: modified
  - file: docs/operations/OPS-host-hook-dispatch-routing.md
    resolution: modified
  - file: docs/operations/OPS-mcp-runtime-refusals.md
    resolution: modified
  - file: docs/operations/OPS-search-mode-and-model-routing.md
    resolution: modified
---

# Reconcile: `SPEC-formal-document-coverage`

## Living Spec changes

The change is documentation only: it creates the six formal documents of the accepted inventory, each a `modified`
target above. No document was dropped: the search entry carries its explicit `--mode hybrid` row, which the source
supports (`SearchIndex.resolve_mode` returns an explicit mode unchanged, so a missing extra or model raises).

| Document | Reader question answered | Owners cited, not restated |
| --- | --- | --- |
| `DESIGN-workflow-stage-evaluation` | Evaluation order of `devkit workflow next` on the sample Unit of `SPEC-formal-document-kinds`, and the first-unmet-stage stop | `CAP-DLV-workflow-orchestration`, `CAP-DLV-workflow-envelopes`, `CAP-DLV-human-interaction` §5, `CAP-DLV-cli-and-output`, `CAP-DLV-workflow-definitions`, workflow reference |
| `OPS-assignment-attention-routing` | Evidence and owner per adaptive assignment attention value | `CAP-DLV-adaptive-assignments`, `CAP-WT-task-worktrees`, `ADR-adaptive-assignment-commands`, adaptive-dev `current-context.md` |
| `OPS-host-hook-dispatch-routing` | Owner for a configured hook with no visible warning and no observation | `CAP-HOST-lifecycle-observation`, `OPS-distribution-sync`, `CAP-DIST-sync-and-transactions`, host reference code table |
| `OPS-mcp-runtime-refusals` | Owner for partly refusing MCP tools or an inactive registration, by cross-surface evidence | `CAP-MCP-runtime-registration`, `ADR-mcp-runtime-and-shared-artifacts`, `CAP-DIST-sync-and-transactions`, `OPS-distribution-sync`, host reference MCP rows |
| `DOMAIN-override-lifecycle` | Capability state of a project override, its difference from `ORPHAN_LEFT`, and what changes it | `CAP-DIST-workspace-ownership`, `CAP-DIST-sync-and-transactions`, `CAP-DIST-agent-projections`, `DOMAIN-bundle-selection-and-installation`, glossary |
| `OPS-search-mode-and-model-routing` | Owner for a lexical-only search or a `SEARCH_*` model error, by an explicit `--mode hybrid` run | `CAP-SRCH-document-search`, `CAP-DOCS-document-search`, search reference error rows |

Capabilities, use cases, architecture, reference, steering and ADRs are unaffected: the documents move no normative
statement (`CAP-DOCS-documentation-ownership` §3.1) and no code changed. The existing formal documents
`DOMAIN-delivery-relationships`, `DOMAIN-bundle-selection-and-installation`, `OPS-distribution-sync`,
`DESIGN-distribution-transactions` and `DESIGN-distribution-file-directory-replacement` are unchanged; the new
documents link to some of them as owners. No link repair elsewhere was needed: formal documents are discovered by ID
and kind, not by a directory index.

Deviation from the inventory wording, kept on the capability's side: the inventory's "bundle mismatch" label is no
state name of `CAP-DIST-workspace-ownership` §3, so `DOMAIN-override-lifecycle` uses the capability's wording
(an override naming another bundle than the asset's); the inventory's "last `received_at`" is the `host status` field
`last_received`, whose object carries `received_at`.

## Entrypoints

`devkit spec entrypoints derive` was reviewed for this bundle; DOMAIN and OPS documents are ineligible. The DESIGN
already names its mechanism files `evaluate.py` and `decision_records.py` in `entrypoints`.

## Owner gaps and source feedback

Gaps found in owner documents are recorded as feedback in this bundle, not edited:
`FB-search-model-invalid-scope-disagrees`, `FB-override-removed-upstream-command-results-unstated`,
`FB-attention-base-check-differs-from-verify`, `FB-host-reference-mcp-table-gaps`,
`FB-host-observation-only-observe-handler`, `FB-handoff-carries-proposal-stage-decision`. No source feedback was
carried from Planning.
