---
reconcile_id: REC-shared-fingerprinted-memo
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
---

# Reconcile: `SPEC-shared-fingerprinted-memo`

## Living Spec impact

- `CAP-DOCS-document-model` 3.4.3: the path sentence ("not used when a symbolic link is at `.devkit/transient/`,
  `docs/` or the file, or the file resolves outside the root") is replaced by the converged rule: the memo is used
  only on the safe memo path shared with the rule facts memo (`devkit_core.core.memo`), with no symbolic link,
  non-directory or directory that resolves elsewhere at any component from `.devkit/` down and a regular file or none
  at the path; a writing load creates a missing `docs/`; a memo with any top-level key besides `version`,
  `fingerprint` and `entries` is discarded (already the docs behavior, now stated) ([AC-03], [AC-06]). 3.4.4 and
  3.4.5 are unchanged: the writer rule, the one-line logging, the non-regular file left in place and the silent
  creation of a missing memo all hold (`evidence/after.md`).
- `CAP-GOV-rules-engine` 5.3: "an existing safe `.devkit/transient/`, rejecting symlinks and non-regular memo
  components" is restated as the same shared rule, which readers also apply; the memo format paragraph now says the
  format is exactly `version`, `fingerprint` and `entries` and a memo with another top-level key is discarded
  ([AC-04], [AC-06]). 5.1, 5.2, 5.4 and 5.5 are unchanged; the cold first run after the change is covered by 5.2
  ("incompatible" memo) ([AC-05]).

## No impact

- `ADR-document-system`, `ADR-rules-run-workspace-cache` and the other memo decisions: the memo locations, file
  formats, format versions and writer policy do not change; the path and envelope strictness converged under decision
  D1 is a contract detail restated in the two capabilities, so no ADR changes.
- `ARCH-05-2-components` and `.devkit/architecture.toml`: the new module lives in `devkit_core.core`, imports only the
  standard library, and both callers already import `devkit_core.core`; no package or feature edge changes.
- No use case changes: no command's output, exit status or advisory changes; only `-v` `info` lines of the docs memo
  change for the D1 layouts.

## Entrypoints

`devkit spec entrypoints derive` proposed 15 new pairs for the two capabilities (the new helper, the other memo
module, `facts.py` and test files); none is written. Tests are never doorways, the helper is shared by both and owned
by neither, and each capability changed by one clause; `CAP-DOCS-document-model` already declares the docs memo
module.

## Source feedback and deferred work

- No source feedback was carried from the proposal.
- `FB-core-reference-row-for-memo-helper`: `docs/development/reference/core.md` (a quick reference outside this
  Unit's write scope) has no row for `devkit_core.core.memo`; recorded for the Host.
