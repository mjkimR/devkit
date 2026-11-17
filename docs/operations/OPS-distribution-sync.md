---
id: OPS-distribution-sync
title: "Distribution sync diagnosis and routing"
status: active
summary: "Classifies distribution sync symptoms and evidence, routes to existing action owners and identifies normal-state observations."
---

# [OPS-distribution-sync] Distribution sync diagnosis and routing

A pending journal, a later-edited recorded file and an older journal require different evidence before choosing
an existing recovery owner. Absence of a journal alone does not establish that desired-state changes are applied.

## Routing

| Symptom or state | Discriminating evidence | Next useful owner |
| --- | --- | --- |
| Interrupted sync reports `TRANSACTION_PENDING` | A pending synchronization journal is reported | `CAP-DIST-sync-and-transactions` §3 Recovery owns eligibility; the actual pending-transaction advisory owns ACTION/FIX. The [error reference](../development/reference/distribution.md#error-codes) maps the code. |
| `RECOVERY_BLOCKED` after a subsequent edit | A recorded path no longer equals its journal before/after content | The same Recovery item owns the stop condition. The actual recovery advisory identifies the affected path and reporting decision; the reference maps this code to `HALT`. |
| `RECOVERY_BLOCKED` for an older journal | The diagnostic identifies a journal without `directories` | The same Recovery item owns version compatibility. Read the actual advisory's version-specific FIX and reporting guidance. |
| No journal, but desired-state drift remains | Desired inventory differs, such as a preset change without synchronization | `CAP-DIST-sync-and-transactions` Readiness Gate owns the readiness decision. The [status reference](../development/reference/distribution.md#devkit-status) explains installed-state diagnostic limits. |

Start with the code and evidence reported in the actual diagnostic, then consult that row's owner before acting.
For pending and blocked cases, the actual advisory and the [consumption instruction](../../packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/consumption.md#completion)
retain action and completion guidance. For evidence that matches no row, use the actual diagnostic and its
reporting and action owner instead of inferring a recovery branch from this table: the error reference maps
`RECOVERY_BLOCKED` to `HALT` for every unusable journal, and the recovery advisory's stop and report guidance applies.

## Normal-state observation

After the applicable owner's recovery decision, consult `CAP-DIST-sync-and-transactions` Readiness Gate.
Its criterion is `uv run devkit sync --check` exit `0`; exits `1` and `2` mean not ready. A missing journal with
remaining desired-state drift is therefore still not ready. Installed-state diagnostics alone do not establish readiness.

## Authority boundary

The four rows cover documented sync states, not every unusable journal or possible advisory.

## Update triggers

- `CAP-DIST-sync-and-transactions` Recovery or Readiness Gate changes.
- The error reference changes the mapping of `TRANSACTION_PENDING` or `RECOVERY_BLOCKED`, or the journal gains or
  loses a field the rows discriminate on, such as `directories`.
