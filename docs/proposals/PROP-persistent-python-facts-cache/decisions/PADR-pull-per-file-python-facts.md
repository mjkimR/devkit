---
id: PADR-pull-per-file-python-facts
title: Pull per-file Python facts through WorkspaceCache
summary: For repeated Python rule checks, we pull rule-owned JSON facts through WorkspaceCache keyed by source bytes and extractor inputs, to reuse extraction across processes, accepting explicit dependency declarations.
proposal: PROP-persistent-python-facts-cache
status: draft
created_at: 2026-10-22
---

# [PADR-pull-per-file-python-facts] Pull per-file Python facts through WorkspaceCache

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

Python rules retain ASTs in memory but start cold in every process. The three target rules own their discovery and
cross-file judgments. Their current AST use includes facade bindings, inherited advisory constants and transport
callback scopes; a list of imports/classes cannot preserve all their behavior.

## 2. Decision Drivers

- Results equal cache-disabled evaluation after source, configuration and cross-file edits.
- Existing rule discovery, selection and direct library callers retain one evaluation path.
- Helper edits and editable installations invalidate persisted extraction without manual release bumps.

## 3. Considered Options

- Keep shared ASTs only: lowest complexity, no extraction reuse across processes.
- Add an evaluator lifecycle hook: central scheduling, but the engine must learn rule-specific file sets and context.
- Pull rule-owned facts from WorkspaceCache: preserves rule composition, requires explicit schemas and dependencies.

## 4. Decision Outcome

Choose the pull descriptor in `materials/design.md`. The rule supplies a typed extractor/codec, schema version and
source dependencies; `WorkspaceCache` owns identity and retention. The key uses logical relative path, exact cached
Python bytes, explicit canonical extraction context and a source-derived fingerprint. Hash the read/AST/codec
framework path, actual extractor/helper sources and Python runtime; unreadable dependencies disable persistence.

Extractors produce immutable rule-owned syntax/scope records, never AST objects or resolved cross-file judgments.
Configuration/settings resolution stays in judgment for the three migrated rules. Shared ASTs remain read-only under
`ADR-share-one-read-only-parsed-tree-per-python-file` and nodes retain their existing order under
`ADR-index-python-ast-nodes-by-type-in-workspacecache`. Preserve source positions, scope and declaration ordering.
Invalidation drops affected extracted facts and cross-file computed state; fresh byte/context validation guards
later reuse. Extractor failures retain their existing behavior and are not saved as successful facts.

## 5. Consequences

- Warm runs skip extraction; discovery, source reads/hashes and global judgments still run.
- Advisory and usecase consumers require explicit scope/expression records and equivalence coverage, adding more
  refactoring than the synthetic benchmark assumes. Development remains medium with cross-component reviews.
- Dependency completeness and facts immutability are reviewable contracts, not runtime sandbox guarantees.
- No BaseRule requirement, new CLI flag, automatic import dependency walker or persistent final violation cache.

## 6. Confirmation

Proposal AC1–AC3 and AC6 compare full judgments, source encodings, cross-file edits and invalidation against disabled
execution. Unit tests assert each descriptor's expected source dependency set and changes to helpers invalidate it.
Rule tests assert warm extraction makes no AST/node acquisition calls. Review matches every prior AST-consuming
branch to a typed fact operation before migration is declared complete.
