---
id: MAT-uiux-run-model-planning
created_at: 2026-11-13
---

# [MAT-uiux-run-model-planning] Run-model contract discovery and options

Evidence source: `plan-uiux-improve-run-model` at `bcea80cf85628445a0e3e99a4bb4fea13faaadbc`, based on
`aa6c51dc3148efba121bc54c8e582a59aacd11d1`. The separate Scout was read-only. Its pre/post full Git tree snapshot
was `80cb944273bf575dc2221505473abdcb661952b5`; HEAD was unchanged. Codex projection is emulated; absolute read/write
scopes, separate host permission requests and caller diff checks substitute for native path enforcement.

## 1. Incoming-reference discovery

`devkit docs refs --direction in -n 0` returned 16 incoming documents for `CAP-DLV-uiux-improvement`, 10 for
`ADR-uiux-improvement-workflow-boundary` and 9 for `ADR-impeccable-session-authority`. Current contracts relevant to
this change are the capability, `UC-improve-an-interface-and-user-flow`, the two ADRs and the three sibling
proposals. Other incoming documents are history or unrelated contract mirrors; they are not live rewrite targets.

- `CAP-DLV-uiux-improvement` rule 3 requires consumer workflow continuation; rules 11–12 qualify verification and
  completion; rules 16–19 cover pre-implementation, acceptance, consumer file ownership and requested actions.
- `ADR-uiux-improvement-workflow-boundary` Decision Outcome clause 2 requires workflow continuation and grants no
  Git authority. Clauses 1, 3 and 4 remain in force.
- `ADR-impeccable-session-authority` Decision Outcome contains consumer-workflow pre-implementation, accepted-change
  continuation and requested-action clauses. Its other permission, brief, question/load and file boundaries remain.
- Source mirrors: entry Boundaries and steps 6–10; orchestration local-role continuation, setup, acceptance and
  requested-action routing; the human README and integration assertions.

## 2. Option comparison and recommendation

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| Retain workflow for every run | Existing rule 3; first pilot in `MAT-uiux-improve-second-pilot` | 18 branch commits including 8 envelope-only commits in the reported run | Retains overhead; that run also caught real defects |
| Announced, task-approved outside route | Owner proposal and second pilot's explicit user instruction | About three product commits, a merge and one question round in the reported run | No independent review or reconcile in that pilot; task and coordinator confounds |
| Neutral route choice | Alternative in proposal Q1 | Still needs explicit route choice and a no-answer boundary | Omits the owner's announced preference |

Recommendation: preserve the owner's announced option while requiring explicit task approval, retain the workflow
choice, keep host/product permissions and applicable checks, and reuse current Git authority or ask once for exact
remaining effects. No answer supplies no bypass authority. Independent reviews remain optional and their absence
is reported. The coordinator reports stale documents with a separate concrete next action.

## 3. Verification limits

This discovery checked internal contracts and instruction/test locations; it ran no behavior or model-obedience
experiment. The pilots support a bookkeeping observation, not comparative quality, lower latency or equivalent
defect detection. No new performance acceptance threshold is inferred from them.
