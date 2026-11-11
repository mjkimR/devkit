---
id: FB-review-refactor-applied-patch-file-set-unchecked
title: Review-refactor does not compare an applied result's file set with the checkout it came from
scope: repo
kind: change-request
category: missing-capability
target: packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/references/applying.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-11
---

# [FB-review-refactor-applied-patch-file-set-unchecked] Review-refactor does not compare an applied result's file set with the checkout it came from

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `applying.md` steps 4 and 5 move each subagent result onto the work item branch as a patch
  (`git apply --3way`) and check the result against the assigned paths and the agreed change.
- **Proposed Procedure**: In step 5, also compare `git diff --name-status` of the subagent checkout (tracked and
  untracked files included) with the applied change on the work item branch. Any deleted, added or renamed file that
  is missing on one side blocks the commit.
- **Expected Benefit**: A transfer that silently drops file deletions or new files gets caught before verification,
  not after a later rules or test failure.
- **Cost & Risk**: One extra command per result, with no behavior risk.
- **Attempted**: Tested in this session. The comparison was run by hand after the fact and found the missing files.

## Diagnostic Details

- **Reproduction**: Phase 2 of a code-surface run. Subagent results were exported from isolated checkouts and applied
  one at a time on the work item branch.
- **Expected / Actual**: Expected the applied change to equal the checkout's change. Actually, 7 file deletions were
  absent after the apply, while the content edits applied. The exact export command that lost them was not isolated.
- **Versions**: main at 4539847e.
- **Conditions**: macOS, several concurrent worktrees, and removals of whole modules.
- **Workarounds Attempted**: `git rm` of each missing path, followed by a file-set comparison. This worked.
- **Related Assets**: review-refactor `references/applying.md` steps 4 and 5; run report
  `docs/materials/2026-11/20261111-review-refactor-code-pass/report.md`.

## Evidence

```text
applied patches: content edits present, 7 module deletions absent on the work item branch
fix: git rm <7 paths>; afterwards the name-status sets of the checkout and the branch matched
```

- **Disposition**: review-refactor references/applying.md §3 step 5 now compares `git diff --name-status` of the checkout (untracked included) with the applied change; a missing add, delete or rename blocks the commit.
