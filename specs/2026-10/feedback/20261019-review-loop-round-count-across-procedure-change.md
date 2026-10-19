---
id: FB-review-loop-round-count-across-procedure-change
title: The review loop's round count is undefined for a Planning whose earlier rounds predate it
scope: repo
kind: question
category: spec-ambiguity
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/review-loop.md (section 1 Round count, section 4 cap)
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-review-loop-round-count-across-procedure-change] The review loop's round count is undefined for a Planning whose earlier rounds predate it

## 1. Friction / Question (friction, question)

- **Context**: A `high` Planning turn of ~~`PROP-worktree-host-compatibility`~~ folded the user's answers and had to
  re-run the bounded review loop on what changed. Its three earlier `challenger` rounds were recorded before the
  high-effort review loop spec integrated on `main`: their summaries carry no `round <N>;` marker and their findings
  carry `high`/`medium` severities instead of `P1`/`P2`/`P3`. The `plan-` branch still lacks `references/review-loop.md`;
  the caller pointed the worker at the copy on `main`.
- **Expectation**: The procedure says how to count rounds that predate the markers, and whether a user's answer
  folded into the proposal opens a new batch inside the same loop or a fresh loop.
- **Actual**: Counts are "read from these markers, never from new fields", so the earlier rounds count as zero by
  the letter, while their envelopes show three rounds. A fold of user answers is not named as a batch, a `return` or
  a user-requested fix (section 4's one further round outside the cap).
- **Workaround (or Interpretation Chosen)**: Counted the three unmarked rounds as rounds 1 to 3 and recorded this
  turn's review as `round 4;`, the cap round, reviewing every change since round 3 (the round-3 fold and the answer
  fold), so a batch needing another round is handed over rather than reviewed again. This is the strictest reading;
  nothing states it.
- **Suggestion**: State in section 1 that unmarked rounds of the same segment count in order of their envelope
  sequence, and say whether folding user answers after a closed loop starts a new loop (a fresh round 1) or continues
  the count.

## Diagnostic Details

- **Reproduction**: Read `envelopes/challenger-01.yaml` to `challenger-03.yaml` of the proposal (no `round` marker,
  `severity: medium`) against `review-loop.md` section 1 on `main`.
- **Expected / Actual**: Expected a defined count; observed a choice between round 1 (markers) and round 4
  (envelopes).
- **Versions**: devkit-spec on `main` at c93f347; branch `plan-worktree-host-compatibility` cut at 298dd9e.
- **Conditions**: local-orchestrated Planning, activity-effort `high`, procedure integrated on `main` mid-Planning.
- **Workarounds Attempted**: none other than the interpretation above.
- **Related Assets**: `references/review-loop.md`; `planning-worker` step 4; the bounded review loop ADR on `main` (not yet on this branch).

## Evidence

```text
review-loop.md, section 1: "Counts are read from these markers, never from new fields."
challenger-03.yaml: summary: 'Third round: no high finding; ...'  severity: medium
git -C <worktree> ls-tree plan-worktree-host-compatibility -- .../skills/spec/references/review-loop.md -> no output
```

Historical source: Git `1b8478093a44cf2d0b74c412bffc93f259459ef0:docs/proposals/PROP-worktree-host-compatibility/feedback/review-loop-round-count-across-procedure-change.md`; relative evidence paths refer to that proposal bundle.

- **Disposition**: `PROP-envelope-record-gaps` Q1 and `PADR-reverify-closes-challenger-rounds` explicitly receive
  unmarked high-effort round counting and answer-fold behavior. The accepted design keeps old high rounds in the
  count and grants the defined answer-fold recovery round. Implementation is pending; this is promotion, not resolution.
