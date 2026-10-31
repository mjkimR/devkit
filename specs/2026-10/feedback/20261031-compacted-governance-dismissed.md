---
id: FB-compacted-governance-dismissed
title: Governance feedback, dismissed
summary: Repository governance rules and architectural constraints.
target: docs/capabilities/governance/
status: dismissed
created_at: 2026-10-31
aliases:
  - FB-adr-before-build-misses-the-reconcile-commit
---

# [FB-compacted-governance-dismissed] Governance feedback, dismissed

## FB-adr-before-build-misses-the-reconcile-commit

- **Symptom**: An ADR written before the build cannot be a reconcile target once the commit gate checks each commit
- **Response**: fe9f270
- **Reason**: already resolved; `RULE-reconcile-contract` reads the staged diff together with the branch's earlier commits since its merge base, and its guide and `spec/references/completion.md` state it.
