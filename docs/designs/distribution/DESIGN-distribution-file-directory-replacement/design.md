---
id: DESIGN-distribution-file-directory-replacement
title: "File/directory replacement: the transaction mechanism"
status: active
area: distribution
summary: "Explains preflight, journal evidence, forward ordering and rollback for distribution file and directory replacement."
aliases: [DESIGN-distribution-transactions]
related_capabilities: [CAP-DIST-sync-and-transactions]
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/transaction.py
---

# [DESIGN-distribution-file-directory-replacement] File/directory replacement: the transaction mechanism

Letting a managed file become a directory, and the reverse, is a change-set problem: one deletion frees a path
another write needs, so the result depends on the ordering of deletions and writes. Rollback also has to tell prior
file content from directories the change set created or replaced, so it depends on the evidence the journal records.

## Preflight and the change set

In [transaction.py](../../../../packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/transaction.py),
`require_writable` checks each planned write against the owned paths this change set removes and the directories it
empties, and uses `blocked_parent` to tell a path freed by this change set from an obstruction. It returns the
directories that a file will replace, so both directions are part of the planned change rather than a blind
overwrite.

For a concrete file-to-directory shape, deleting the managed file `notes` permits writing `notes/SKILL.md`.
For the reverse shape, deleting the owned contents beneath `notes/` permits writing a file named `notes`.
The exact refusal conditions belong to `CAP-DIST-sync-and-transactions` §3.

## Forward application

`apply_changes` first calls `require_writable`, then orders the changes so that deletions come before writes.
It builds a journal with encoded `before` and `after` content for each changed path. For a replaced directory,
its file-shaped `before` is absent; the deleted child files supply their own snapshots.
`missing_directories` records parents that the writes would create, including a removed file that will become a
parent. The journal's `directories` also includes the replaced directories returned by `require_writable`.

`apply_changes` writes that journal before applying the ordered changes. For a directory-to-file replacement, the
now-empty directory is removed before the file write. `atomic_write` delegates each changed file to `replace_file`.
A caught application exception invokes `recover_locked`; a successful application removes the journal and prunes
empty owned parents left by deletions.

## Reverse application

`recover_locked` validates the journal and compares snapshots with its recorded before/after values, recognizing a
recorded directory swap. It prepares each path's previous content and orders removal of transaction-created content
before restoring prior content. Recorded created directories are removed only while empty. The implementation then
removes the journal.

## Authority boundary

`CAP-DIST-sync-and-transactions` §3 owns eligibility, admissible replacements, safety and recovery guarantees.
`ARCH-05-4-distribution-components` §3 locates the installation service that implements them.

## Update triggers

- `apply_changes`, `require_writable` or `recover_locked` change the deletion and write order, the journal fields
  (`before`, `after`, `directories`) or the rollback order.
- `CAP-DIST-sync-and-transactions` §3 changes which replacements are admissible.
