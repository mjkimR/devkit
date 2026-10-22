---
reconcile_id: REC-frontmatter-libyaml
status: resolved
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
---

# Reconciliation: `SPEC-frontmatter-libyaml`

## Contract reflection

`CAP-DOCS-document-model` section 3.1 records optional libyaml parsing, unchanged types and duplicate checks,
Python routing for scanner-sensitive characters and deep syntax, original Python error diagnostics, and the no-libyaml fallback.
No CLI, use-case sequence, dependency, architecture or glossary term changes.

## Source feedback

`FB-strict-frontmatter-loader-without-libyaml` is directly addressed by the implementation and its tests.
The Disposition in the source records the checks and measured benefit. No required work is deferred.

## Entrypoints

Keep the existing document feature entrypoint and add the shared frontmatter module as its grammar doorway.
Exclude the test module and performance evidence from entrypoints.

## Reconcile verification

Self-verified at medium effort: only one application-independent core module changes behavior and one capability
reflects that behavior. No cross-component behavior changes or unresolved interpretation remain. Compared the
parser guard, syntax-depth routing, error retry and loader absence with every reflected sentence and AC-01 through
AC-05. The independent code review and its P1 reverify passed. Test and benchmark evidence is in evidence.md.
