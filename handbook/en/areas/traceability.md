---
sources:
  CAP-DLV-drift-reconciliation: 4666e8d6bab265e18b275ce59b5f7d32b904a6d7
  CAP-DOCS-document-lookup: d03d09297497506274e7e0e69adf4ac9958b3b2e
  CAP-TRACE-code-entrypoints: 5df9001f75de5efa05627e963763935bb184a6f0
  UC-keep-the-living-spec-consistent: 3a6a41d611a4ad3d32ed0c3ba96efa1babf02128
  UC-run-parallel-work-safely: 0d974e0c636645b44666c8442980b3c83f3bdf72
title: Traceability
---

# Traceability

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.7` at source commit `c03315d43325`, generated 2026-11-17. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

Traceability links Living Spec documents to code. A capability, use case or canonical DESIGN document can declare `entrypoints`: the files
and directories where its implementation starts. That one field lets you go from a document to its code, from a
code path back to its documents, and lets the commit gate notice when code disappears under a document. devkit-docs
owns the path contract, the rule and the reverse query; devkit-spec adds the derivation from spec bundles. The
contract is
[CAP-TRACE-code-entrypoints](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md).

An entrypoint is where reading starts, not a complete list of the implementation and not proof that the code does
what the document says. Coverage and correctness stay with tests and review. The Living Spec and its documents are
introduced in [Concepts](../concepts.md).

## Declare entrypoints

```yaml
entrypoints:
  - src/example/engine.py
  - src/example/cli/
```

- Capabilities, use cases and canonical `design.md` anchors under `designs/<area>/DESIGN-<slug>/` can carry the field, including in namespace roots. DOMAIN and OPS documents and support files cannot.
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

### Keep generated paths out of derived entrypoints

Derivation skips `.devkit/managed/`, `.devkit/installation.json` and receipt-owned outputs, even when a task boundary
names them. Fully managed directories are excluded; mixed directories, ignored authored code and project-owned seeded
paths stay eligible. Managed outputs still belong to work-scope observation: this exclusion affects entrypoint derivation only.
A malformed present receipt raises `RECEIPT_INVALID`. An explicit managed `--code` selection is unmatched, not admitted.
