---
id: FB-planning-direction-change-without-question
title: No record form for a direction change without a pending question
scope: repo
kind: friction
category: spec-ambiguity
target: spec skill references/planning.md (step 2) and references/worker-records.md (section 2)
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-20
---

# [FB-planning-direction-change-without-question] No record form for a direction change without a pending question

## 1. Friction / Question (friction, question)

- **Context**: A Planning turn after a completed run (no pending question) received a user direction change made at
  the `plan-accept` review, and later a second change superseding the first.
- **Expectation**: Planning step 2 records answers as an `answer` envelope before folding them.
- **Actual**: The `answer` envelope requires `--answers-to <worker-NN.yaml>` naming a run that asked; none asked, so
  the procedure gives no record form for an unsolicited decision.
- **Workaround (or Interpretation Chosen)**: Recorded the decision only in `proposal.md` and the PADR (marked as a user
  decision at the `plan-accept` review) and named it in the run's `worker` envelope summary.
- **Suggestion**: State in planning step 2 how a decision without a pending question is recorded (document text plus
  the `worker` summary, or an `answer` envelope without `answers_to`).

## Evidence

```text
planning.md step 2: "an `answer` envelope naming the `worker` envelope that asked (... --answers-to <worker-NN.yaml> ...)"
envelopes/worker-02.yaml: status: completed, no questions
```

## Resolution

Directly resolved by `SPEC-worker-guidance-and-fixtures`: worker-records section 2 documents unsolicited decisions in proposal/PADR and the subsequent worker summary, preserving pending answers and settles-only records.

Verification: Independent medium code review found the settles-only exception; the implementer corrected and reverified it against the existing envelope contract.
