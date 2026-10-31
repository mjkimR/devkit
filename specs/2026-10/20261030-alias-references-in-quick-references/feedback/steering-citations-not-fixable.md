---
id: FB-steering-citations-not-fixable
title: An alias cited in a steering file is reported but not fixed, unlike one in a quick reference
scope: repo
kind: suggestion
category: other
target: RULE-document-reference
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-steering-citations-not-fixable] An alias cited in a steering file is reported but not fixed, unlike one in a quick reference

## 2. Suggestion / Change Request (suggestion, change-request)

Inconsistent fix coverage between two ID-free inputs of the same rule.

- **Current Procedure**: `RULE-document-reference` reports a backtick-cited alias in a steering file (`docs/steering/*.md`)
  and in a glossary Owner cell without a fix, while since `SPEC-alias-references-in-quick-references` it rewrites the
  same citation in a quick reference with `devkit rules fix`. After a rename, steering citations need a hand edit.
- **Proposed Procedure**: Let the fix rewrite a code-span alias in the steering files (and, if wanted, glossary Owner
  cells) with the same offset-based rewrite the quick references use.
- **Expected Benefit**: One `devkit rules fix` after a rename covers steering background too; one behavior to explain.
- **Cost & Risk**: Changes a stated contract (`CAP-GOV-spec-rules` 3.3: steering "No autofix"); the Owner cell rewrite
  must keep the table layout. Low risk: the rewrite touches only the ID span.
- **Attempted**: Hypothesis; the quick-reference rewrite is implemented and tested, the steering pass was left
  report-only as a Non-Goal of that spec.

## Diagnostic Details

- **Reproduction**: Cite an alias in `docs/steering/product.md`, run `devkit rules fix`, then `devkit rules check`.
- **Expected / Actual**: Proposed: rewritten. Actual: still reported, `name` remediation.
- **Versions**: the head of `SPEC-alias-references-in-quick-references`.
- **Conditions**: any repository with steering files.
- **Workarounds Attempted**: hand edit.
- **Related Assets**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/document_reference.py`
  (`_steering`, `_rewrite_citations`), `CAP-GOV-spec-rules`.

## Evidence

```text
test_ids_cited_in_steering_files_resolve_without_fixes_or_edges: product.md unchanged after fix=True
test_an_alias_cited_in_a_quick_reference_is_fixed: quick references rewritten by fix=True
```

- **Disposition**: `SPEC-steering-alias-autofix`: steering code-span and glossary Owner aliases now receive
  deterministic fixes preserving delimiters and table columns; deployed rule suite 47 tests and affected suite
  2140 tests pass. Independent review's masked-first-cell defect was fixed and regression-verified.
