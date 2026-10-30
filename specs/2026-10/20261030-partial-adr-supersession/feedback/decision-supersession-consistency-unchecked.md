---
id: FB-decision-supersession-consistency-unchecked
title: No check keeps decision status, supersedes and in-part lines consistent
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ (a decision ledger check)
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-decision-supersession-consistency-unchecked] No check keeps decision status, supersedes and in-part lines consistent

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `CAP-DOCS-document-model` ("Decision supersession") requires `superseded` and
  `superseded_by` only for a wholly replaced ADR, an "Superseded in part by `ADR-<new>`" line on a partly replaced
  one, and the superseder naming it in `supersedes`. The index does not read a decision's `supersedes` or
  `superseded_by`, so only review enforces this; the ledger had drifted across more than twenty ADRs before
  `SPEC-partial-adr-supersession` repaired it with a one-off frontmatter scan.
- **Proposed Procedure**: a docs-bundle rule (or an extension of `RULE-document-reference`) that reports, for
  decisions: `superseded_by` on a non-`superseded` ADR; a `superseded` ADR without `superseded_by`; a `supersedes`
  target that is neither `superseded` nor carries an in-part line naming the superseder; an in-part line whose
  superseder does not list the ADR in `supersedes`; and an unresolved ID in `supersedes`.
- **Expected Benefit**: the ledger stays searchable and the `adr-compaction` closure complete without a manual audit;
  a rename through `devkit rules fix` could also rewrite `supersedes` values.
- **Cost & Risk**: one rule and tests; aliases must resolve (a `supersedes` may name a member alias); existing
  repositories with drift get new errors, so it may start as a warning.
- **Attempted**: the scan rules were applied by hand in this Unit (frontmatter parse plus regex over in-part lines);
  after the repair it reports no inconsistency.

## Evidence

```text
parse.py: supersedes is skipped on documents other than Unit anchors.
Before SPEC-partial-adr-supersession: 4 partly replaced ADRs were status superseded, 1 accepted ADR carried
superseded_by, 10 superseders had in-part lines without supersedes, a dozen partial targets lacked a pointer.
```
