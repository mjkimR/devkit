---
name: spec-entrypoints
description: Derive, review and write core-eligible document entrypoints from a spec's tasks.md and reconcile.md, during spec-sync or as a backfill across completed specs.
---

# spec-entrypoints: Entrypoint Derivation and Sync

`devkit spec entrypoints derive` joins `_Boundary` paths with non-waived `reconcile.md` targets; you choose the pairs
to write. Path contract: `devkit rules explain RULE-code-entrypoints`. To fill empty entrypoints across completed
specs, read [backfill](references/backfill.md) instead.

## Procedure for one bundle

1. Run `devkit spec entrypoints derive --spec <dir>`; candidates are the `new=` paths of each
   `[CANDIDATES: <doc> ...]` line.
2. Review:
   - Drop a document the bundle touched only for metadata or wording.
   - For CAP/UC, keep 1–3 doorway files per document, where reading starts (`cli.py`, `usecase.py`, `service.py`, `index.ts`,
     `__init__.py`); not helpers, models, schemas or tests.
   - For DESIGN, select useful mechanism file/directory anchors, including helpers/models/schemas when they are
     the subject's reading start; entrypoints do not prove correctness or public adapter standing. Consume core
     eligibility; DOMAIN/OPS and README/artifact paths are ineligible and produce no pairs.
   - For CAP/UC, use a directory (trailing `/`) only when the document owns the whole package, never a broad shared directory.
   - For DESIGN, use a directory when it bounds the described mechanism, excluding unrelated shared directories.
3. Apply only the chosen pairs:
   `devkit spec entrypoints derive --spec <dir> --apply --target <eligible-document-id> --code <path> [--code ...]`, with
   `--exclude` for hub paths (`AGENTS.md`, `README.md`). Without `--target` and `--code` it writes every candidate.
4. Record each document whose `entrypoints` changed as a `modified` `reconcile.md` target, or in a `session` task's
   report.

## Completion

- [ ] `devkit rules check <document>` passes, and `devkit docs list capability --file <path>` (or `usecase` / `design`) lists the
  document for a written path.
- [ ] The report states rejected candidates that matter later.
