---
id: FB-rename-write-scope-unstated
title: Document renames imply writes to ADRs and spec feedback that boundaries exclude
scope: repo
kind: change-request
category: instruction-conflict
target: CAP-DOCS-document-model
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-rename-write-scope-unstated] Document renames imply writes to ADRs and spec feedback that boundaries exclude

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: The renaming step of `CAP-DOCS-document-model` (§3.5 item 5) says one `devkit rules fix`
  moves current documents to the new ID. It does not say which paths that writes. The proposal template's
  `boundaries.excludes` example lists `docs/decisions/`, and drafts commonly exclude `specs/` as history. Under
  `ADR-immutable-decisions-editable-records`, `RULE-document-reference` reports and fixes alias references in ADRs.
  It also treats `specs/**/feedback/` files as current at any status. A rename proposal that follows the template
  therefore excludes paths its own rule fix must write.
- **Proposed Procedure**: State in the renaming step that the rewrite reaches ADRs, PADRs and feedback files under
  `specs/`. Have it name `devkit docs refs <old-id> --direction in` as the way to list the paths a rename proposal
  must own. Optionally add a comment to the template's `excludes` example that a document rename must own the
  referencing ADRs and feedback directories.
- **Expected Benefit**: Planning finds the full write scope before the challenger pass instead of after it.
  Development no longer hits a boundary conflict when it runs `devkit rules fix`.
- **Cost & Risk**: One sentence in a capability and an optional template comment; no behavior change.
- **Attempted**: Observed in this Planning run. The draft excluded `docs/decisions/` and `specs/`. The challenger
  found 15 feedback files in 10 `specs/**/feedback/` directories and 7 ADRs citing IDs to be renamed, and Planning
  widened `owns`.

## Diagnostic Details

- **Reproduction**: Plan a rename of a capability ID that ADRs and spec feedback cite, with the template's
  `excludes`.
- **Expected / Actual**: Expected: the rename procedure names its write scope. Actual: the scope was found only
  through `index.is_historical` and `ADR-immutable-decisions-editable-records`.
- **Versions**: base `fb9b549a`.
- **Conditions**: SDD proposal Planning on a `plan-` worktree.
- **Workarounds Attempted**: The `owns` entries list each referencing `feedback/` directory and `docs/decisions/`.
- **Related Assets**: `CAP-DOCS-document-model`, `RULE-document-reference`,
  `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/templates/proposal.md`.

## Evidence

```text
packages/devkit-docs/src/devkit_docs/features/documents/repositories/index.py:239-242 is_historical excludes feedback/
docs/decisions/2026-10/20261022-immutable-decisions-editable-records.md:75-78 alias references in ADRs are fixed
proposal template boundaries.excludes example: - docs/decisions/
```

## Disposition

Resolved by `SPEC-lifecycle-feedback-fixes` (AC-06): `CAP-DOCS-document-model` section 3.5 item 5 states that the
rule fix rewrites references in ADRs, PADRs and every spec bundle's `feedback/` files, that a rename's write scope
owns those paths (completed bundle files outside `feedback/` excepted), and names
`devkit docs refs <old-id> --direction in -n 0` to list them. The spec bundle's proposal template comments the
`excludes` example accordingly; `devkit sync` redeployed it. Verified by independent review against
`index.is_historical`, `RULE-document-reference` and `ADR-immutable-decisions-editable-records`, and by
`devkit sync --check` and `just rules-check`.
