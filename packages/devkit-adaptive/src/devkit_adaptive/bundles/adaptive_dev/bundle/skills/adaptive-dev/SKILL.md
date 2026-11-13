---
name: adaptive-dev
description: Develop or resume an incomplete product idea through adaptive clarification, research, implementation and usage verification without SDD delivery records. Use only when the effective project approach is adaptive-dev.
---

# Adaptive development

Take the next useful action toward the user's product goal, keeping enough current evidence to resume in another session.

## Constraints

- Before product actions, check the effective `configuration.development.approach` from `uv run devkit config show`, not bundle selection or installed packages. If inspection fails, stop product work and report it. If it is not `adaptive-dev`, stop product work and explain the shared `.devkit/config.toml` setting `[development] approach = "adaptive-dev"`; change it only on the user's direction.

## Procedure

1. Once per agent context, read `uv run devkit get-context adaptive-dev` (its rules apply throughout), existing `.devkit/adaptive-dev.md` and the repository's relevant run instructions.
2. Reuse known facts and ask ordinary small questions inline. Read `references/discovery.md` when the next action needs product clarification or comparison.
3. Choose the next action from the missing evidence; research or implementation may start before discovery finishes.
4. Read `references/evidence-and-iteration.md` before research, an experiment, implementation or usage verification; run the action and verify its retained result.
5. Actively delegate useful separable planning, research, implementation and verification; read `references/delegation.md` before assigning it. Keep decomposition, coordination, integration and final validation with the main agent.
6. Read `references/orchestration.md` when coordinating parallel writers, role leads, combined checks or interruption recovery.
7. Read `references/current-context.md` before writing current context, pausing, resuming in another session or answering an explicit SDD adoption request.
8. Write only documents that help the next decision or describe retained behavior; read `references/documents.md` before partitioning against project documents, settling a shared interface that outlives its assignment, integrating a retained result or writing a project document.
9. Fix failed retained behavior, rerun its affected checks and report remaining gaps.

## Completion of an action

- State the observed result, source/artifact identity, checks actually run, limitations and next useful action.
- Continue authorized work while a useful next action remains; adaptive development never requires SDD adoption.
