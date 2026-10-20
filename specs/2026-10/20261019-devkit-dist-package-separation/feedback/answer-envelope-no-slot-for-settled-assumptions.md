---
id: FB-answer-envelope-no-slot-for-settled-assumptions
title: Answer envelope has no slot for user decisions that settle worker assumptions
scope: repo
kind: question
category: spec-ambiguity
target: spec skill references/worker-records.md (answer records) and devkit workflow envelope answer
skill: spec
agent: claude-code
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-19
---

# [FB-answer-envelope-no-slot-for-settled-assumptions] Answer envelope has no slot for user decisions that settle worker assumptions

## 1. Friction / Question (friction, question)

- **Context**: A Planning turn received one rewritten answer to the single open question of the previous `worker`
  envelope, plus two more user decisions from the same round. Those two settled assumptions the previous worker had
  recorded (in its `assumptions` list, each "open at plan-accept"). They were not answers to a question, and the
  caller said to record them as decisions.
- **Expectation**: The answer record has a place for user decisions of the round that close a worker assumption,
  so the PADRs can cite them with user authority.
- **Actual**: `devkit workflow envelope answer` takes only a list of `{question, choice, decision, constraints}`
  items, each tied to a question of the named worker envelope. The guide limits `constraints` to "what the answer
  adds". No field records a decision on a worker assumption.
- **Workaround (or Interpretation Chosen)**: Recorded both decisions as `constraints` on the one answer, each
  starting "Settled by the user in the same round:", and cited that envelope from the PADR and the proposal. The
  link is visible, but it stretches the meaning of `constraints`.
- **Suggestion**: Either allow an optional `settles` list in the answer envelope (each item names a worker
  assumption and gives a decision sentence), or state in `worker-records.md` that decisions settling assumptions go
  into `constraints` of the nearest answer, or into the PADR alone with the answer envelope cited as provenance.

## Evidence

```text
worker-records.md (installed copy), answer recording:
  --answers-to worker-NN.yaml --answers-file -    # - { question: q1, choice: a, decision: "...", constraints: [...] }
  "One decision sentence per question; ... `constraints` only for what the answer adds."

Previous worker envelope (worker-02.yaml) assumptions:
  - Contract 6 split ... the user can overrule at plan-accept
  - A generic cross-bundle SELECTION_INVALID hint is a non-goal ... the user can add it at plan-accept

Recorded answer-02.yaml: one answer (harness-bundle-name, keep-harness) carrying two constraints
"Settled by the user in the same round: ..." for those two assumptions.
```

- **Disposition**: PROP-envelope-record-gaps: a slot for assumptions the user settled (Q2)
- **Disposition (resolved)**: `SPEC-envelope-record-gaps` adds `settles: [{assumption, decision}]` to `answer`
  envelopes, written with `devkit workflow envelope answer --settle N=DECISION`
  (`ADR-answer-envelopes-settle-worker-assumptions`). Verified by `packages/devkit/tests/workflow/test_envelope_record_gaps.py` (AC-06, AC-07).
