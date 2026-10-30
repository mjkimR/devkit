---
id: FB-rules-fix-rewrites-rename-mapping-tables
title: rules fix rewrites the old-ID column of a rename spec's own mapping table
scope: repo
kind: friction
category: tool-error
target: RULE-document-reference
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-rules-fix-rewrites-rename-mapping-tables] rules fix rewrites the old-ID column of a rename spec's own mapping table

## 1. Friction / Question (friction, question)

- **Context**: A spec that renames six documents listed each old ID in backticks in its Design table and problem
  statement, then moved the documents with the old IDs in `aliases` and ran `devkit rules fix`.
- **Expectation**: The rename procedure of `CAP-DOCS-document-model` (renaming step) says one `devkit rules fix`
  moves current documents to the new ID; the spec-specify contract says to cite documents by full ID in backticks.
- **Actual**: The fix also rewrote the old-ID column of the spec's own mapping table, its problem statement and its
  user story, so every row read "new ID → new ID" and the record lost which IDs were renamed.
- **Workaround (or Interpretation Chosen)**: Restored the old IDs as plain text (not code spans), which
  `RULE-document-reference` neither reports nor rewrites.
- **Suggestion**: State in the renaming step and in spec-specify that a rename spec writes the old IDs as plain text
  before it runs `devkit rules fix`, or let the rule skip a code span that is the ID an `aliases` entry declares in a
  row that also names the canonical ID.

## Evidence

```text
rules fix: fixed=132 (included specs/<unit>/spec.md and plan.md)
spec.md after fix: | `CAP-DLV-adaptive-development` | CAP-DLV-adaptive-development | Adaptive Development |
spec.md before fix: | `CAP-DLV-idea-incubation` | CAP-DLV-adaptive-development | Adaptive Development |
```
