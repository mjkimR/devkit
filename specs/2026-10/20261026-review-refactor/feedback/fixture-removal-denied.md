---
id: FB-fixture-removal-denied
title: Disposable fixture removal is denied to the Development worker
scope: unknown
kind: friction
category: other
target: development-worker role contract (scratch fixture cleanup) and the host permission settings
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-fixture-removal-denied] Disposable fixture removal is denied to the Development worker

Nature: a permission boundary between the Host's payload and the host's permission system.

## 1. Friction / Question (friction, question)

- **Context**: the Development payload asked the worker to build a disposable Git fixture under the ignored
  `scratch/` path and remove it before the last commit.
- **Expectation**: creating and deleting files inside the worktree's ignored scratch path is within the write scope.
- **Actual**: the first fixture-creation command (which began with a recursive delete of the target path and a
  directory change) and the final recursive removal of `scratch/rr-fixture` were both denied by the host. Creating
  the fixture with absolute paths and no delete succeeded.
- **Workaround (or Interpretation Chosen)**: the fixture was left at the ignored path (nothing tracked); the record
  and the worker envelope name it for the Host to delete.
- **Suggestion**: either allow recursive removal of `<worktree>/scratch/**` for workers, or have payloads that ask for
  a scratch fixture state that the Host removes it after the run.

## Evidence

```text
rm -rf <worktree>/scratch/rr-fixture && rmdir <worktree>/scratch  -> Permission ... has been denied.
git check-ignore -v scratch/x -> .gitignore:47:/scratch/
```

## Disposition

Resolved by `SPEC-feedback-guidance-and-scope` (decision 1): the development-worker contract (rule 8) keeps authored scratch files in an ignored path inside the worktree and tells the worker never to delete them, because removing the worktree cleans them; the `spec-delegate` payload reference says a payload never asks a worker to delete a scratch file or fixture it created; the planning-worker contract and `CAP-DLV-delivery-workflows` mirror it. Host permissions were not widened. Verified by `test_scratch_cleanup_guidance.py` and a probe showing `git worktree remove` succeeds with ignored files present.
