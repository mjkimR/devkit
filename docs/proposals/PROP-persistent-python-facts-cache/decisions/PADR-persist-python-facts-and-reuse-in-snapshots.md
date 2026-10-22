---
id: PADR-persist-python-facts-and-reuse-in-snapshots
title: Store Python facts per rule with read-only snapshot reuse
summary: For Python facts persistence, we use per-rule JSON memos with atomic working-tree writes and read-only snapshot reuse, to preserve fresh-run results, accepting hashing every input and cache misses on invalidation.
proposal: PROP-persistent-python-facts-cache
status: draft
created_at: 2026-10-22
---

# [PADR-persist-python-facts-and-reuse-in-snapshots] Store Python facts per rule with read-only snapshot reuse

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

Facts require a disposable memo that cannot change rule results. Document memo identity and safe storage are useful
precedents, but its writers exclude rule runs. Python facts need deliberate working-tree warming and snapshot
read-only borrowing to benefit commit gates without changing snapshot code or policy authority.

## 2. Decision Drivers

- Missing, corrupt or unwritable derived state never changes findings, advisories or exit status.
- Staged and CI snapshots execute their own code and source identities.
- No lock wait; unchanged runs write nothing; partial runs do not erase unseen entries.

## 3. Considered Options

- JSON per rule with atomic replace: simple safe decoding and independent invalidation; concurrent writers may lose hits.
- Per-entry files: isolate writes but create many small filesystem operations.
- Pickle or persisted ASTs: avoid record design but permit executable loading or couple storage to AST internals.
- No snapshot sharing: simpler authority boundary but temporary snapshots always miss host facts.

## 4. Decision Outcome

Choose per-rule JSON memos with atomic working-tree updates and read-only snapshot borrowing, as detailed in
`materials/design.md`. Use `.devkit/transient/rules/facts/<rule-id>.json` under an existing safe transient directory.
Validate format, fingerprint, entry identity and rule codec before reuse. Reject symlink components and escaped or
non-regular memo paths; never remove obstructing files. Validated rule IDs determine safe filenames.

Only explicitly enabled working-tree evaluations write, after fixes/rechecks; dry runs, library defaults and all
snapshot paths are read-only. This is a Python-facts policy difference from `ADR-parse-memo-failure-and-write-policy`,
which remains unchanged for documents. Full successful rule enumeration may prune; partial runs retain unseen paths.
Use lock-free atomic replacement; failures log only and unchanged payloads do not rewrite. Cache I/O/validation errors
are misses; extractor programming failures retain the existing evaluator failure semantics.

A snapshot keeps its evaluation workspace root. The project use case injects only the originating worktree's storage
root in read-only mode. Match snapshot source bytes and actual executing rule/helper fingerprints, after existing
receipt checks, including in-place staged execution. A miss extracts from the snapshot and writes no memo anywhere.
No cross-worktree cache is introduced. Deletion, rename and policy changes rebuild discovery and global judgment.

## 5. Consequences

- Cache deletion, concurrent lost updates and schema mismatches cost extraction, without a new user action.
- Working-tree checks gain ignored transient writes; this behavior must be documented in governance contracts.
- JSON schema validation provides safe loading, not authenticity of malicious well-shaped local edits. The memo is
  trusted local derived state, matching the document memo model; adversarial cache authentication is excluded.
- Complete-process performance remains unverified until Development measures real records and snapshot overhead.

## 6. Confirmation

Proposal AC4–AC5 exercise corruption, schema/fingerprint changes, path containment, symlinks, concurrent writers,
partial/full pruning, no-op writes and materialized/in-place snapshots with divergent unstaged code and source.
AC7 reports fresh-process disabled/cold/warm timings; synthetic JSON decoding is not completion evidence.
