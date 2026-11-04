---
id: FB-consolidated-generated-promoted
title: Generated feedback, promoted
summary: Tracked generated artifacts and registry checks.
target: docs/capabilities/generated/
status: promoted
created_at: 2026-10-31
aliases:
  - FB-compacted-generated-promoted
  - FB-generated-check-uncommitted-registry
---

# [FB-consolidated-generated-promoted] Generated feedback, promoted

## FB-generated-check-uncommitted-registry

- **Symptom**: devkit generated check refuses an artifact that list shows, before the registry is committed
- **Response**: packages/devkit/src/devkit/generated/engine.py
- **Reason**: `devkit generated check` names an ID registered only in the working tree as not committed at the checked revision, with a `[FIX]` to commit `.devkit/generated.toml` or pass `--rev`.
