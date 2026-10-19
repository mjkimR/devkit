---
id: FB-review-round-count-before-markers
title: The bounded review loop does not say how to count rounds recorded before the round marker existed
scope: repo
kind: question
category: unclear-instruction
target: spec skill references/review-loop.md
skill: spec
agent: claude-code
origin: agent
severity: friction
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-review-round-count-before-markers] The bounded review loop does not say how to count rounds recorded before the round marker existed

## 1. Friction / Question (friction, question)

- **Context**: the `high` Planning of `PROP-draft-direct-acceptance` resumed after the user's answers, with four
  `challenger` envelopes recorded before the high-effort review-loop spec landed on main (not yet on this branch);
  the caller asked the worker to follow the bounded loop of main's `references/review-loop.md`.
- **Expectation**: the loop says how earlier `challenger` envelopes without a `round <N>;` marker count, and whether a
  question round answered by the user (not a cap or recurrence problem) opens a fresh round outside the cap.
- **Actual**: counts "are read from these markers, never from new fields", so unmarked envelopes count as nothing by
  the letter, while by substance the fourth pass was already the cap round; the only fresh round outside the cap
  follows a `resolution` of a cap or recurrence problem, and the user's answers to `needs_input` questions are neither.
- **Workaround (or Interpretation Chosen)**: counted the unmarked passes as rounds 1 to 4, treated the user's answers
  as opening one fresh round outside the cap (`challenger-05`, `round 5;`), and handed its non-minor fix batch to the
  user as a problem.
- **Suggestion**: state in `review-loop.md` §1 that envelopes of the same kind without a marker count in file order,
  and say in §4 whether answered `needs_input` questions that change decisions open a fresh round outside the cap.

## Diagnostic Details

- **Reproduction**: resume a `high` Planning whose `challenger-01` to `challenger-04` predate the marker, then apply
  main's loop.
- **Expected / Actual**: expected one counting rule; actual two readings, one of which allows unbounded rounds.
- **Versions**: branch `plan-draft-direct-acceptance` at `96ddbc8`; loop text from main at `c93f347`.
- **Conditions**: a unit whose Planning spans the loop's introduction.
- **Workarounds Attempted**: the interpretation above, stated in the `worker` envelope.
- **Related Assets**: `references/review-loop.md` §1 and §4 and the bounded high-effort review-loop ADR on main.
