---
id: ADR-resolved-feedback-retires-by-deletion
title: Resolved feedback retires by deletion
summary: "For resolved feedback, delete eligible records at user-invoked compaction without aliases, accepting that old IDs stop resolving and Git history retains evidence."
status: accepted
created_at: 2026-10-31
supersedes:
  - ADR-closed-feedback-compacts-into-per-area-records-with-aliases
  - ADR-recording-looks-up-existing-feedback-of-every-status-first
---

# [ADR-resolved-feedback-retires-by-deletion] Resolved feedback retires by deletion

## 1. Context & Problem Statement

Resolved feedback records verified fixes. Keeping summaries and aliases indefinitely increases ledger maintenance. Tests and Git history retain regression checks and evidence.

## 2. Decision Drivers

- Reduce retained records without losing active work references.
- Keep rejected and routed outcomes discoverable.

## 3. Considered Options

- Keep compact records and aliases for all outcomes: preserves lookup but retains resolved summaries indefinitely.
- Delete eligible resolved records: reduces ledger size but retired IDs no longer resolve.

## 4. Decision Outcome

Delete eligible resolved feedback during user-invoked compaction, including existing resolved compact records and their aliases. Protect current references, incomplete work and unmerged branches. Continue compacting other terminal outcomes with aliases. A recurrence is a fresh observation; cite an existing resolved record when available. Permit unresolved historical feedback references, while retaining ambiguity errors and strict active reference validation.

This replaces the resolved-feedback compaction and alias retention clauses of `ADR-closed-feedback-compacts-into-per-area-records-with-aliases` and the resolved recurrence action of `ADR-recording-looks-up-existing-feedback-of-every-status-first`.

## 5. Consequences

Historical missing feedback IDs, including typos, are no longer distinguished by reference validation. Git history retains deleted records; active references continue to block deletion.

## 6. Confirmation

Guidance integration tests cover compaction and recording; document reference rule tests cover historical and active references.
