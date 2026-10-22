---
id: FB-question-option-conditional-fallback
title: Question guidance does not ask a conditional option to state its fallback
scope: repo
kind: friction
category: unclear-instruction
target: spec skill references/worker-records.md (questions)
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-19
---

# [FB-question-option-conditional-fallback] Question guidance does not ask a conditional option to state its fallback

## 1. Friction / Question (friction, question)

- **Context**: this Planning turn folded the user's answers to `worker-03` of `SPEC-draft-direct-acceptance`. The
  recommended option `positive-base-check` of `base-checkout-definition` reads: "its branch must equal the integration
  base (the origin/HEAD target when it resolves, as the integration resolves it). Anything else is refused." The user
  chose it.
- **Expectation**: a chosen option settles every case it names, so the fold only writes it down.
- **Actual**: the option names a condition ("when it resolves") but not what holds when `origin/HEAD` does not
  resolve, for example in a repository without a remote. The same PADR allows that case ("or that there is no
  remote"). Read literally, "anything else is refused" would block every direct acceptance there.
- **Workaround (or Interpretation Chosen)**: the fold takes the main worktree's branch as the base when `origin/HEAD`
  does not resolve. That is how `devkit worktree` treats the base checkout (`lifecycle.py`, `base_branch`). A detached
  `HEAD` and `plan-*` or `dev-*` branches are still refused. The worker envelope lists this reading as an assumption,
  so the plan-accept request shows it to the user. No new question was opened, because the caller asked for a
  completed turn and the reading follows from the option text and the code.
- **Suggestion**: in `worker-records.md` (Questions), add that an option which depends on a condition also states
  what happens when the condition does not hold. Then the user's choice leaves no case for the fold to fill in.

## Diagnostic Details

- **Reproduction**: write an option with "X when it resolves", have the user choose it, then fold it.
- **Expected / Actual**: expected a complete rule. Actual: the else case had to be derived.
- **Versions**: branch `plan-draft-direct-acceptance`, after `fd6730d`; installed `spec` skill.
- **Conditions**: options that depend on an environment condition (a remote, a resolved ref).
- **Workarounds Attempted**: the interpretation above, recorded as an assumption.
- **Related Assets**: `envelopes/worker-03.yaml`, `envelopes/answer-02.yaml`,
  `ADR-direct-acceptance-command-and-handoff-guard`.

- **Disposition**: `session` task `dev-feedback-resolutions`: updated `packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/worker-records.md` (section 1, Questions) to require stating what holds when a condition does not hold for conditional question options, avoiding inference during answer folding. Synced to managed files and projections via `devkit sync`.

