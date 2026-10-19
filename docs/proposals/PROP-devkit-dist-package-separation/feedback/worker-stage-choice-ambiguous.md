---
id: FB-worker-stage-choice-ambiguous
title: Planning worker envelope stage is ambiguous when spike work runs under collect-feedback
scope: repo
kind: question
category: spec-ambiguity
target: planning-worker role contract (step 6, --stage) and spec skill references/worker-records.md
skill: spec
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-worker-stage-choice-ambiguous] Planning worker envelope stage is ambiguous when spike work runs under collect-feedback

## 1. Friction / Question

- **Context**: A Planning run started with `devkit workflow next` naming `collect-feedback` (spike is optional and
  never becomes current). The run did spike work (scout, two challenger rounds, PADRs), then the feedback sweep,
  then its single `worker` envelope with questions.
- **Expectation**: The contract says `--stage` is "the stage `next` named". After the run's own feedback envelope,
  `next` names `direction-handoff`, so "the stage next named" differs between the start and the end of the run.
- **Actual**: Both choices hold `plan-accept` (the questions hold the gate of their stage and every later one), so
  the outcome is the same; only the record differs.
- **Workaround (or Interpretation Chosen)**: Used the stage `next` named at the start of the run
  (`collect-feedback`), which is also the stage the caller's payload named.
- **Suggestion**: State in the planning-worker contract and `worker-records.md` whether `--stage` is the stage at
  the start of the run or at the time the envelope is written.

## Diagnostic Details

- **Reproduction**: Start Planning on a proposal whose `plan-intent` passed; `next` names `collect-feedback`; write
  the feedback envelope; `next` then names `direction-handoff`.
- **Expected / Actual**: One unambiguous stage; two defensible readings.
- **Versions**: devkit-agt 0.1.1, devkit-spec 0.1.0 (workspace source).
- **Conditions**: local-orchestrated planning worker in its own worktree.
- **Workarounds Attempted**: Interpretation above.
- **Related Assets**: `.devkit/managed/spec/subagents/planning-worker.md` step 6, `sdd-proposal` workflow.

## Evidence

```text
devkit workflow next (start of run): [STAGE: collect-feedback ...] [UNMET: envelope-check-pass(feedback swept)]
planning-worker.md step 6: "--stage (the stage `next` named) and --effort always"
```
