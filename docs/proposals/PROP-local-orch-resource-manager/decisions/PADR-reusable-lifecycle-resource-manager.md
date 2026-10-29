---
id: PADR-reusable-lifecycle-resource-manager
title: Reusable lifecycle execution with a standard model default
summary: "For local orchestration, we reuse a lifecycle executor with an initial standard model default, to reduce Host operational context while preserving decisions, accepting an unproven total-cost benefit and compact-model overrides."
proposal: PROP-local-orch-resource-manager
status: draft
created_at: 2026-10-29
---

# [PADR-reusable-lifecycle-resource-manager] Reusable lifecycle execution with a standard model default

- **Status**: Draft
- **Date**: 2026-10-29

## 1. Context & Problem Statement

The Host handles recurring preparation, handoff, integration execution and recovery while also maintaining user
discussion. `ADR-orchestration-workers` makes Planning/Development workers one-shot and keeps lifecycle work in
the Host. `ADR-host-cli-lifecycle-authority` binds business decisions to the Host but existing guarded CLI execution
can be delegated without changing that authority.

`MAT-resource-manager-planning-evidence` found 12/12 safe core decisions from both requested model configurations
and matching live read-only state reports. It did not measure lifecycle mutation reliability, token cost or
conversation availability. A role-wide model default still needs an explicit, reversible choice.

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
| Reuse one manager, standard default | Mid-tier initial operator baseline | May spend more than compact without improving outcomes |

## 4. Decision Outcome

Recommend one lazily created, reusable `resource-manager` per Host conversation and repository, with initial
`level: standard`. Keep `compact` as a project override. This is a provisional default chosen for the full
execution role; the probe does not show Luna to be unsafe or Sol to be cost-effective.

- The manager owns mechanical preparation/setup, already-authorized handoff/integration execution, exact merged
  resource cleanup and inspection after partial results through existing procedures.
- The Host owns user decisions, unit scheduling, result acceptance and semantic conflict decisions.
- Source-authoring fixes, semantic reconciliation and resolution of merge conflicts remain with the implementer
  or Host. The manager can report that source preparation is required; it does not invent production edits.
- Each job supplies current identities and effect authority. Remembered state never expands that authority.
- After context loss, rebuild from CLI/Git state and current Host input. Do not persist an approval store or a
  resource-manager service.
- Serialize conflicting jobs within the conversation and require quiescent writers before cleanup. Do not claim
  repository-wide mutual exclusion.
- Standard means Sol on Codex and Sonnet on Claude under the existing preset. Antigravity standard inherits;
  existing project mappings can select its available model without changing distribution behavior.

On promotion, supersede only Host-only lifecycle invocation clauses in `ADR-host-cli-lifecycle-authority` and
`ADR-orchestration-workers`; keep their unrelated authority, worker and recovery decisions.

## 5. Consequences

The Host needs dispatch, approval and exception guidance; operation-specific CLI steps and logs reside in the
manager's context. Normal integration keeps its existing combined cleanup, without a redundant manager cleanup job.

The role may increase total tokens. Reuse grows its own context and one Luna follow-up in the probe failed without
a diagnostic before a changed-input retry completed. No reliability or cost ranking follows from that event.
Only the Codex read-only invocation path was live exercised; other host and mutation coverage stays explicit.

Reconsider the shipped model default after matched live jobs show compact preserves effect scope and recovery
without extra Host reconstruction. Require no new model router or automatic escalation to change the preset.

## 6. Confirmation

- Development adds role-contract and projection checks under
  `packages/devkit-spec/tests/integration/bundles/spec/`.
- Review compares caller and role instructions for approval retention, exact job scope, partial/unknown recovery,
  output bounds and lack of production-authoring authority.
- Development exercises repeated jobs and isolated lifecycle fixtures with source/worktree/ref guards.
- Review only: expected conversation availability and total-cost improvement remain unmeasured in Planning.
