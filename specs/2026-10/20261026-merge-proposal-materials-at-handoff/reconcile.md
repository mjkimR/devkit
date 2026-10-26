---
reconcile_id: REC-merge-proposal-materials-at-handoff
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
---

# Reconciliation: Merge existing proposal materials during handoff

`CAP-DLV-proposal-incubation` states the merge decided by `ADR-merge-proposal-materials-per-leaf-at-handoff`:

- Rule 4 no longer refuses the dated materials directory for existing; a merge conflict with it is
  `SPEC_PROPOSAL_TARGET_EXISTS`.
- Rule 5 adds that the roll-back never moves, removes or records a path that existed before the handoff, on one
  file system or across file systems.
- Section 4.5, step 5 gains the merge rules (`lstat` containment, descent into shared real directories, whole moves
  of absent subtrees holding material, junk dropped on the proposal side and ignored on the destination side,
  byte-identical duplicates, the four collision kinds, the refusal's target, details and fix) and the residual window
  for a same-path write between preflight and move; the roll-back paragraph after the steps says every pre-existing
  path stays byte-identical.
- Section 4.7 says merged leaves and whole-moved subtrees resolve links from where they were written, pre-existing
  files from where they are, and a link to a dropped duplicate reaches the kept file.
- Section 4.10 lists `[MATERIALS: <dir> merged=yes]`, `[DROPPED_DUPLICATE: <path>]` and the JSON keys
  `materials_merged` and `dropped_duplicates`; the error table's `SPEC_PROPOSAL_TARGET_EXISTS` row lists the merge
  conflict and its fix, and its `SPEC_PROPOSAL_INVALID` row a same-path pair that cannot be read for the comparison.
- Step 5 states the fix for a dated path that is not a real directory (rename it aside with its content kept, or
  replace it with a real directory holding that content), added after review finding 1 of `review-01`.

No other Living Spec document changes:

- `UC-incubate-and-hand-off-a-proposal` stays accurate: step 8 says the handoff "moves materials", which still holds
  for a merge, and extension 7f (roll-back) keeps its meaning; the use case lists no `SPEC_PROPOSAL_TARGET_EXISTS`
  extension, before or after this change.
- `docs/capabilities/governance/` names no handoff collision; `docs/architecture/` describes no materials move.
- The code `SPEC_PROPOSAL_TARGET_EXISTS` and its class stay, so no code registry or guide changes.

Entrypoints: `devkit spec entrypoints derive` proposed the four broad boundary directories for
`CAP-DLV-proposal-incubation`; none was written, because its `entrypoints` already name the handoff doorways
(`features/delivery/cli/proposals.py`, `features/delivery/usecases/native_handoff.py`) and the candidates are shared
package directories.

No deferred work and no source feedback.
