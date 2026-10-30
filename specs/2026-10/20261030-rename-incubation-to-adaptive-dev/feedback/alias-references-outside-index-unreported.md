---
id: FB-alias-references-outside-index-unreported
title: Alias references in docs/development, guides and READMEs are neither reported nor fixed
scope: repo
kind: friction
category: missing-capability
target: RULE-document-reference
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-alias-references-outside-index-unreported] Alias references in docs/development, guides and READMEs are neither reported nor fixed

## 1. Friction / Question (friction, question)

- **Context**: After moving six renamed documents with their old IDs in `aliases`, `devkit rules fix` rewrote the
  alias references in capabilities, use cases, ADRs and spec feedback, and `devkit rules check` reported no alias
  reference left.
- **Expectation**: `CAP-DOCS-document-model` (renaming step) says one `devkit rules fix` moves current documents to
  the new ID, and a clean `rules check` suggests no stale reference remains.
- **Actual**: Code-span references to an old ID stayed in `docs/development/reference/integration.md`, in a guide
  under `guides/install/` and in package README text, and plain-text old IDs stayed in feedback `target` fields;
  none was reported. Only a repository-wide `rg` found them.
- **Workaround (or Interpretation Chosen)**: Rewrote them by hand after an `rg` sweep for each old ID.
- **Suggestion**: Either name in the renaming step that files outside the document index (`docs/development/`,
  `guides/`, package READMEs) and plain-text IDs need a manual sweep, or extend the alias-reference check to the
  indexed repository's other Markdown files in report-only mode.

## Evidence

```text
base 0debf74f docs/development/reference/integration.md:91 ... See `CAP-DLV-proposal-incubation` and `CAP-INT-mcp-services`.
devkit rules check after rules fix: errors=0 warnings=0 (integration.md line unchanged)
guides/install/<adoption guide>:86 The current contract is `CAP-DLV-incubation-sdd-baseline` ... (unchanged by rules fix)
```

## Disposition

Resolved by `SPEC-alias-references-in-quick-references`: `RULE-document-reference` resolves the backtick-quoted IDs of
the quick references its `quick_references` setting matches (default `docs/development/**/*.md`, `guides/**/*.md`,
`packages/*/README.md`, `tools/*/README.md`); an unresolved ID is an error and an alias citation is fixable, so
`devkit rules fix` rewrites it. The four alias citations left in `docs/development/` and the viewer README were
rewritten, and the renaming step of `CAP-DOCS-document-model` names plain-text IDs and feedback `target` fields as
the remaining manual sweep (out of scope by the user's decision). Verified by the rule tests (check, fix and clean
recheck in all four default locations; unresolved IDs; masking, targets, exclusions and settings), a whole-workspace
`devkit rules check` with no finding and the `code-reviewer` pass (`review-01`, `reverify-01`).
