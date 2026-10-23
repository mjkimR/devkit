---
reconcile_id: REC-persistent-python-facts-cache
status: resolved
targets:
  - file: docs/decisions/2026-10/20261022-pull-per-file-python-facts.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-persist-python-facts-and-reuse-in-snapshots.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    resolution: modified
  - file: docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md
    resolution: modified
  - file: docs/development/reference/rules-library.md
    resolution: modified
  - file: docs/glossary.md
    resolution: modified
---

# Reconciliation: `SPEC-persistent-python-facts-cache`

## Contract reflection

- `CAP-GOV-rules-engine` owns identity, derived-state failures, safe atomic stores, writer authority and bounded pruning.
- `CAP-GOV-rule-authoring` owns the pull descriptor/source API, immutable file-local extraction, provenance and strict codecs.
- `CAP-GOV-evaluation-lifecycle` owns post-recheck flushing, invalidation and read-only snapshot borrowing with snapshot identities.
- `CAP-ADV-agent-advisory-protocol` records syntax-only reuse while current inheritance, constants and settings remain judgment inputs.
- The library reference documents the supported controls and authoring entrypoints; the glossary registers per-file rule facts.
- The architecture, usecase-boundaries and advisory rule guides mirror the persistence and failure behavior.

The two accepted ADRs were promoted by the inherited approved handoff and are additions in the cumulative branch diff; both are targets here. Development retains their decisions. Existing document memos, shared AST immutability, rule selection,
receipt verification and public advisory/CLI runtime APIs retain their contracts; no additional contract target is needed.
Incoming-reference checks covered current governance, gate, distribution, workflow and worktree documents. Their
selection, receipt and authority promises are unchanged. Completed specs remain history.

## Verification

Independent code review found and verified fixes for impossible call/attribute records. Warmed-memo corruption
regressions prove fallback preserves complete findings. Snapshot tests cover in-place and materialized staged runs,
CI snapshots and divergent unstaged source, rule and helper code. Performance evidence is preserved in
`docs/materials/2026-10/20261022-persistent-python-facts-cache/`.

## Deferred work

No required acceptance criterion is deferred. Other Python rules, shared worktree caches, persisted ASTs and
judgments remain the approved non-goals rather than retained follow-up scope.

## Entrypoints

Broad directory and test candidates were rejected as reading doorways. The existing engine/public API and
rule-authoring cache entrypoints remain sufficient. Lifecycle adds project orchestration; advisory adds its
static uniqueness rule. Task 2, 4 and 6 boundaries name their concrete implemented files so derive can select
the doorway files rather than broad directory candidates.

The inherited handoff retires the accepted proposal after preserving its investigation in dated materials and its
records in the feature unit. Those historical material moves and retired proposal files change no additional
current contract. The Development baseline, preliminary measurements and final measurements are historical
evidence, not separate Living Spec capabilities.
