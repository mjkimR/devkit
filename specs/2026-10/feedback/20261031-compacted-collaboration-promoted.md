---
id: FB-compacted-collaboration-promoted
title: Collaboration feedback, promoted
summary: Work scope registration and cross-agent collaboration.
target: docs/capabilities/collaboration/
status: promoted
created_at: 2026-10-31
aliases:
  - FB-receipt-overlap-between-tasks
  - FB-skeleton-placeholder-registers-false-overlap
---

# [FB-compacted-collaboration-promoted] Collaboration feedback, promoted

## FB-receipt-overlap-between-tasks

- **Symptom**: Parallel tasks overlap on the installation receipt
- **Response**: src/devkit_spec/bundle/skills/spec/references/worktree.md
- **Reason**: S-Lane; a receipt conflict when integrating the base is resolved by `devkit sync`; the registry still reports the overlap, which is real

## FB-skeleton-placeholder-registers-false-overlap

- **Symptom**: Scope registration counts the skeleton placeholder <target area> as a declared code scope
- **Response**: `src/devkit_spec/scope/inputs.py`
- **Reason**: `from_spec` treats a skeleton `tasks.md` (`<!-- devkit:skeleton -->`) as `missing-tasks` and angle-bracket placeholders (`<...>`) as `not-a-path` unresolved entries instead of declared code paths.
