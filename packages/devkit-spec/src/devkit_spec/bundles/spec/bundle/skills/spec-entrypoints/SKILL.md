---
name: spec-entrypoints
description: Derive capability/story entrypoints from a spec bundle's tasks.md (_Boundary) and reconcile.md targets, review the candidates and write the chosen ones. Use during spec-sync, or across completed specs to backfill empty entrypoints.
---

# spec-entrypoints: Entrypoint Derivation and Sync

Use this skill when a spec bundle has both `tasks.md` and `reconcile.md` (normally inside `spec-sync`), or when capability/story documents lack `entrypoints` and completed specs can supply them. The command joins declarations mechanically; this skill supplies the review that decides what is written. Path contract: `devkit rules explain RULE-code-entrypoints`.

---

## 1. Inputs

- Code side: every `_Boundary` path in the bundle's `tasks.md` (`N/A`, globs, absolute paths and `docs/` or `specs/` paths are skipped).
- Document side: `reconcile.md` targets under `docs/capabilities/` or `docs/stories/` (also under `docs/packages/<name>/`) that are not `waived`.
- A candidate under another candidate of the same bundle is folded into the ancestor and never written.

---

## 2. Procedure for the current bundle

1. **Derive**: `devkit spec entrypoints derive --spec specs/<YYYY-MM>/<YYYYMMDD>-<slug>`; the `new=` paths of each `[CANDIDATES: <doc> ...]` line are what the review decides on.
2. **Review** before writing. Drop a document when the bundle touched it only for metadata or wording (its reconcile target is `modified`, but the code paths belong to another capability). Keep a directory candidate only when the document really owns that package; prefer the file-level candidate when a task's boundary was broad. A pair is a declaration join, not proof that the code implements that document.
3. **Apply** the chosen pairs only: `devkit spec entrypoints derive --spec <dir> --apply --target <CAP-or-US-id> --code <path> [--code ...]`. `--target` picks documents, `--code` keeps candidates equal to or under a path, `--exclude` drops hub paths every bundle touches (root `AGENTS.md`, `README.md`, agent guides). Without them every bearing target and candidate of the bundle is written. To declare a folded file instead of its directory, apply with `--all` (folding is per bundle) or edit the boundary. The command appends and is idempotent; follow the `[FIX]` of any warning.
4. **Verify**: `devkit rules check <document>` (`RULE-code-entrypoints` checks that every written path exists) and `devkit spec list capability --file <path>` (or `story`) for one written path: the document must be listed.
5. **Record**: a document whose `entrypoints` changed is a Living Spec change; make sure it is a `modified` target in the bundle's `reconcile.md` (or reported by a `session` task).

---

## 3. Backfill across completed specs

1. `devkit spec entrypoints derive --all` aggregates every `completed` and `in-progress` bundle; each path carries its spec count, `src/a.py(2)` (`--format json` for the spec IDs). Add `--status` to change the filter.
2. Choose a threshold from the distribution: `--min-count 2` keeps pairs two or more specs agree on and removes most one-off joins. Inspect the remaining `new=` paths per document; `--format json` helps when the list is long.
3. Apply per document so each decision is explicit: `devkit spec entrypoints derive --all --min-count <n> --apply --target <id> --code <path> ...`, adding `--exclude` for hub paths. Directories and files under them collapse to the directory. Then run `devkit rules check`.
4. Report which documents were filled and which stayed empty with the reason (`missing-path`, no candidates, candidates rejected in review). Backfill of many documents is a Living Spec change: record it through the current bundle's `reconcile.md` or the report of a `session` task.

---

## 4. Definition of Done

- [ ] Each written document was reviewed, not applied blindly from the full candidate list; `devkit rules check` passes.
- [ ] Rejected or deferred candidates are stated in the report when they matter later.
