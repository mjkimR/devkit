---
reconcile_id: REC-steering-alias-autofix
status: pending
targets:
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
---

# Reconciliation: `SPEC-steering-alias-autofix`

## Contract comparison

`CAP-GOV-spec-rules` section 3.3 and the rule inventory state that steering code-span aliases and glossary Owner
aliases are fixable, preserving delimiters and layout. The implementation's `_steering` and `_glossary` mark
only uniquely resolved aliases fixable; `fix`, `_rewrite_citations` and `_rewrite_owners` write through the cache.
The shared `_owners` extraction takes table boundaries from original source and matches references in masked
visible lines, keeping canonical/missing/ambiguous IDs and bracket references outside Owners unchanged.
The deployed rule guide gives the same scope and remediation.

`CAP-DOCS-document-model` already states that these ID-free inputs use the cache and remain unindexed without
graph edges; no model contract changed. `UC-keep-the-living-spec-consistent` already describes unambiguous,
targeted byte repairs and manual remediation of missing or ambiguous IDs; its operation remains accurate.
No architecture, naming, UI or lasting policy decision changed.

## Source feedback

`FB-steering-citations-not-fixable` is resolved by the verified direct implementation, including both Owner
reference delimiters. Dedicated suite 47 and affected suite 2140 pass. Independent code review found one P2
column shift; original-source delimiter handling and three regressions resolve it, recorded in reverify-01.

## Verification and retained work

The before/after probe loads 7e0f153d code in memory without checking out the base: baseline leaves two aliases
and two files unchanged; head repairs both files with no findings. Targeting, exclusions, masking, delimiter and
layout preservation, ambiguous aliases, canonical IDs and second-run convergence have deployed regression tests.
A transient unrelated scope history ordering assertion is retained as `FB-scope-history-ordering-intermittent`;
its isolated rerun and subsequent affected suite pass. No required scope was deferred.

At medium effort, self reconciliation is used: one package and one capability area, all contract changes identified
above, and exact implementation/test agreement shown. No cross-component behavior or unresolved interpretation.

Entrypoint derivation already recognizes the governance use case through the capability's existing governance
directory. Reject `.devkit/installation.json` and the bundle rule directory as entrypoints: they are receipt/content
support rather than the operation's doorway. Keep existing entrypoints unchanged.
