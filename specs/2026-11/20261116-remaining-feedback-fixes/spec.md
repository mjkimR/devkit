---
id: SPEC-remaining-feedback-fixes
title: Remaining formal-document-coverage feedback fixes
summary: Align search, host reference, override, observation and capabilities README docs with current behavior from six open feedback items
status: completed
created: 2026-11-16
related_capabilities: [CAP-DOCS-document-search, CAP-SRCH-document-search, CAP-DIST-workspace-ownership, CAP-HOST-lifecycle-observation, CAP-MCP-runtime-registration]
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-remaining-feedback-fixes] Remaining formal-document-coverage feedback fixes

## 1. Problem Statement & Motivation

Six open feedback items from the formal-document-coverage Development found Living Spec and reference text that
disagrees with, omits or mislocates current source behavior. An agent routing a search model error, an MCP code, an
override record whose asset left its bundle, or a missing hook observation reads a wrong or incomplete statement. The
source behavior is the intended one; the documents are the defect.

## 2. Defect Characterization

- **Current behavior**:
  - `CAP-DOCS-document-search` §4.5 says `SEARCH_MODEL_INVALID` passes through only for explicit dense or hybrid
    searches; `CAP-SRCH-document-search` §2 says a broken model raises it "in every mode". `SearchIndex.resolve_mode`
    loads the model for `auto` and lets `ModelInvalidError` through, while `lexical` never loads the model.
  - `CAP-SRCH-document-search` §6 lists `lexical.py`, `dense.py`, `fusion.py`, `index.py` and `errors.py` without
    their `services/` and `models/` layers, puts `SearchDocument`, `SearchHit` and `SearchMode` in `index.py` and
    omits `models/contracts.py`.
  - The MCP services table of `docs/development/reference/host.md` has five two-cell rows in a three-column table
    and no `MCP_REGISTRATION_PENDING` row.
  - `CAP-DIST-workspace-ownership` §3 does not state what `override list`, `diff` and `accept` report for a kept record
    whose asset the installed bundle no longer has.
  - `CAP-HOST-lifecycle-observation` §5 does not state that only the `observe` handler writes the observation record.
  - The Directory Structure tree of `docs/capabilities/README.md` lists 12 of the 18 capability areas.
- **Expected behavior and its basis**: each document states the source behavior pinned by its tests:
  `packages/devkit-dist/src/devkit_dist/features/search/services/index.py` and
  `packages/devkit-dist/tests/integration/features/search/test_index.py` (`test_auto_still_reports_a_broken_model`);
  the advisory mode derivation in `devkit.advisory` applied to `RuntimeStaleError`, `McpWorkspaceError`,
  `McpInteractiveError`, `HostMcpError`, `HostMcpInputError` and `McpRegistrationPendingNotice`, with
  `CAP-MCP-runtime-registration` (withheld registration writes); `OverrideStatus.drift_detected` and `_find` in the
  distribution override use cases; `observe` and `host status` in the host feature; the `docs/capabilities/` listing.
- **Behavior to preserve**: no source behavior changes. Existing search, override, host and MCP tests keep passing;
  the existing `test_remove_drops_the_override_of_a_removed_asset` assertions stay.
- **Reproduction conditions**: read each named document section against the cited source and `ls docs/capabilities/`;
  for the override record, `pytest packages/devkit-dist/tests/integration/features/distribution/test_override_tracking.py`
  with the added pin.
- **Assumption**: the observation record stays observe-only; a persisted last-failure record is not adopted because
  no evidence shows a need for it.

## 3. Non-Goals

1. **Scope Excluded**: any source code change, a hook failure-recording mechanism, anchors on host reference table
   rows, other feedback items, and restructuring the search capability's module layout ownership.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Search model error scope agrees with source
- **Given** `CAP-DOCS-document-search` §4.5 and `CAP-SRCH-document-search` §2
- **When** a reader looks up when `SEARCH_MODEL_INVALID` reaches the caller
- **Then** both state it for every mode that loads the model (`auto`, `dense`, `hybrid`) and never for `lexical`,
  and `SEARCH_EXTRA_MISSING` and `SEARCH_MODEL_NOT_FOUND` pass through only for explicit `dense` or `hybrid`.

### [AC-02] Search module layout names each layer
- **Given** `CAP-SRCH-document-search` §6
- **When** a reader locates a module
- **Then** each listed module carries its layer path: `services/lexical.py`, `services/dense.py`,
  `services/fusion.py`, `services/index.py` (`SearchIndex` only), `models/contracts.py` (`SearchMode`,
  `SearchDocument`, `SearchHit`) and `models/errors.py`.

### [AC-03] Host reference MCP table is complete
- **Given** the MCP services table of `docs/development/reference/host.md`
- **When** a reader routes an MCP code
- **Then** every row has three cells, the five former two-cell rows show `ERROR` with `INTERACTION`, `BLOCKED`,
  `BLOCKED`, `MAINTENANCE` and `INPUT_ERROR` respectively, and an `MCP_REGISTRATION_PENDING` `NOTICE` row names
  `uv run devkit sync --registrations-only`.

### [AC-04] Override results for a removed-upstream record are stated and pinned
- **Given** a tracked override kept after its asset left the installed bundle
- **When** `override list`, `diff`, `accept` and `remove` run on it
- **Then** `CAP-DIST-workspace-ownership` §3 states `list` reports `drift_detected: false`, `diff` and `accept`
  refuse with `SELECTION_INVALID` (asset not found) and `remove` reconciles it, and the regression test asserts the
  `list`, `diff` and `accept` results before `remove`.

### [AC-05] Observation record scope is stated
- **Given** `CAP-HOST-lifecycle-observation` §5
- **When** a reader interprets a null `last_received`
- **Then** §5 states only the `observe` handler writes the record, another handler leaves `last_received: null` after
  successful dispatches, and its failure appears only on hook stderr and is not recorded.

### [AC-06] Capabilities area tree is complete
- **Given** the Directory Structure tree of `docs/capabilities/README.md`
- **When** compared with `ls docs/capabilities/`
- **Then** it lists all 18 areas, including `collaboration/` (prefix CAP-COLL), `documents/` (CAP-DOCS),
  `harness/` (CAP-HARN), `mcp/` (CAP-MCP), `traceability/` (CAP-TRACE) and `viewer/` (CAP-VIEW).

### [AC-07] Behavior is preserved
- **Given** the unchanged source
- **When** `just test-affected` and the override tracking tests run
- **Then** they pass with exit `0`.

## Source feedback

- `FB-search-model-invalid-scope-disagrees`: AC-01.
- `FB-search-module-layout-omits-layers`: AC-02.
- `FB-host-reference-mcp-table-gaps`: AC-03.
- `FB-override-removed-upstream-command-results-unstated`: AC-04.
- `FB-host-observation-only-observe-handler`: AC-05.
- `FB-capabilities-readme-area-tree-incomplete`: AC-06.
