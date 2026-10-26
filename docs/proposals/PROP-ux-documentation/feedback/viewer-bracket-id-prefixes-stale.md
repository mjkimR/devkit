---
id: FB-viewer-bracket-id-prefixes-stale
title: Viewer bracket-ID pattern lists stale prefixes
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

# [FB-viewer-bracket-id-prefixes-stale] Viewer bracket-ID pattern lists stale prefixes

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The viewer links bracket-form IDs (`[CAP-...]`) in rendered pages through a fixed prefix
  alternation that still lists `US`, removed by `ADR-usecases-replace-stories`, and omits `UC`, `MS` and `FB`, so
  bracket references to use cases, milestones and feedback stay unlinked. Code-span IDs are linked by index lookup and
  are not affected.
- **Proposed Procedure**: Build the pattern from the document kinds (the kind definition table of
  `PROP-table-driven-document-kinds`, whose viewer step can absorb this), or at least list the current prefixes.
- **Expected Benefit**: Bracket references to every kind link in the viewer, and a new kind such as `UX` needs no
  separate edit.
- **Cost & Risk**: Small; the frontend tests of rendering cover it.
- **Attempted**: Hypothesis from reading the source during `PROP-ux-documentation` Planning; not run.

## Diagnostic Details

- **Reproduction**: unknown; not reproduced in a browser. Read from the source.
- **Expected / Actual**: Expected bracket references of every current kind to link; the pattern matches `US` and
  misses `UC`, `MS` and `FB`.
- **Versions**: `main` at `96df5d86`.
- **Conditions**: Any page that writes a use case, milestone or feedback ID in bracket form.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `CAP-VIEW-repository-viewer`, `CAP-DOCS-document-model`, `ADR-usecases-replace-stories`.

## Evidence

```text
packages/devkit-viewer/frontend/src/lib/api/documents.ts:246
  /\[((?:CAP|US|ARCH|ADR|PROP|SPEC|PLAN|TASKS|REC|MAT|PADR)-[A-Za-z0-9][A-Za-z0-9-]*)\]/g
CAP-DOCS-document-model section 3.2 lists the prefixes CAP, UC, ARCH, ADR, PROP, PADR, SPEC, PLAN, TASKS, REC, FB, MAT, MS.
```
