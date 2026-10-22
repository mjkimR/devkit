---
id: FB-review-loop-adr-disagrees-with-bundle
title: The high-effort review loop ADR disagrees with the shipped review-loop reference
scope: repo
kind: friction
category: docs-mismatch
target: ADR-bounded-high-effort-review-loop; packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/review-loop.md
skill: adr-compaction
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-review-loop-adr-disagrees-with-bundle] The high-effort review loop ADR disagrees with the shipped review-loop reference

## 1. Friction / Question (friction, question)

- **Context**: An ADR compaction run grouped the review ADRs.
- **Expectation**: The accepted ADR, the bundle reference and the capability state one escalation rule.
- **Actual**: `ADR-bounded-high-effort-review-loop` sends a contested P1 to the user as a worker question and closes a user-rejected P1 by a waiver citing the answer. The shipped `review-loop.md` §4 makes it a Host-owned `problem`, gives a Host-directed recovery the extra round and "adds no user approval gate" (commit 59402001, no ADR). `CAP-DLV-delivery-workflows` rule 7 still matches the ADR.
- **Workaround (or Interpretation Chosen)**: The ADR and the one it supersedes (`ADR-medium-review-delegation`) were left out of compaction.
- **Suggestion**: Decide which rule holds; record it in an ADR that supersedes `ADR-bounded-high-effort-review-loop`, or revert the bundle text, and align `CAP-DLV-delivery-workflows`.

## Diagnostic Details

- **Reproduction**: Compare the ADR's escalation clauses with `review-loop.md` §4.
- **Expected / Actual**: One rule; two different rules.
- **Versions**: main at dd008f2b.
- **Conditions**: not applicable.
- **Workarounds Attempted**: Left out of compaction.
- **Related Assets**: `ADR-bounded-high-effort-review-loop`, `CAP-DLV-delivery-workflows`, `review-loop.md`.

## Evidence

```text
review-loop.md §4: contested P1 -> problem for the Host; "adds no user approval gate"
ADR-bounded-high-effort-review-loop: contested P1 -> worker question to the user
```
