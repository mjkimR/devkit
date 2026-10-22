---
id: FB-answer-correction-unrecorded
title: Worker records give no record for correcting an already-answered question
scope: repo
kind: friction
category: spec-ambiguity
target: spec skill references/worker-records.md
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-answer-correction-unrecorded] Worker records give no record for correcting an already-answered question

## 1. Friction / Question (friction, question)

- **Context**: A Planning turn received the answer to an open question together with the user's correction of an
  earlier, already-recorded answer (`answer-01.yaml` q3), whose meaning the previous turn had applied too broadly.
- **Expectation**: A correction of a recorded answer would be recorded beside the original, so the answer trail shows
  that q3's recorded decision no longer reads as it was applied.
- **Actual**: `references/worker-records.md` allows an `answer` envelope only for an open question or a worker
  assumption of the envelope it names; a correction of an answered question falls under "direction without a
  recorded question", which leaves the misleading `answer-01.yaml` decision sentence unannotated in the envelopes.
- **Workaround (or Interpretation Chosen)**: Recorded only the open question in `answer-02.yaml` and stated the
  correction and its reason in the proposal's Planning decisions and in the worker summary.
- **Suggestion**: Say in worker-records.md how a correction of a recorded answer is recorded (for example a later
  `answer` envelope naming the same worker envelope with the corrected decision, superseding the earlier one).

## Evidence

- `references/worker-records.md` section 2 and "Direction without a recorded question".
- `envelopes/answer-01.yaml` q3 decision ("No ADR file under docs/decisions/ is changed by this work") and the
  proposal's Planning decision "ADRs are not excluded".
