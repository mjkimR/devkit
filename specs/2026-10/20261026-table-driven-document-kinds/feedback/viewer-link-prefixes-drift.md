---
id: FB-viewer-link-prefixes-drift
title: Viewer cross-reference links use a stale prefix list
scope: repo
kind: change-request
category: docs-mismatch
target: packages/devkit-viewer/frontend/src/lib/api/documents.ts
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-viewer-link-prefixes-drift] Viewer cross-reference links use a stale prefix list

The viewer turns `[ID]` references into links with its own prefix list, which no longer matches the document ID
grammar of `CAP-DOCS-document-model` section 3.2.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `documents.ts` links `[CAP|US|ARCH|ADR|PROP|SPEC|PLAN|TASKS|REC|MAT|PADR-...]` references.
  `US` is the retired use case prefix; `UC`, `FB` and `MS` references in brackets render as plain text.
- **Proposed Procedure**: Fix the list in a separate viewer bugfix; `SPEC-table-driven-document-kinds` leaves the
  viewer out of scope (its Planning decision).
- **Expected Benefit**: Use case, feedback and milestone references become navigable like the others, and the list
  cannot drift again.
- **Cost & Risk**: Rendered pages gain links; a `[UC-x]` that resolves to no document stays plain text as today.
- **Attempted**: Hypothesis; observed in source only, not in a running viewer.

## Diagnostic Details

- **Reproduction**: Read `frontend/src/lib/api/documents.ts:246` and compare with `ids.py` `PREFIXES`.
- **Expected / Actual**: Expected every prefix of the ID grammar; actual list has `US`, lacks `UC`, `FB`, `MS`.
- **Versions**: base `96df5d86`.
- **Conditions**: Any repository whose documents cite use cases, feedback or milestones in `[ID]` form.
- **Workarounds Attempted**: Not attempted.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/features/documents/models/ids.py:34-48`,
  `CAP-VIEW-repository-viewer`, historical Git `cfc82a4cb3d651c38c61b6a4da880be9ebfbe2fd:docs/proposals/PROP-table-driven-document-kinds/envelopes/scout-01.yaml` finding 1.

## Evidence

```text
documents.ts:246  /\[((?:CAP|US|ARCH|ADR|PROP|SPEC|PLAN|TASKS|REC|MAT|PADR)-[A-Za-z0-9][A-Za-z0-9-]*)\]/g
ids.py:34-48      PREFIXES = CAP, UC, ARCH, ADR, PROP, PADR, SPEC, PLAN, TASKS, REC, FB, MAT, MS
```
