---
id: FB-impeccable-audit-storage-write-missing
title: Impeccable 4.8.2 CLI has no audit-storage write command
scope: upstream
kind: friction
category: tool-error
target: impeccable audit-storage write
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-13
---

# [FB-impeccable-audit-storage-write-missing] Impeccable 4.8.2 CLI has no audit-storage write command

## 1. Friction / Question (friction, question)

- **Context**: An Impeccable session delegated by `app-uiux-improve` ran the `audit` command in a consumer
  repository.
- **Expectation**: The audit flow can persist its result through `audit-storage write`.
- **Actual**: The Impeccable 4.8.2 CLI does not provide `audit-storage write`.
- **Workaround (or Interpretation Chosen)**: unknown; the audit result was returned in the session report.
- **Suggestion**: Report upstream to Impeccable. devkit needs no change unless the brief template starts naming audit
  storage.

## Diagnostic Details

- **Reproduction**: unknown; observed in a consumer run.
- **Expected / Actual**: Expected the subcommand; actual not available in 4.8.2.
- **Versions**: Impeccable CLI 4.8.2.
- **Conditions**: Claude Code subagent session in a consumer repository.
- **Workarounds Attempted**: unknown.
- **Related Assets**: `MAT-uiux-improve-second-pilot`.

## Evidence

```text
Coordinator report from the consumer run: `audit-storage write` is missing in the 4.8.2 CLI.
```
