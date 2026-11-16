---
reconcile_id: REC-open-feedback-fixes
status: resolved
targets:
  - file: docs/architecture/ARCH-06-runtime-view.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
    resolution: modified
---

# Reconcile: `SPEC-open-feedback-fixes`

- `ARCH-06-runtime-view` §1 now writes the journal of pending changes and previous state before the loop that writes
  managed files and projections, as `CAP-DIST-sync-and-transactions` §3 item 3 and `apply_changes` order it. The
  capability keeps the full algorithm (deletions first, directory handling, recovery); the view stays a summary.
- `CAP-DLV-proposal-lifecycle` §3 step 1 now states that the carried planned boundaries omit the proposal's own path,
  matched exactly, which `_without_own_path` in the handoff use case implements and `test_carries_the_proposal_body`
  checks. The bugfix notes of step 2 reuse the same boundaries, so the clause covers them.
- `CAP-DOCS-document-lookup` §3.1 item 1 already requires workspace-relative paths; the resolve help now restates it
  and needs no contract change.
- The scout's Claude Code tool list is a bundle role contract, not Living Spec; `ARCH-04-1-ecosystem-boundaries`
  describes scout as read-only inspection, which `WebSearch` keeps. `CAP-DIST-agent-projections` lists only
  `role-worker`'s tools, so it is unaffected.
- Design, domain and operations: unaffected. No design document owns the handoff boundary rendering or the sync
  journal, no domain term changed, and no operational procedure depends on the help wording or the scout tools.
- Entrypoints: unchanged. `devkit spec entrypoints derive` offers `CAP-DLV-proposal-lifecycle` only paths from the
  other tasks (the docs CLI, the scout contract and tests), none of which it owns; its handoff use case is already
  declared.
- Source feedback: `FB-runtime-journal-ordering`, `FB-scout-lacks-web-search`,
  `FB-handoff-skeleton-keeps-proposal-boundary` and `FB-resolve-package-path-anchor` are `resolved` with a
  Disposition naming this spec. No deferred work.
