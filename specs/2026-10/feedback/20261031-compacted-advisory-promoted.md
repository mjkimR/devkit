---
id: FB-compacted-advisory-promoted
title: Advisory feedback, promoted
summary: Agent advisory protocol and unique code reporting.
target: docs/capabilities/advisory/
status: promoted
created_at: 2026-10-31
aliases:
  - FB-advisory-init-docstring-bundle
---

# [FB-compacted-advisory-promoted] Advisory feedback, promoted

## FB-advisory-init-docstring-bundle

- **Symptom**: devkit.advisory docstring says devkit reads a bundled guide from it
- **Response**: packages/devkit-advisory/src/devkit/advisory/__init__.py
- **Reason**: the docstring drops the bundled-guide clause and names `devkit.advisory_guide` as where the guides ship.
