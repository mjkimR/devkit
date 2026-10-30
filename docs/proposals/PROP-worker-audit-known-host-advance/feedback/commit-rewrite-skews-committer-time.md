---
id: FB-commit-rewrite-skews-committer-time
title: Commit rewriting stamps times hours away from the wall clock, so committer time does not follow ancestry
scope: unknown
kind: friction
category: other
target: the "[cgate] Commit rewritten" commit amendment
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-commit-rewrite-skews-committer-time] Commit rewriting stamps times hours away from the wall clock, so committer time does not follow ancestry

Nature: a Git history property that breaks time-based reasoning over commits.

## 1. Friction / Question (friction, question)

- **Context**: Planning a worker-audit window bounded by the audit base's committer time.
- **Expectation**: A commit's author and committer times are the wall-clock time it was made, so a child is never
  dated before its parent on one machine.
- **Actual**: Every commit in this run was amended right after creation ("[cgate] Commit rewritten: <old> -> <new>").
  The reflog shows the original commit at wall-clock time and the amendment stamped about five hours later. The
  audit base on `main` is dated after all of its children on the Planning branch, and a challenger counted 33
  child-before-parent pairs in the last 300 commits on `main`.
- **Workaround (or Interpretation Chosen)**: The proposal dropped the time-bounded design; nothing in devkit relies on
  commit times today as far as this run found.
- **Suggestion**: Find the component that prints `[cgate]` (no hook is configured in the repository's Git config) and
  keep the original author and committer times when it amends, or document that commit times are unreliable here.

## Evidence

```text
git log fdba6646^..HEAD: fdba6646 dated 18:05:25 +0900; its descendants 650b0fb9.. dated 17:37-17:43 +0900
git reflog: 650f6133 HEAD@{12:37:59 +0900}: commit
            7d6c1185 HEAD@{17:48:51 +0900}: commit (amend)
date during the run: 12:27 KST
git config --show-origin --get-regexp 'hook|cgate': no entry
```
