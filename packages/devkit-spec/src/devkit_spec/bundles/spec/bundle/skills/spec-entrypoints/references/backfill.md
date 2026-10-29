# Backfill entrypoints across completed specs

Apply the review rules of `SKILL.md` step 2 to the aggregated candidates.

1. Run `devkit spec entrypoints derive --all`. Each path carries its spec count, `src/a.py(2)`; `--format json` lists
   the spec IDs, `--status` changes the bundle filter.
2. Default to `--min-count 2` (pairs two or more specs agree on).
3. Apply per document:
   `devkit spec entrypoints derive --all --min-count <n> --apply --target <id> --code <path> ...`, with `--exclude`
   for hub paths.
4. Run `devkit rules check`, and report which documents were filled and which stayed empty with the reason
   (`missing-path`, no candidates, rejected in review). Record the change through the current bundle's
   `reconcile.md` or a `session` task's report.
