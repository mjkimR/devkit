---
reconcile_id: REC-crlf-selection-and-viewer-probes
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/development/reference/viewer.md
    resolution: modified
---

# Reconciliation: `SPEC-crlf-selection-and-viewer-probes`

- `CAP-DIST-sync-and-transactions` (Commented Template, **Selection edits**): the edit follows the line-ending rule of
  **Append-only**: existing lines keep their bytes, line endings included, and added lines end in CRLF when every line
  ending of the file is CRLF, and in LF otherwise (AC-01, AC-02). The paragraph named only where an entry goes.
- `docs/development/reference/viewer.md` (Frontend): names `just viewer probe <abs-dir> [vitest args]` and states what
  it collects, how it resolves imports, the temporary config it removes and its exit codes `1` and `2` (AC-03, AC-04).

The `code-reviewer` role contract's probe sentence names the command for a viewer frontend change (AC-05); it is
bundle guidance with no Living Spec statement. `docs/development/reference/distribution.md` needs no change: its
`devkit add` row states no file formatting, and its `devkit config template` row already states the rule.
`docs/development/setup.md` lists the everyday frontend commands and points to the viewer reference for the rest;
the review-only probe action stays in the reference. No use case describes selection-edit line endings or review
probes; no architecture, ADR or glossary impact.

## Entrypoints

`devkit spec entrypoints derive --spec` joins the boundaries with the targets; no pair is written. `config.py` is
already declared for `CAP-DIST-sync-and-transactions`; the reference page is not a capability or use case, and the
other candidates are tests, a script, guidance sources, a sync output and feedback files, not doorways.

## Source feedback

Resolved with a Disposition: `FB-selection-edits-rewrite-crlf-line-endings` and
`FB-viewer-review-probes-outside-vitest-include`.

## Deferred work

None.
