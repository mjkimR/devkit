---
id: FB-entrypoints-derive-pairs-unrelated-boundaries
title: entrypoints derive pairs every task boundary with every reconcile target
scope: repo
kind: friction
category: other
target: devkit spec entrypoints derive
origin: agent
severity: noise
recurring: false
status: dismissed
created_at: 2026-11-11
---

# [FB-entrypoints-derive-pairs-unrelated-boundaries] entrypoints derive pairs every task boundary with every reconcile target

Category other: candidate relevance in entrypoint derivation.

## 1. Friction / Question (friction, question)

- **Context**: spec-sync of a unit whose four tasks touched three packages (worktree, core Git, search), each with
  its own capability target in `reconcile.md`.
- **Expectation**: candidates relate a document to the code its tasks changed for it.
- **Actual**: `devkit spec entrypoints derive` offered 17 new pairs, for example `devkit_core/core/git.py` and the
  search package as entrypoints of `CAP-WT-task-worktrees`: every boundary path is joined with every target,
  including test files and paths of unrelated tasks.
- **Workaround (or Interpretation Chosen)**: rejected every candidate by review, as the skill allows.
- **Suggestion**: join a target only with the boundaries of tasks whose `_Requirements` serve ACs that relate to it
  (or with paths under the target's documented ownership), and skip test paths, so a multi-area unit yields few
  reviewable candidates. Distinct from FB-derive-prints-every-pair, which grouped the output lines.

- **Disposition**: Normal behavior: `CAP-TRACE-code-entrypoints` pairs every document with every candidate and leaves relevance to the spec-entrypoints review (Non-Goals, §3.5, §3.7). Revisit through a proposal if candidate lists keep growing.
