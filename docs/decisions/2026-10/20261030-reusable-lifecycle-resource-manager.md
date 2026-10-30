---
id: ADR-reusable-lifecycle-resource-manager
title: Reusable git-operator lifecycle execution with lean
summary: "For local orchestration, we reuse git-operator with the user-selected lean preset, to reduce Host operational context while preserving decisions, accepting limited live coverage and unproven total-cost benefits."
proposal: SPEC-local-orch-resource-manager
status: accepted
created_at: 2026-10-29
supersedes:
  - ADR-host-cli-lifecycle-authority
  - ADR-orchestration-workers
  - ADR-five-subagent-levels
---

# [ADR-reusable-lifecycle-resource-manager] Reusable git-operator lifecycle execution with lean

- **Status**: Accepted
- **Date**: 2026-10-29

## 1. Context & Problem Statement

The Host handles recurring preparation, handoff, integration execution and recovery while also maintaining user
discussion. `ADR-orchestration-workers` makes Planning/Development workers one-shot and keeps lifecycle work in
the Host. `ADR-host-cli-lifecycle-authority` binds business decisions to the Host but existing guarded CLI execution
can be delegated without changing that authority.

`MAT-resource-manager-planning-evidence` found 12/12 safe core decisions from both requested model configurations
and matching live read-only state reports. It did not measure lifecycle mutation reliability, token cost or
conversation availability. The user selected the role name `git-operator` and the existing `lean` preset.
Terra medium was not part of the probe; that choice is not inferred from the Sol results.

## 2. Decision Drivers

- Reduce the Host's operational instructions and intermediate output across multiple units.
- Preserve exact approval scope, CLI guardrails, writer ownership and partial-result recovery.
- Reuse native subagent continuation and existing model/config mechanisms.
- Keep the implementation to agent assets, guidance and proportionate contract checks.
- Avoid treating a small instructed replay as proof of lightweight-model execution parity.

## 3. Considered Options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Keep lifecycle execution in Host | No new delegation boundary | Leaves recurring operational context in user conversation |
| Spawn a fresh agent for each operation | Fresh job context | Repeats startup and operating-reference loading |
| Reuse one manager, compact default | Lightweight family for bounded work | Full mutation/recovery parity and net savings are unmeasured |
| Reuse one manager, standard default | Earlier provisional mid-tier baseline | Does not encode the selected Terra medium configuration |
| Reuse git-operator, lean default | Selected name with explicit Sonnet/Terra medium and native Flash fallback | Terra execution and total costs remain unmeasured |

## 4. Decision Outcome

Use one lazily created, reusable `git-operator` per Host conversation and repository, with source `level: lean`.
The name and preset are the user's explicit choices. Preserve existing project overrides. The preset already
exists under `ADR-lean-subagent-level`; this proposal changes no distribution engine or level mappings.
The original Luna/Sol probe does not validate Terra medium or establish a cost advantage.

- The manager owns mechanical preparation/setup, already-authorized handoff/integration execution, exact merged
  resource cleanup and inspection after partial results through existing procedures.
- The Host owns user decisions, unit scheduling, result acceptance and semantic conflict decisions.
- Source-authoring fixes, semantic reconciliation and resolution of merge conflicts remain with the implementer
  or Host. The manager can report that source preparation is required; it does not invent production edits.
- Each job supplies current identities and effect authority. Remembered state never expands that authority.
- Preserve original CLI status/exit/effects separately from role status. Use completed only for all verified
  requested effects/checks, needs_input for a Host-dependent remainder, and failed for execution failure. Always
  carry completed_effects and remaining_effects; zero-exit partial cleanup cannot imply completion.
- After context loss, rebuild from CLI/Git state and current Host input. Do not persist an approval store or a
  git-operator service.
- Serialize conflicting jobs within the conversation and require quiescent writers before cleanup. Do not claim
  repository-wide mutual exclusion.
- Lean selects Sonnet medium on Claude Code and `gpt-6.1-terra` medium on Codex. Antigravity selects Flash
  with effort omitted because the supported native per-role schema cannot express it. Lean guarantees neither
  Flash high effort nor cross-provider quality equivalence; use no prompt-based effort emulation.

This decision supersedes only Host-only lifecycle invocation clauses in `ADR-host-cli-lifecycle-authority` and
`ADR-orchestration-workers`; keep their unrelated authority, worker and recovery decisions. Supersede the
scout-only source-preset/default-inheritance clause of `ADR-five-subagent-levels` for this manager; preserve
its preset mappings and unrelated distribution policy.

## 5. Consequences

The Host needs dispatch, approval and exception guidance; operation-specific CLI steps and logs reside in the
manager's context. Normal integration keeps its existing combined cleanup, without a redundant manager cleanup job.

The role may increase total tokens. Reuse grows its own context and one Luna follow-up in the probe failed without
a diagnostic before a changed-input retry completed. No reliability or cost ranking follows from that event.
Only the Codex read-only invocation path was live exercised; other host and mutation coverage stays explicit.

`MAT-git-operator-development-evidence` records selected Terra medium native read-only continuation and
separately labels partial-result replay and isolated CLI mutation fixtures. Terra-driven lifecycle mutation and
other live hosts remain unexercised. Preserve the earlier Luna/Sol outputs as historical evidence; do not transfer
Sol results to Terra. Require no new model router or automatic escalation to use lean.

## 6. Confirmation

- Development adds role-contract and projection checks under
  `packages/devkit-spec/tests/integration/bundles/spec/`.
- Review compares caller and role instructions for approval retention, exact job scope, partial/unknown recovery,
  output bounds and lack of production-authoring authority.
- Development exercises repeated jobs and isolated lifecycle fixtures with source/worktree/ref guards.
- Review only: expected conversation availability and total-cost improvement remain unmeasured in Planning.
