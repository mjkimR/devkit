---
id: FB-native-approval-adrs-without-pointers
title: Two accepted ADRs still describe the native approval route without a supersession pointer
scope: repo
kind: change-request
category: docs-mismatch
target: ADR-proposal-acceptance, ADR-mcp-runtime-and-shared-artifacts
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-02
---

# [FB-native-approval-adrs-without-pointers] Two accepted ADRs still describe the native approval route without a supersession pointer

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `ADR-proposal-acceptance` lets a native `spec_plan_accept` form authorize acceptance.
  `ADR-mcp-runtime-and-shared-artifacts` makes native confirmation the normal route when connected. In
  practice, `ADR-delivery-approval-and-lifecycle-authority` already replaced both with a Host conversation followed by a CLI call.
  `devkit spec proposal accept` is the acceptance command. Neither ADR carries a "Superseded in part by" line.
  `ADR-proposal-acceptance` also describes a "narrowly scoped supersession" of the viewer that keeps Git-only ordinary
  endpoints, which `ADR-repository-viewer` has since replaced.
- **Proposed Procedure**: Add the missing partial-supersession pointers (or a small retiring ADR, as
  `ADR-local-and-pull-request-integration` did). Then compact both with the integration chain
  (`FB-integration-adr-chain-uncompacted`).
- **Expected Benefit**: No accepted ADR describes an approval route that does not exist.
- **Cost & Risk**: Low; no behavior changes.
- **Attempted**: Hypothesis. The compaction run left both ADRs out for this reason.

## Diagnostic Details

- **Reproduction**: `rg spec_plan_accept packages/ tools/` finds nothing.
- **Expected / Actual**: Expected a pointer to the superseding ADR; observed none.
- **Versions**: base `27987dd7`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: none.
- **Related Assets**: `CAP-DLV-proposal-planning`, `CAP-INT-mcp-services`.

## Evidence

```text
docs/decisions/2026-10/20261022-proposal-acceptance.md: "a native `spec_plan_accept` form explicitly authorizes ..."
docs/decisions/2026-10/20261022-mcp-runtime-and-shared-artifacts.md: "Native confirmation is the normal route when connected"
```

- **Disposition**: `SPEC-adr-ledger-cleanup`: `ADR-retire-native-approval-and-moved-ownership-clauses` retires the native approval clauses of both ADRs, with pointer lines. Verified by `devkit rules check`, the spec review and its reverify; recorded in the spec's `reconcile.md`.
