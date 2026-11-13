---
reconcile_id: REC-snapshot-subdirectory-source-commit
status: resolved
targets: []
---

# Reconciliation

## Impact comparison

No canonical document change is required. The source diff adds only `--full-tree` to the repository helper's
existing `ls-tree` call. It restores repository-relative lookup under a subdirectory provider while preserving the
captured immutable commit, copied bytes/executable modes, timeout and failure-to-null result.

`CAP-DIST-in-repo-bundles` section 8 rules 4–7 and 10 already require verified optional identity, path-independent
provenance, read-only preview, reviewed digest adoption and no writes for unchanged metadata/content.
`UC-snapshot-bundle-sources` already describes the same explicit snapshot/refresh operations. Their API entrypoints,
schema, result codes, user actions and architectural ownership are unchanged. Root-provider and captured-HEAD
regressions pass alongside the added subdirectory byte/mode and metadata-only refresh cases.

The blueprint `PROP-snapshot-subdirectory-source-commit-target` deliberately declares no canonical targets. The
actual diff agrees. Entrypoint derivation has no document-code pair because no capability/use case target changes;
the existing repository helper is not a new public doorway.

## Verification

Low-effort self-review at source `059f2926a7aafa2ceea121648f9e9ffa02f4e83f` found no defects. Snapshot integration
43 passed, independent dist-only 1413 passed, affected tests across all tiers 3327 passed and 1 skipped. Lint,
types and cumulative rules passed. Red and Green evidence retain the subdirectory reproduction as regression tests.

No agreed acceptance criterion is deferred. No source feedback was named for this fix and no follow-up feature is
required. The preserved Planning material is historical evidence and introduces no Living Spec contract.
