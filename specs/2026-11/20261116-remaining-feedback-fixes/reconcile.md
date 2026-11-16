---
reconcile_id: REC-remaining-feedback-fixes
status: resolved
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
    resolution: modified
  - file: docs/capabilities/search/CAP-SRCH-document-search.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/capabilities/host/CAP-HOST-lifecycle-observation.md
    resolution: modified
  - file: docs/capabilities/README.md
    resolution: modified
---

# Reconcile: `SPEC-remaining-feedback-fixes`

## Living Spec changes

The change is documentation against unchanged source; each target restates source behavior.

- `CAP-DOCS-document-search` §4.5 and `CAP-SRCH-document-search` §2: `SEARCH_MODEL_INVALID` reaches the caller in every
  mode that loads the model (`auto`, `dense`, `hybrid`), never `lexical`; `SEARCH_EXTRA_MISSING` and
  `SEARCH_MODEL_NOT_FOUND` only for explicit `dense` or `hybrid`. Source: `SearchIndex.resolve_mode` and `search` in
  `packages/devkit-dist/src/devkit_dist/features/search/services/index.py`; test
  `test_auto_still_reports_a_broken_model`. `OPS-search-mode-and-model-routing` already states the same scope.
- `CAP-SRCH-document-search` §6: modules named with their `services/` and `models/` layers, contract types under
  `models/contracts.py`.
- `docs/development/reference/host.md` MCP services table: Level and mode cells derived from the error classes by the
  `devkit.advisory` mode derivation, and the `MCP_REGISTRATION_PENDING` notice row matching
  `CAP-MCP-runtime-registration` (withheld registration writes). `CAP-MCP-runtime-registration` itself is unchanged.
- `CAP-DIST-workspace-ownership` §3: `list`, `diff` and `accept` results for a kept record whose asset left its bundle;
  pinned by `test_remove_drops_the_override_of_a_removed_asset`.
- `CAP-HOST-lifecycle-observation` §5: the observation record is observe-only; a non-observe handler's failure is
  reported on hook stderr and not recorded.
- `docs/capabilities/README.md`: the area tree lists all 18 areas.

## Impact assessment

- Design: no `DESIGN` document covers these mechanisms' statements changed here; no source changed, so no mechanism
  statement or artifact is affected.
- Domain: no domain term introduced or renamed; glossaries unaffected.
- Operations: the operations routing entries from the formal-document-coverage Development already follow the source
  behavior now stated; none needs an update.
- Use cases and architecture: no behavior or structure change.
- Entrypoints: `spec-entrypoints` derived only the override tracking test file as a candidate for four documents;
  all were rejected because a test is not a doorway file and no source changed. No document's `entrypoints` changed.

## Source feedback

Each was set `resolved` with a Disposition naming this spec, verified by the code review (review-01) and the checks
in green-01:

- `FB-search-model-invalid-scope-disagrees`: resolved (AC-01).
- `FB-search-module-layout-omits-layers`: resolved (AC-02).
- `FB-host-reference-mcp-table-gaps`: resolved (AC-03); rows stay without anchors like every other table in the file.
- `FB-override-removed-upstream-command-results-unstated`: resolved (AC-04).
- `FB-host-observation-only-observe-handler`: resolved (AC-05); a persisted last-failure record was not adopted
  because there is no evidence of need.
- `FB-capabilities-readme-area-tree-incomplete`: resolved (AC-06).

## Deferred work

None.
