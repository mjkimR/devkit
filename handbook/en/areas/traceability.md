---
sources:
  CAP-DLV-drift-reconciliation: 25e499e1a6d18c0d65be1855cfe8bd3925f2d1c6
  CAP-DOCS-document-lookup: d908536d3cc6b3c3676c21f0858e5fd4d416cca6
  CAP-TRACE-code-entrypoints: 3b8cb1476d9102bf09e6ffc6a469c3e00e58da97
  UC-keep-the-living-spec-consistent: 7ebdf1e2f7ae6581fa9140d1898d755de57b5667
  UC-run-parallel-work-safely: eb22803d64e8af4f3479c6c935942508db14f5cf
title: Traceability
---

# Traceability

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `ae01161143be`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

Traceability links Living Spec documents to code. A capability or use case can declare `entrypoints`: the files
and directories where its implementation starts. That one field lets you go from a document to its code, from a
code path back to its documents, and lets the commit gate notice when code disappears under a document. The
contract is
[CAP-TRACE-code-entrypoints](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md).

An entrypoint is where reading starts, not a complete list of the implementation and not proof that the code does
what the document says. Coverage and correctness stay with tests and review. The Living Spec and its documents are
introduced in [Concepts](../concepts.md).

## Declare entrypoints

```yaml
entrypoints:
  - src/example/engine.py
  - src/example/cli/
```

- Only Markdown files under `docs/capabilities/` and `docs/usecases/` (and the same directories of a namespace root
  `docs/packages/<name>/`) carry the field.
- Paths are literal and workspace-relative with `/`, also for namespace documents; never package-relative. Files and
  directories are both fine.
- No absolute paths, `..`, backslashes, drive colons or glob characters. Comparison is by whole segment and
  case-sensitive: `src/a` covers `src/a/b.py`, not `src/ab`.

The same path contract applies to the code paths of the work-scope registry, which is how parallel tasks see that
they touch the same code; see [Run parallel work safely](../journeys/run-parallel-work-safely.md)
(`UC-run-parallel-work-safely`).

## Find the documents that own a path

Before you change a file, ask which documents claim it:

```bash
uv run devkit spec list capability --file src/engine/
uv run devkit spec list usecase --file src/engine/parse.py
```

It lists documents whose entrypoints equal the path, lie under it, or are a directory containing it. The path
need not exist, so a file you just deleted still finds its documents. A path that breaks the contract fails with
`SPEC_ENTRYPOINTS_PATH_INVALID` before any document is read. The rest of `devkit spec list` is described in
[Documents](documents.md) and `CAP-DOCS-document-lookup`.

## Keep declarations alive

`RULE-code-entrypoints` (linter phase, severity error, not fixable) checks that every declared path is a valid,
existing file or directory inside the workspace. In a commit gate or CI run it reads the snapshot's tree, and it
also reports every current document that declares a path the diff deletes. So deleting code without touching its
document fails the gate.

When it fires, decide what happened; the rule never guesses:

- the code moved: point the declaration at the new place;
- the code was removed on purpose: remove the obsolete declaration;
- the deletion was a mistake: restore the code.

This is part of [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
(`UC-keep-the-living-spec-consistent`). Entrypoints also help the manual drift sweep of
`CAP-DLV-drift-reconciliation` locate evidence, but a passing path check never proves that a document is current.

## Derive declarations from finished specs

A spec bundle already names both sides of the link: `tasks.md` lists the code each task may touch on its
`_Boundary` lines, and `reconcile.md` lists the Living Spec documents the change reconciled.
`devkit spec entrypoints derive` joins them into document-path pairs.

```bash
uv run devkit spec entrypoints derive --spec <bundle-dir>     # one bundle, nothing written
uv run devkit spec entrypoints derive --all --min-count 2      # backfill across bundles
uv run devkit spec entrypoints derive --spec <bundle-dir> \
  --apply --target <ID> --code src/engine/                     # write the chosen ones
```

How to use it well:

1. Run it without `--apply` first. Each `[CANDIDATES: ...]` line shows one document with its paths by state: `new`,
   `missing`, `folded` (covered by a shorter candidate) or `declared`.
2. Review before applying. A bundle that touched a capability only for wording still pairs it with every path its
   tasks named. Drop such documents, keep directory candidates only for documents that own the package, and
   `--exclude` hub files that every bundle touches. The `spec-entrypoints` skill carries this review; `spec-sync`
   runs it on the current bundle.
3. Apply per document with `--apply --target <ID>` and `--code <path>`. Only the `entrypoints` block of the
   frontmatter is rewritten, every other byte is kept, and a rerun writes nothing.

Use `--all` with `--min-count` to backfill older documents: a pair produced by several specs is a stronger
candidate. Error codes and the full option list are in the contract.
