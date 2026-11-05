---
id: PROP-gitignore-drift-detection-target
title: Target Living Spec Structure for PROP-gitignore-drift-detection
status: draft
proposal: SPEC-gitignore-drift-detection
created_at: 2026-11-04
targets: []
---

# [Blueprint] PROP-gitignore-drift-detection

## 1. Retained Contract Changes

- CAP-DIST-sync-and-transactions: define projection Git diagnostics, stable notice codes, bounded remediation
  output and behavior across sync modes.
- CAP-DIST-workspace-ownership: describe diagnostics while retaining project ownership of root ignore files
  and the Git index. Existing managed/transient ignore behavior remains unchanged.
- Proposed UC-sync-projection-git-diagnostics: distinguish ignored projections, missing ignore coverage and
  tracked projections while preserving neighboring project-owned files.

## 2. Implementation Boundary

Distribution owns the diagnostic using actual deployment records. No governance rule, automatic root ignore
editor, index fixer or new configuration table is planned. No architecture change is currently required.

## 3. Verification

Cover tracked and untracked projections, effective and negated ignore rules, mixed project/native ownership,
and non-Git workspaces. Verify that the diagnostic never writes the root ignore file or Git index.
