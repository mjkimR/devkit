---
id: PADR-keep-performance-passes-in-a-separate-maintenance-playbook
title: Keep performance passes in a separate maintenance playbook
summary: For repeatable performance passes, we ship a separate router-structured performance-pass playbook in the maintenance bundle instead of a review-refactor surface, to keep each playbook's goal, criteria and evidence focused, accepting a second playbook that must stay aligned with review-refactor.
proposal: PROP-performance-pass
status: draft
created_at: 2026-10-27
---

# [PADR-keep-performance-passes-in-a-separate-maintenance-playbook] Keep performance passes in a separate maintenance playbook

- **Status**: Draft
- **Date**: 2026-10-27

---

## 1. Context & Problem Statement

The 2026-10-27 performance pass borrowed the `review-refactor` procedure, but its goal (latency of user-selected
operations) and its evidence (a measured baseline, attribution without profiler distortion, measured savings) differ
from a maintenance-cost review. Folding it into `review-refactor` as a fourth surface would put measurement and
profiling text into a playbook that is already near its size budget and whose criteria (a named maintenance cost,
reduction grounds) do not apply to latency.

## 2. Decision Drivers

- Each playbook keeps one goal, one set of review criteria and one kind of evidence.
- The playbook fits the skill size budget with a router `SKILL.md` and references read per phase.
- Application, evidence and review rules shared with `review-refactor` exist once.
- A consumer selects the playbook from the `maintenance` bundle like the other maintenance playbooks.

## 3. Considered Options

- **A separate `performance-pass` playbook in `maintenance`, router-structured from the start** (selected by `user`):
  focused criteria and evidence; a second asset whose shared steps are reused by reference.
- **A `performance` surface of `review-refactor`**: one asset; mixes latency criteria into maintenance-cost criteria
  and grows a playbook near its budget.
- **A playbook in another bundle**: no shared preset or retrieval path with `review-refactor`.

## 4. Decision Outcome

- `performance-pass` is a directory-form playbook asset of the `maintenance` catalog bundle beside `review-refactor`.
- It is authored by the `skill-authoring` playbook as a router: `SKILL.md` holds the entry condition, intake, mode
  selection, the decision round summary, the report and completion; each phase that only some runs need has its own
  reference.
- It reuses `review-refactor`'s application procedure and differential evidence by reference
  (`PADR-reuse-review-refactor-application-through-exact-playbook-retrieval`).

## 5. Consequences

- Positive: each playbook stays focused and within budget; latency evidence has its own criteria.
- Negative: two playbooks to keep aligned where they share steps.
- Follow-up: if a later run shows the two share most of their procedure, merge them (the proposal's retirement
  criterion).

## 6. Confirmation

`devkit-catalog` bundle tests (asset kind and source, presets) and
`uv run devkit rules check --phase hygiene` on the playbook directory (`RULE-skill-document-size`,
`RULE-agent-asset-wording`).
