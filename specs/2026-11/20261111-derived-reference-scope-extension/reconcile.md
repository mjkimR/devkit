---
reconcile_id: REC-derived-reference-scope-extension
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-roles.md
    resolution: modified
  - file: docs/decisions/2026-11/20261111-derived-reference-documents-as-worker-scope-extensions.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-recorded-adjacent-path-extensions-for-development-workers.md
    resolution: modified
---

# Reconcile: `SPEC-derived-reference-scope-extension`

## Living Spec changes

- `CAP-DLV-delivery-roles` (Tier B rule): an exact existing derived reference document qualifies, namely a quick
  reference (`docs/development/reference/`), a user guide (`guides/`) or the README of a package or tool owning a
  changed source, when its edited passages restate a changed public name, command or behavior. The reason names that
  symbol, command or contract ID; the edit adds no document or section. Agent instruction files, bundle and agent
  assets and release documents do not qualify. The inspection paragraph's list of recognizable protected classes now
  names agent instruction files (`AGENTS.md`, `CLAUDE.md`), which `protected()` already rejected.
- `ADR-derived-reference-documents-as-worker-scope-extensions` records the decision and supersedes in part
  `ADR-recorded-adjacent-path-extensions-for-development-workers`, which carries the identical pointer statement and
  stays accepted.

## No impact

- `UC-drive-development-to-integration`: its steps say each task is implemented within its boundary without
  listing the Tier B classes, so no step, extension or postcondition changes.
- `CAP-DLV-workflow-envelopes`: the `scope_extensions` record format is unchanged.
- `docs/development/reference/`, `guides/` and package READMEs restate no Tier B class.

## Entrypoints

`devkit spec entrypoints derive` proposed two bundle references and two test files for `CAP-DLV-delivery-roles`;
all are rejected as non-doorway files. The worker role it already declares stays its doorway.

## Source feedback

- `FB-core-reference-row-for-memo-helper` is `resolved` (terminal); it is cited as evidence only and gets no
  disposition.

## Deferred work

None.
