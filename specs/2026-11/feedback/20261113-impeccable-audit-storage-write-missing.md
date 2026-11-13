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
status: promoted
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

## Disposition

Promoted to `SPEC-uiux-upstream-fallbacks` as completed local mitigation. The local skill checks installed supported help/interface before persistence and returns audit findings in the session report when unsupported, without invented retries, unrequested files or installation changes.

Verification: focused UI/UX bundle integration 16 passed; installed-consumer E2E 1 passed; catalog lint/format and type checks passed; `just test-affected --base 5cab6156a60de1a2a2845e38fc19bda92961c90e --tier all` passed 182 tests. These checks verify shipped instructions and distribution, not upstream runtime or model obedience.

The upstream runtime was not fixed. Native upstream trials were not required or performed. The user selected local compensation and no external submission or retained upstream follow-up; this disposition records no upstream resolution.
