---
name: incubate
description: Develop or resume an incomplete product idea through adaptive clarification, research, implementation and usage verification without SDD delivery records. Use only when the effective project approach is incubation.
---

# Incubate

Take the next useful action toward the user's product goal; keep enough current evidence to resume another session.

## Constraints

- Inspect `uv run devkit config show` before product actions and use its effective `configuration.development.approach`, not bundle selection or installed packages.
- If inspection fails, stop product work and report its code and configuration action.
- If the effective approach is not `incubation`, stop product work and explain the shared `.devkit/config.toml` setting `[development] approach = "incubation"`; obtain the user's direction before changing the project's approach.
- Do not classify ordinary incubation edits into SDD depths or require per-change proposals, Units, approvals or envelopes.
- Preserve existing SDD history; incubation does not grant permission to reopen its retained decisions or completed artifacts.
- Preserve independent project checks and the host's permissions for files, external services and Git actions.

## Procedure

1. Read `uv run devkit get-context incubation` once per agent context, existing `.devkit/incubation.md` and the repository's relevant run instructions.
2. Reuse facts already in the conversation and repository; read `references/discovery.md` when the next action needs product clarification or comparison.
3. Choose the next useful action from the missing evidence; do not require discovery to finish before research or implementation starts.
4. Read `references/evidence-and-iteration.md` before research, an experiment, implementation or usage verification; execute the agreed action and verify its retained result.
5. When a question or verification scope separates usefully, read `references/delegation.md` before optionally assigning it; inline work needs no role invocation.
6. Read `references/current-context.md` before writing current context, pausing, resuming in another session or responding to an explicit SDD adoption request.
7. Before document authoring, read `uv run devkit get-context docs`; write only documents that help the next decision or describe retained behavior.
8. If the product goal or constraints change, present that decision to the user before dependent work; ordinary implementation choices inside them need no new ceremony.
9. Fix failed retained behavior and rerun its affected checks; keep unavailable, skipped or inconclusive evidence visibly unverified.

## Completion of an action

- State the observed result, source/artifact identity, actual checks, limitations and next useful action.
- Update `.devkit/incubation.md` when facts needed for resume change; preserve unrelated project content.
- Leave no claim that an unexecuted check passed or that an abandoned experiment is retained behavior.
- Continue authorized work when a useful next action remains; incubation does not require eventual SDD adoption.
