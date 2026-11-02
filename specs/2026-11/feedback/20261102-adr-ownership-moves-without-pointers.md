---
id: FB-adr-ownership-moves-without-pointers
title: Compacted ADRs keep ownership clauses that later ADRs moved without a supersession pointer
scope: repo
kind: change-request
category: docs-mismatch
target: ADR-document-system, ADR-steering-documents
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-02
---

# [FB-adr-ownership-moves-without-pointers] Compacted ADRs keep ownership clauses that later ADRs moved without a supersession pointer

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The compaction copied every clause that no "Superseded in part" line names. Some of these
  clauses state an ownership that a later ADR moved without a pointer:
  - In `ADR-document-system`, the document-package clause says the spec bundle keeps shipping every rule asset,
    while the document-and-sdd-bundles clause moves the document rules, templates and docs-skeleton to the docs
    bundle.
  - In `ADR-steering-documents`, the background-pointer clauses say `devkit get-context spec` lists the steering
    documents, while the docs bundle declares `context_documents`.
- **Proposed Procedure**: Retire the superseded halves through a small ADR with `supersedes` (or "Superseded in part"
  lines on the replacements). Fix stale Confirmation test paths at the same time.
- **Expected Benefit**: Each compacted ADR states only the ownership that holds today.
- **Cost & Risk**: Low; no behavior changes.
- **Attempted**: The fidelity review found these and kept the text verbatim, because a compaction changes no decision.

## Diagnostic Details

- **Reproduction**: Compare `ADR-document-system` §Document package and bundles with
  `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml`.
- **Expected / Actual**: Expected one owner per asset; observed two statements.
- **Versions**: base `27987dd7`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: none.
- **Related Assets**: `ADR-decision-ledger` (compaction rules).

## Evidence

```text
packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml:6 context_documents = "docs/steering"
```

- **Disposition**: `SPEC-adr-ledger-cleanup`: `ADR-retire-native-approval-and-moved-ownership-clauses` retires the moved-ownership clauses of `ADR-document-system` and `ADR-steering-documents`, with pointer lines. Verified by `devkit rules check`, the spec review and its reverify; recorded in the spec's `reconcile.md`.
