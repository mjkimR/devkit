---
id: FB-reconcile-close-guidance-names-reverify
title: Effort and delegate guidance still offer reverify for reconcile findings
scope: repo
kind: friction
category: docs-mismatch
target: spec skill references/effort.md
skill: spec-sync
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-reconcile-close-guidance-names-reverify] Effort and delegate guidance still offer reverify for reconcile findings

## 1. Friction / Question (friction, question)

- **Context**: Fixing `FB-reverify-fix-omits-reconcile-check` in `SPEC-feedback-guidance-fixes`, whose write scope
  covered the `[FIX]` text but not the skill sentences.
- **Expectation**: Every guide that tells an agent how to close a reconcile finding names the route the CLI accepts.
- **Actual**: `references/effort.md` (medium repeat calls) says "Close findings with evidence in `reverify` or a new
  `reconcile-check`", and `spec-delegate` Step 6 names only `envelope reverify` for closing findings; the CLI refuses
  a reverify `--from` a `reconcile-check` envelope (`ENVELOPE_FROM_INVALID`), now with a `[FIX]` naming the
  reconcile-check route.
- **Workaround (or Interpretation Chosen)**: Left both sentences unchanged; the refusal's `[FIX]` points to the route.
- **Suggestion**: In `effort.md`, say a code-review finding closes with `reverify` and a reconcile finding with a new
  `reconcile-check`; add the same sentence beside the reverify sentence in `spec-delegate` Step 6.

## Evidence

```text
references/effort.md: "Close findings with evidence in `reverify` or a new `reconcile-check`, naming who verified ..."
spec-delegate Step 6: "A review records findings as found (all open); `envelope reverify` (...) closes it ..."
CLI: (ENVELOPE_FROM_INVALID) --from must name a review, challenger or reverify envelope, not reconcile-check
```
