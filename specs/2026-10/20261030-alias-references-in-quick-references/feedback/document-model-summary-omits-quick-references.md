---
id: FB-document-model-summary-omits-quick-references
title: The document model summary does not name the quick references RULE-document-reference reads
scope: repo
kind: friction
category: docs-mismatch
target: CAP-DOCS-document-model
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-document-model-summary-omits-quick-references] The document model summary does not name the quick references RULE-document-reference reads

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-alias-references-in-quick-references` extended `RULE-document-reference` to the ID-free quick
  references (`quick_references` setting) and updated `CAP-GOV-spec-rules` and the renaming step of
  `CAP-DOCS-document-model`.
- **Expectation**: Section 1 of `CAP-DOCS-document-model` lists every ID-free input the rule reads.
- **Actual**: Its sentence says the rule "also reads root glossary Owner cells and the IDs cited in steering files"
  and does not name the quick references. The unit's write scope allowed only the renaming step, because a parallel
  unit edits other parts of the capability.
- **Workaround (or Interpretation Chosen)**: Left the sentence as written; the reconcile-reviewer judged it still true
  ("also reads" lists additions without claiming completeness) and the renaming step cites `CAP-GOV-spec-rules`.
- **Suggestion**: Once the parallel unit has landed, add the configured quick references to that sentence.

## Diagnostic Details

- **Reproduction**: Read section 1 of `CAP-DOCS-document-model` beside section 3.3 of `CAP-GOV-spec-rules`.
- **Expected / Actual**: Expected the three ID-free inputs; actual two.
- **Versions**: the head of `SPEC-alias-references-in-quick-references`.
- **Conditions**: write scope restricted to the renaming step by the Host.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `CAP-DOCS-document-model`, `CAP-GOV-spec-rules`, `RULE-document-reference`.

## Evidence

```text
CAP-DOCS-document-model section 1: "RULE-document-reference also reads root glossary Owner cells and the IDs cited in
steering files through the rules workspace cache"
CAP-GOV-spec-rules 3.3: "The quick references are a third ID-free input ..."
```
