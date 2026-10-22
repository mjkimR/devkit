---
reconcile_id: REC-document-index-cache
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: modified
---

# Reconciliation

`CAP-DOCS-document-model` now states that the index is built from the files on every load and reuses a file's parse
result only for the same path and text, also between processes. Its Non-Goal changes from "a persistent cache or
database of documents" to "a persistent source of truth", as `ADR-content-keyed-document-parse-memo` decided.
Section 3.4 gains the parse memo (key, fingerprint, location, symbolic-link refusal, safe deletion), the write
policy (walk loads with the default reader only, only on change, atomic replace without a lock) and its silence
(fresh build, no advisory or exit-status change, one `-v` log line; a missing memo is created without one). Rules
3.4.3 to 3.4.5 are new; the resolution, reference-query and rewriting rules keep their text as 3.4.6 to 3.4.8, and
no document cites them by number. `CAP-DOCS-document-lookup` notes that `resolve`, `refs` and `list` load the index
through the memo and that the memo changes no argument, output, code or exit status.

No other Living Spec document changes:

- `CAP-GOV-spec-rules` 3.2 rule 1 stays true: the rules still read documents through the run's workspace cache;
  the memo only reuses parse results for the exact texts that cache returns, and those loads never write it.
- `CAP-DOCS-document-search` and `UC-find-the-right-documents` describe results, not how the index is loaded;
  no step, extension, postcondition or code changes.
- `CAP-DIST-workspace-ownership` and `ARCH-07-deployment` list devkit-dist's own `.devkit/transient/` files and
  already omit other packages' entries (`work/`, `mcp/`); the memo follows that convention (spec Assumption 3).
- No architecture invariant changes, and no domain term is introduced: "parse memo" is an implementation term of
  the documents feature, defined where it is used.
- The three ADRs were accepted in Planning and are implemented as decided; no ADR changes.

## Entrypoint review

`CAP-DOCS-document-model` already lists `packages/devkit-spec/src/devkit_spec/features/documents/`, which owns the
new `repositories/memo.py`. `CAP-DOCS-document-lookup` lists the lookup commands' module, which did not change. No
entrypoint is added; the derivation candidates are recorded in the `reconcile-check` envelope.

## Source feedback and retained follow-up

No source feedback is addressed. `FB-strict-frontmatter-loader-without-libyaml` stays open: a faster strict loader
is Non-Goal 2 of `SPEC-document-index-cache`. The stat-signature fast path that
`ADR-content-keyed-document-parse-memo` names as a possible follow-up is conditional on measurements of larger
workspaces, not retained work; this Unit's evidence (`materials/speed.md`) shows the walk and reads as most of the
warm time, which is where that decision would start.
