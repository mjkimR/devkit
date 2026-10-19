---
id: FB-direct-host-pause-status-undefined
title: The worker envelope status for a direct Host pausing for a planned user action is unstated
scope: repo
kind: question
category: spec-ambiguity
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/worker-records.md (section 1)
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-19
---

# [FB-direct-host-pause-status-undefined] The worker envelope status for a direct Host pausing for a planned user action is unstated

## 1. Friction / Question (friction, question)

- **Context**: The round-5 `challenger` of ~~`PROP-worktree-host-compatibility`~~ found that its Development, run in
  `direct`, must pause mid-activity while the user runs a live Codex turn the user agreed to in Planning. The
  proposal had to say how that pause is recorded.
- **Expectation**: `worker-records.md` says which status a `direct` Host's `worker` envelope takes when it stops for
  the user for a planned step that is neither a question nor a problem.
- **Actual**: Section 1 says a `direct` Host writes a `worker` envelope "whenever you stop for the user", that a
  `needs_input` envelope always carries questions or a problem, and that a `completed` one never carries a problem.
  `sdd-spec-feature.md` lets only a problem stop Development. The status for a planned pause follows only by
  elimination (`completed`), and `completed` is described elsewhere as the activity's final change report holding.
- **Workaround (or Interpretation Chosen)**: The proposal states that the Host commits its work and ends its run
  with a `completed` `worker` envelope whose summary names the pending task, after checking that no gate reads a
  `worker` envelope's status (`EnvelopeSet.hold()` counts only problems, questions and malformed records).
- **Suggestion**: State in section 1 that a run ending mid-activity without a question or a problem, including a
  planned pause for the user, records `completed` with the pending step in its summary, and that `completed` for a
  run is not the activity's completion.

## Diagnostic Details

- **Reproduction**: Read `worker-records.md` section 1 and `sdd-spec-feature.md` "Development runs on the agreed
  intent" for a `direct` Development that must wait for a user action named in its accepted plan.
- **Expected / Actual**: Expected a stated status; found one only by eliminating the malformed combinations.
- **Versions**: devkit-spec on `main` at dfea030; branch `plan-worktree-host-compatibility`.
- **Conditions**: `high` Planning, recovery turn after a review-loop cap hand-over.
- **Workarounds Attempted**: none other than the interpretation above.
- **Related Assets**: `envelopes/challenger-05.yaml` finding 2; ~~`PADR-codex-process-worker`~~ §4 The live turn itself;
  `packages/devkit/src/devkit/workflow/unit/envelope/model.py` (`hold`).

## Evidence

```text
worker-records.md §1: "in `direct` mode you write it for your run whenever you stop for the user or end the activity"
worker-records.md §1: "A `completed` envelope never carries a problem, and a `needs_input` one always carries questions or a problem"
sdd-spec-feature.md: "Only a problem that cannot be solved without changing the agreed goal, scope or contract stops the work"
```

Historical source: Git `1b8478093a44cf2d0b74c412bffc93f259459ef0:docs/proposals/PROP-worktree-host-compatibility/feedback/direct-host-pause-status-undefined.md`; relative evidence paths refer to that proposal bundle.
