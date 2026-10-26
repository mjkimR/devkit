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
`review` envelope and the review loop require P1-P3 severity (`MAT-ux-documentation-planning-spike` §5). A stage
switched on by content is excluded by `CAP-DLV-delivery-workflows` under `ADR-delivery-classification`.

## 2. Decision Drivers

- Independence from the author: a fresh, read-only context.
- Fit to evidence: walkthrough plus graded criteria with cited evidence; no severity.
- No change to the workflow engine (`devkit-agt`), to the code-review round state or to `ADR-delivery-classification`.
- Deterministic results are reported, not re-judged.

## 3. Considered Options

- **Walkthrough only**: lowest cost; misses single-screen content problems.
- **Walkthrough plus a 0/1/2 rubric with evidence**: covers both; one run per round.
- **Merged independent runs**: offsets run-to-run inconsistency at several times the cost.
- **Placement as a conditional workflow stage**: rejected: a stage switched on by content is a non-goal of
  `CAP-DLV-delivery-workflows` (`ADR-delivery-classification`), and it would need a new check primitive.
- **Placement as an optional delegation before code**: no engine change; not enforced.

## 4. Decision Outcome

Decided by the user (`review-method` and `review-placement`):

- A `ux-reviewer` subagent (isolated, read-only) bound to a new `spec-ux-review` skill walks each linked use case's
  main scenario and extensions through its screens, answering per step: will the actor try the right thing, notice
  the control, connect it to the goal and see progress.
- It then scores each screen 0, 1 or 2 with evidence for every score below 2 on: **R1 task fit** (the primary task
  and the facts to commit to it are present; secondary items have a place); **R2 one primary region** (no competing
  primary regions, no information dumping); **R3 states** (every state offers a next action or says why none
  exists); **R4 feedback** (every interaction gives feedback; irreversible ones confirm or can be undone); **R5
  terms** (labels use the use case's and glossary's terms); **R6 objects** (representations and calls to action match
  the steering object register for the role; recorded as not applicable while the register is absent or empty).
- Before code the screens are drafts the rules do not read (`PADR-ux-drafts-before-code`), so the reviewer checks
  the link-rule items (link agreement, uncovered steps, targets, exits, reachability, modal close) on the drafts by
  hand, labels them as its own judgment and keeps them out of the rubric; the rules confirm them at
  `living-spec-draft`. Rule results are inputs only for screens already in `docs/ux/` that the drafts link and leave
  unchanged.
- Findings carry no severity and are recorded as `ux-review-NN` envelopes, separate from `review`; at most two rounds
  per unit. In Development the implementer closes the last round by a further `ux-review` envelope marking each
  finding `resolved` or `waived` with a reason; in Planning open findings go to the user at `plan-accept`, listed in
  the acceptance request next to the `challenger` and `scout` envelopes (`sdd-proposal` and the planning reference
  change accordingly).
- It runs as an optional delegation before code: in Planning on the drafted screens, and at spec depth after the
  Screens section of `spec.md` is written and before the plan: inside `specify` before `spec-plan` for
  `sdd-spec-feature`, inside `characterize` before `plan-tasks` for `sdd-spec-bugfix`, recorded at that stage so that
  its fixes precede `plan.md` and `tasks.md`. The reviewed `spec.md` is not yet committed there, so the envelope
  names the last commit and states the uncommitted draft in its assumptions; the effort table recommends it at `medium` and `high` when
  screens change. A `session` task applies the
  `ux-writing` instruction and runs no review.

## 5. Consequences

- Positive: an independent check before build without engine changes.
- Negative: nothing blocks a unit that skips it; `CAP-DLV-delivery-workflows` gains a seventh role, and the effort
  table and its review rule name the UX review.
- Follow-up: enforcing the review needs a decision superseding `ADR-delivery-classification`.
- Follow-up: merged independent runs if rubric scores prove inconsistent across runs.

## 6. Confirmation

Role-contract tests for the new role and skill; review of the skill text. The review's own quality is Review only.
