---
sources:
  CAP-DLV-drift-reconciliation: 25e499e1a6d18c0d65be1855cfe8bd3925f2d1c6
  CAP-DOCS-document-lookup: f16d8d88730261a376acc66ccb8e11ce209d4b49
  CAP-TRACE-code-entrypoints: 71c9a300749a114f5dd4141e70aee300dcafd4ee
  UC-keep-the-living-spec-consistent: 6aa78b77ed1eb5a1f7f8b59742048c01319abccc
  UC-run-parallel-work-safely: f60eea1f7ddb44d8d4d47058e2777990f1a50d64
title: Traceability
---

# Traceability

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `022b9f03bbd2`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

Traceability links Living Spec documents to code. A capability or use case can declare `entrypoints`: the files
and directories where its implementation starts. That one field lets you go from a document to its code, from a
code path back to its documents, and lets the commit gate notice when code disappears under a document. devkit-docs
owns the path contract, the rule and the reverse query; devkit-spec adds the derivation from spec bundles. The
contract is
[CAP-TRACE-code-entrypoints](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md).

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

The same path contract applies to the code paths of work-scope comparison, which is how the Host sees that parallel
tasks touch the same code; see [Run parallel work safely](../journeys/run-parallel-work-safely.md)
(`UC-run-parallel-work-safely`).

## Find the documents that own a path

Before you change a file, ask which documents claim it:

```bash
uv run devkit docs list capability --file src/engine/
uv run devkit docs list usecase --file src/engine/parse.py
```

It lists documents whose entrypoints equal the path, lie under it, or are a directory containing it. The path
need not exist, so a file you just deleted still finds its documents. A path that breaks the contract fails with
`DOCS_ENTRYPOINTS_PATH_INVALID` before any document is read. The rest of `devkit docs list` is described in
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
   `missing`, `folded` (covered by a shorter candidate) or `declared`. Documents are paged 20 at a time
   (`--limit`, `--offset`, with a `[NEXT_CMD: ...]` for the next page), and skipped inputs are counted per reason
   (`[SKIPPED_COUNT: ...]`; `--skipped` lists each one).
2. Review before applying. A bundle that touched a capability only for wording still pairs it with every path its
   tasks named. Drop such documents, keep directory candidates only for documents that own the package, and
   `--exclude` hub files that every bundle touches. The `spec-entrypoints` skill carries this review; `spec-sync`
   runs it on the current bundle.
3. Apply per document with `--apply --target <ID>` and `--code <path>`. A `--code` path may also name a folded
   candidate (to write it as is) or a file under a directory candidate (a doorway file). A `--code` path that matches
   no candidate refuses the whole run with `SPEC_ENTRYPOINTS_CODE_UNMATCHED` before anything is written, so a typo
   never lets the other selections slip through. Only the `entrypoints` block of the frontmatter is rewritten, every
   other byte is kept, and a rerun writes nothing. Paging never limits what `--apply` writes.

Use `--all` with `--min-count` to backfill older documents: a pair produced by several specs is a stronger
candidate. Error codes and the full option list are in the contract.
