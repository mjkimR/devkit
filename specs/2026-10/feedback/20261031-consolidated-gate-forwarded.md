---
id: FB-consolidated-gate-forwarded
title: Gate feedback, forwarded
summary: Git commit gates, hooks, and lifecycle checks.
target: docs/capabilities/gate/
status: forwarded
created_at: 2026-10-31
aliases:
  - FB-compacted-gate-forwarded
  - FB-post-commit-rewrite-stales-the-printed-hash
---

# [FB-consolidated-gate-forwarded] Gate feedback, forwarded

## FB-post-commit-rewrite-stales-the-printed-hash

- **Symptom**: A post-commit hook rewrites the commit, so the hash git commit prints is stale
- **Response**: cgate (owner's change)
- **Reason**: the post-commit hook now prints `[cgate] Commit rewritten: <old> -> <new> (use <new>)`.
