---
id: FB-glossary-owner-ids-unchecked
title: RULE-document-reference did not report two unresolvable capability IDs in docs/glossary.md
scope: repo
kind: friction
category: docs-mismatch
target: RULE-document-reference (docs/glossary.md)
skill: spec-sync
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-glossary-owner-ids-unchecked] RULE-document-reference did not report two unresolvable capability IDs in docs/glossary.md

## 1. Friction / Question (friction, question)

- **Context**: Migrating devkit's `docs/glossary.md` to the five-column table, whose `Owner` column carries the
  defining document ID in backticks.
- **Expectation**: The constitution and `living-spec-writing` treat a backticked full ID as a reference that must
  resolve (`RULE-document-reference`), so a dangling `Owner` ID would be reported.
- **Actual**: Two cells (CAP-ADV-protocol and CAP-HOST-lifecycle, written here as plain text) resolved to no document, and neither the commit gate
  nor `devkit rules check --ci --base <base>` reported them; only the reconcile reviewer found them.
- **Workaround (or Interpretation Chosen)**: Resolved every `Owner` ID by hand with `devkit spec resolve` and fixed the
  two cells (`CAP-ADV-agent-advisory-protocol`, `CAP-HOST-lifecycle-observation`).
- **Suggestion**: Decide whether the glossary (a document without an ID) is in the reference rule's scope. Now that the
  terminology guidance makes `Owner` a registration field, including it would keep the column trustworthy.

## Diagnostic Details

- **Reproduction**: Before the fix, `devkit rules check --ci --base <base>` reported errors=0 with the two cells in place;
  `devkit spec resolve CAP-ADV-protocol` returned `SPEC_ID_UNRESOLVED`.
- **Expected / Actual**: Expected a reference violation; actual none.
- **Versions**: devkit-spec at the branch of `SPEC-terminology-authoring-guidance`.
- **Conditions**: `docs/glossary.md` has no frontmatter ID. Why the rule skips it was not investigated.
- **Workarounds Attempted**: Manual resolution of all 14 Owner IDs; all resolve after the fix.
- **Related Assets**: `RULE-document-reference`, `SPEC-terminology-authoring-guidance`, `CAP-HARN-agent-guidance`.

## Evidence

```text
devkit spec resolve CAP-ADV-protocol   -> [ERROR] (SPEC_ID_UNRESOLVED) no document has the ID CAP-ADV-protocol
devkit spec resolve CAP-HOST-lifecycle -> [ERROR] (SPEC_ID_UNRESOLVED) no document has the ID CAP-HOST-lifecycle
devkit rules check --ci --base <base>  -> [SUMMARY: errors=0 warnings=0]
```
