---
id: FB-document-reference-guide-adr-rewrite-stale
title: The document reference rule guide says rules fix never rewrites ADR or PADR alias references
scope: repo
kind: friction
category: instruction-conflict
target: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/guide.md
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-document-reference-guide-adr-rewrite-stale] The document reference rule guide says rules fix never rewrites ADR or PADR alias references

## 1. Friction / Question (friction, question)

- **Context**: Development of `SPEC-lifecycle-feedback-fixes` stated in `CAP-DOCS-document-model` section 3.5 item 5
  that a document rename's `devkit rules fix` rewrites alias references in ADRs, PADRs and spec `feedback/` files.
- **Expectation**: `devkit rules explain RULE-document-reference` agrees with the code and
  `ADR-immutable-decisions-editable-records`.
- **Actual**: The guide's Remediation section says the autofix "never rewrites an alias reference in an ADR or PADR".
  The code and the ADR say it does.
- **Workaround (or Interpretation Chosen)**: Followed the code and the ADR; the guide is outside this unit's write
  scope.
- **Suggestion**: Drop that clause from the guide's Remediation bullet, so a Planning agent scoping a rename does not
  exclude ADRs and PADRs again (the defect `FB-rename-write-scope-unstated` reported).

## Evidence

```text
guide.md (Remediation, Autofix): "... never rewrites an alias reference in an ADR or PADR, skips completed specs ..."
ADR-immutable-decisions-editable-records: RULE-document-reference reports an alias reference in an ADR or PADR like
  one in any current document, and devkit rules fix rewrites it to the canonical ID.
Found by the reconcile-reviewer check of SPEC-lifecycle-feedback-fixes.
```
