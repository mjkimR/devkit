---
id: FB-post-resolution-round-outcome
title: The review loop does not say how a post-resolution round ends when its batch fails again
scope: repo
kind: question
category: unclear-instruction
target: spec skill references/review-loop.md
origin: agent
severity: friction
recurring: false
status: resolved
resolved_at: 2026-10-19
disposition: Clarified review-loop.md §4 that the resolution envelope is recorded when the requested round finishes, and that any failure of the post-resolution round's batch to meet §2 terminates the run and hands back to the user as a problem.
created_at: 2026-10-19
---

# [FB-post-resolution-round-outcome] The review loop does not say how a post-resolution round ends when its batch fails again

## 1. Friction / Question (friction, question)

- **Context**: the `high` Planning of `SPEC-draft-direct-acceptance` handed a cap problem to the user (`worker-02`).
  The user asked for one more fresh `challenger` round (round 6). That round returned P2 and P3 findings marked
  `recurs:`, plus a `Decision needed:` finding.
- **Expectation**: `review-loop.md` §4 says how a round opened by a `resolution` ends when its batch again fails §2.
  It should also say when the `resolution` envelope is written: before the round, or only after the round closes.
- **Actual**: §4 says the fix "gets one further fresh round outside the cap, named by the `resolution` envelope", and
  that "its outcome follows the rules above; a recurrence of the same P1 hands over again". It says nothing about a
  P2 or P3 recurrence, or about a non-minor fix in that round. "The rules above" would need yet another round, which
  the cap no longer allows. The Host's payload asked for the resolution "once the round closes", which never happens
  when the round fails, while §4 reads as if the resolution opens the round.
- **Workaround (or Interpretation Chosen)**: I fixed the minor findings and self-verified them. The batch went to the
  user as a new problem in `worker-03`, because recurring findings cannot be self-verified. I recorded `resolution-01`
  for `worker-02` anyway, since the recovery it asked for (round 6) was carried out.
- **Suggestion**: state in §4 that a post-resolution round whose batch fails §2 for any reason (a recurrence of any
  severity, or a decision change) goes back to the user as a new problem. Also state that the `resolution` is
  recorded when the requested round has run, whatever its outcome.

## Diagnostic Details

- **Reproduction**: at `high`, hand a cap problem to the user, get a "one more round" answer, and have that round
  return a P2 finding marked `recurs:`.
- **Expected / Actual**: expected one end condition and one point for the resolution record. Actual: the text covers
  only a recurring P1, and the payload and the loop name different moments for the resolution.
- **Versions**: branch `plan-draft-direct-acceptance` at `e28d7cc`; loop text from the installed `spec` skill.
- **Conditions**: a user-requested round after a cap hand-over.
- **Workarounds Attempted**: the interpretation above, stated in the `worker` envelope.
- **Related Assets**: `references/review-loop.md` §4, `spec-delegate` recovery payload, planning-worker role contract.
