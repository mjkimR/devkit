---
reconcile_id: REC-alias-references-in-quick-references
status: pending
targets:
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
---

# Reconciliation

## Rule contract

`CAP-GOV-spec-rules` section 3.3 gains the quick references as a third ID-free input of `RULE-document-reference`:
the `quick_references` setting with its defaults, per-file settings, resolution with the messages of indexed
documents, the fixable alias citation and that the fix rewrites only the code span, the indexed-document and
steering-file exclusions, targeting and `[rules] exclude`, the unset `inputs`, and what stays unchecked (plain-text
IDs, feedback `target` fields). The catalog row names the new input and fix. The rule guide (`devkit rules explain`)
carries the same contract with the Configuration table.

## Renaming step

`CAP-DOCS-document-model` section 3.5 item 5 states that the rename's `devkit rules fix` also rewrites code-span
citations in the configured quick references, that a manual sweep still covers plain-text mentions (feedback
`target` fields included) and ID-free files outside the configured set (the root `README.md`, agent guides), and that a rename spec writes the old IDs as plain text in its mapping tables and prose. Only the
renaming step changed, by the agreed write scope; the section 1 sentence that `RULE-document-reference` "also reads
root glossary Owner cells and the IDs cited in steering files" is left as written and does not yet name the quick
references (a sibling unit owns other parts of this capability).

## Not affected

No use case changes its goal or steps: `UC-keep-the-living-spec-consistent` already has the rules report a broken
reference and repair what is deterministic, now in more files; no architecture document or ADR states the rule's file set; `ADR-document-id-aliases` (alias references
in current documents are fixed) and `ADR-immutable-decisions-editable-records` (ADRs and PADRs are rewritten) hold
unchanged. The glossary gains no term: "quick reference" is the existing wording of the repository's `AGENTS.md`, and the
setting name is a code identifier of the rule.

## Entrypoints

`devkit spec entrypoints derive` proposed no new pair worth writing: `CAP-GOV-spec-rules` already declares
`packages/devkit-docs/src/devkit_docs/features/governance/`, which holds `document_reference.py`, and
`CAP-DOCS-document-model` changed only in its renaming guidance, so its candidates (the rule, its guide and tests, the
`spec-specify` skill, the viewer README and `.devkit/installation.json`) are rejected.

## Source feedback

- `FB-alias-references-outside-index-unreported`: resolved. The rule checks and fixes cited IDs in the configured
  quick references; the base's four alias citations are rewritten; plain-text IDs, feedback `target` fields and
  ID-free files outside the configured set stay a manual sweep that the renaming step names (out of scope by the user's decision). Evidence: the rule tests, a clean
  whole-workspace `devkit rules check`, `review-01` and `reverify-01`.
- `FB-rules-fix-rewrites-rename-mapping-tables`: resolved with the guidance option (no rule change): the renaming step,
  `spec-specify` and the rule guide say rename specs write old IDs as plain text. Evidence: `test_rename_guidance.py`
  and `review-01`.
- `FB-document-reference-guide-adr-rewrite-stale`: resolved. The guide's Remediation states that ADRs and PADRs are
  rewritten. Evidence: the guide assertion in the rule tests, `devkit rules explain` and `review-01`.

No work is deferred.
