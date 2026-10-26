---
id: PADR-ux-review-before-code
title: Isolated UX walkthrough review before code
summary: For reviewing screens independently of their author, we add a read-only ux-reviewer that walks each linked use case through the screens and scores a 0/1/2 rubric with evidence under its own envelope kind before code, to counter lenient self-review, accepting an optional delegation without severity.
proposal: PROP-ux-documentation
status: draft
created_at: 2026-10-26
---

# [PADR-ux-review-before-code] Isolated UX walkthrough review before code

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

Agents grade their own interface work leniently and layouts converge to generic averages; a separate evaluator with
graded criteria and a round cap is the documented mitigation (`MAT-ux-documentation-practice` §3-§4). An LLM reviewer
is credible for a step-by-step walkthrough over declared links and for single-screen content, not for severity or
real-user validation. devkit has an isolated read-only reviewer pattern (`code-reviewer` with `spec-review`), but its
`review` envelope and the review loop require P1-P3 severity, and no workflow check can run a stage only for units
that touch UX documents (`MAT-ux-documentation-planning-spike` §5).

## 2. Decision Drivers

- Independence from the author: a fresh, read-only context.
- Fit to evidence: walkthrough plus graded criteria with cited evidence; no severity.
- No change to the workflow engine (`devkit-agt`) or to the code-review round state.
- Deterministic results are reported, not re-judged.

## 3. Considered Options

- **Walkthrough only**: lowest cost; misses single-screen content problems.
- **Walkthrough plus a 0/1/2 rubric with evidence**: covers both; one run per round.
- **Merged independent runs**: offsets run-to-run inconsistency at several times the cost.
- **Placement as a conditional workflow stage**: enforced, but needs a new check primitive in `devkit-agt`.
- **Placement as an optional delegation before code**: no engine change; not enforced.

## 4. Decision Outcome

Pending the user's answers to `review-method` and `review-placement` (Planning recommendation):

- A `ux-reviewer` subagent (isolated, read-only) bound to a new `spec-ux-review` skill walks each linked use case's
  main scenario and extensions through its screens, answering the four walkthrough questions per step, then scores
  each screen on a 0/1/2 rubric with evidence for every score below 2.
- Results of the UX coverage rule are inputs reported as facts; the rubric excludes what that rule decides.
- Findings carry no severity and are recorded as `ux-review-NN` envelopes, separate from `review`; at most two
  rounds per unit, stated in the skill.
- It runs as an optional delegation before code: in Planning on the proposal's target UX documents, and after
  `specify` on the unit's UX documents; the effort table recommends it at `medium` and `high` when UX documents
  change.

## 5. Consequences

- Positive: an independent check before build without engine changes.
- Negative: nothing blocks a unit that skips it; `CAP-DLV-delivery-workflows` gains a seventh role.
- Follow-up: a conditional stage when projects report skipped UX reviews; it needs a check primitive that inspects
  the unit's links.
- Follow-up: merged independent runs if rubric scores prove inconsistent across runs.

## 6. Confirmation

Role-contract tests for the new role and skill; review of the skill text. The review's own quality is Review only.
