---
name: spec-entrypoints
description: Derive capability/use case entrypoints from a spec bundle's tasks.md (_Boundary) and reconcile.md targets, review the candidates and write the chosen ones. Use during spec-sync, or across completed specs to backfill empty entrypoints.
---

# spec-entrypoints: Entrypoint Derivation and Sync

The command joins `_Boundary` paths with non-waived `reconcile.md` targets; this skill decides which pairs are
written. Path contract: `devkit rules explain RULE-code-entrypoints`. To fill empty entrypoints across completed specs,
read [backfill](references/backfill.md) instead.

## Procedure for one bundle

1. Run `devkit spec entrypoints derive --spec <dir>`; the `new=` paths of each `[CANDIDATES: <doc> ...]` line are the
   candidates.
2. Review:
   - Drop a document the bundle touched only for metadata or wording.
   - Keep 1–3 doorway files per document: where reading starts (`cli.py`, `usecase.py`, `service.py`, `index.ts`,
     `__init__.py`), not helpers, models, schemas or tests.
   - Choose a directory (trailing `/`) only when the document owns the whole package; never a broad shared directory.
3. Apply the chosen pairs only:
   `devkit spec entrypoints derive --spec <dir> --apply --target <CAP-or-UC-id> --code <path> [--code ...]`, with
   `--exclude` for hub paths (`AGENTS.md`, `README.md`). Without `--target` and `--code` it writes every candidate.
4. Record each document whose `entrypoints` changed as a `modified` target in `reconcile.md`, or in a `session`
   task's report.

## Completion

- [ ] `devkit rules check <document>` passes, and `devkit docs list capability --file <path>` (or `usecase`) lists the
  document for a written path.
- [ ] The report states rejected candidates that matter later.
