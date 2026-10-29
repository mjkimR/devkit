---
name: incubate
description: Develop or resume an incomplete product idea through adaptive clarification, research, implementation and usage verification without SDD delivery records. Use only when the effective project approach is incubation.
---

# Incubate

Take the next useful action toward the user's product goal, keeping enough current evidence to resume in another session.

## Constraints

- Before product actions, run `uv run devkit config show` and use its effective `configuration.development.approach`, not bundle selection or installed packages. If inspection fails, stop product work and report its code and configuration action. If the approach is not `incubation`, stop product work and explain the shared `.devkit/config.toml` setting `[development] approach = "incubation"`; change it only on the user's direction.
- Do not classify edits into SDD depths or require per-change proposals, Units, approvals or envelopes; never reopen retained SDD decisions or completed artifacts.

## Procedure

1. Once per agent context, read `uv run devkit get-context incubation` (its rules apply throughout), existing `.devkit/incubation.md` and the repository's relevant run instructions.
2. Reuse known facts; read `references/discovery.md` when the next action needs product clarification or comparison.
3. Choose the next action from the missing evidence; research or implementation may start before discovery finishes.
4. Read `references/evidence-and-iteration.md` before research, an experiment, implementation or usage verification; then run the action and verify its retained result.
5. Read `references/delegation.md` before assigning a separable question or verification scope to an optional role; inline work needs no role.
6. Read `references/current-context.md` before writing current context, pausing, resuming in another session or answering an explicit SDD adoption request.
7. Write only documents that help the next decision or describe retained behavior.
8. Present a goal or constraint change to the user before dependent work.
9. Fix failed retained behavior, rerun its affected checks and report remaining gaps.

## Completion of an action

- State the observed result, source/artifact identity, checks actually run, limitations and next useful action.
- Update `.devkit/incubation.md` when resume facts change, preserving unrelated content.
- Never claim that an unexecuted check passed or that an abandoned experiment is retained behavior.
- Continue authorized work while a useful next action remains; incubation never requires eventual SDD adoption.
