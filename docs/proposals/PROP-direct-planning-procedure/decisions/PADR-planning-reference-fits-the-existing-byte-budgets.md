---
id: PADR-planning-reference-fits-the-existing-byte-budgets
title: Planning reference fits the existing byte budgets
summary: The new Planning reference and the one-line link from the spec SKILL.md fit the existing byte budgets, so no other reference is trimmed; role contracts have no byte budget and shrink.
proposal: PROP-direct-planning-procedure
status: draft
created_at: 2026-10-19
---

# [PADR-planning-reference-fits-the-existing-byte-budgets] Planning reference fits the existing byte budgets

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

Q2 asks whether moving the steps fits the bundle's byte budgets or forces another reference to be trimmed.
`packages/devkit-spec/tests/test_bundle_budgets.py` caps every skill and playbook document at 12288 bytes, holds
`spec/SKILL.md` to 11776 bytes (headroom from `SPEC-subagent-procedure-in-contract`), and requires every file under
a skill's `references/` to be linked from that skill.

## 2. Decision Drivers

- Measured sizes at base `97cdcd8`: `spec/SKILL.md` 6531 bytes; the largest `spec` reference 6833 bytes
  (`completion.md`); the `planning-worker` contract 7953 bytes, of which steps 2 to 6 are 4277 bytes.
- No test or rule caps a role contract's size.

## 3. Considered Options

1. **New `references/planning.md`, linked once from the routing table's proposal row** (chosen).
2. Append the steps to `worker-records.md` (6791 bytes): about 11 KB, near the budget edge, and mixes record mechanics
   with the activity's order.

## 4. Decision Outcome

Option 1. The moved text, with a short opening for both executors, is about 4.5 KB, well under 12288; the link adds about 100 bytes to `spec/SKILL.md`
(about 6.6 KB of 11776). The contract shrinks to about 4 KB. No reference is trimmed.

## 5. Consequences

- The link-coverage test passes once the routing row links `references/planning.md`.
- If Development's text grows past about 8 KB, split it rather than trimming another reference.
