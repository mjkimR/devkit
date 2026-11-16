# File/directory replacement: the transaction mechanism

**Reader question:** Which ordering and recorded evidence let a managed file become a directory, and the reverse?

This non-normative detail explains transaction.py at the pilot source revision.
`CAP-DIST-sync-and-transactions` §3 owns eligibility, safety and recovery guarantees.
For orientation, the [design entry](design-entry.md) locates this mechanism within distribution.

## Preflight and the change set

In [transaction.py](../../../../packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/transaction.py),
`require_writable` uses `_removed_owned`, `blocked_parent` and `_emptied` to distinguish a path freed by this
change set from an obstruction. It returns the directories that a file will replace. This makes both directions
part of the planned change rather than a blind overwrite.

For a concrete file-to-directory shape, deleting the managed file `notes` permits writing `notes/SKILL.md`.
For the reverse shape, deleting the owned contents beneath `notes/` permits writing a file named `notes`.
These names illustrate a change-set shape; they do not report a recovery run or introduce a new allowed destination.
The exact refusal conditions belong to the capability owner above.

## Forward application

`apply_changes` first calls `require_writable`, then `_ordered`, which groups deletions before writes.
It builds a journal with encoded `before` and `after` content for each changed path. For a replaced directory,
its file-shaped `before` is absent; the deleted child files supply their own snapshots.
`missing_directories` records parents that the writes would create, including a removed file that will become a
parent. The journal's `directories` also includes the replaced directories returned by `require_writable`.

`apply_changes` writes that journal before applying the ordered changes. For a directory-to-file replacement,
`_remove_emptied` removes the now-empty directory before the file write. `atomic_write` delegates each changed
file to `replace_file`. A caught application exception invokes `recover_locked`; a successful application removes
the journal and prunes empty owned parents left by deletions.

## Reverse application

`recover_locked` validates the journal and compares snapshots with its recorded before/after values, with
`_swapped_directory` recognizing a recorded directory swap. It prepares each path's previous content and orders
removal of transaction-created content before restoring prior content. `_prune_created` removes recorded created
directories only while empty. The implementation then removes the journal.

For a later edit or a legacy journal, next use `CAP-DIST-sync-and-transactions` §3 “Recovery”; its stop conditions
own the operational decision. This explanation is not a rollback procedure. No recovery command was executed.

## Maintenance seam

A change to deletion ordering calls for checking `_ordered`, `apply_changes`, `recover_locked` and this detail.
It does not itself change the domain relationship between selection and installed evidence. Revisit architecture
only if system interactions or component responsibilities change, and capability guarantees if their facts change.
