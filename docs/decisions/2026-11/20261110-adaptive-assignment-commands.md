---
id: ADR-adaptive-assignment-commands
title: Adaptive assignment commands
summary: For adaptive delegation whose assignment board lives only in the Host's context, we add a devkit adaptive assignment command group that records assignments and verifies returns against the repository, to make resume and return checks deterministic, accepting a CLI the first decision excluded.
proposal: SPEC-adaptive-assignment-cli
supersedes: [ADR-adaptive-development-and-research]
status: accepted
created_at: 2026-11-10
---

# [ADR-adaptive-assignment-commands] Adaptive assignment commands

- **Status**: Accepted
- **Date**: 2026-11-10

---

## 1. Context & Problem Statement

Adaptive development is guidance: `CAP-DLV-adaptive-development` excludes a runtime scheduler and states that no
adaptive-development runtime or CLI is added. `ADR-adaptive-development-and-research` names its identifiers and
commands `adaptive-dev`. The Host therefore keeps delegated assignments in its context and in
`.devkit/adaptive-dev.md`, which it updates when useful and before pausing. An unplanned interruption or a context
compaction loses the outstanding assignments, and a returned result is checked by reading its diff.
`MAT-adaptive-runtime-references` records that comparable harnesses write this state in code at each event, and that
an adaptive assignment already names a worktree, a base and a write scope that a command can compare with the
repository.

## 2. Decision Drivers

- Outstanding assignments survive an interruption without relying on conversation history.
- A return is compared with repository facts, not with the shape of a report.
- No scheduler, process runner, model routing or per-change SDD record enters adaptive development.
- Reusable archetypes keep working for callers that never use the commands, including SDD callers.
- Judgments that need product knowledge stay with the Host.

## 3. Considered Options

- **Keep guidance only**: no new surface, but the two failures above stay.
- **Commands that record and verify, run by the delegating agent** (chosen): deterministic state and checks, with
  one command group and a ledger to maintain.
- **Commands that also dispatch agents, run declared checks or block completion**: closer to the reference
  harnesses, but it adds the process runner and gates that the milestone excludes or defers to
  ~~`PROP-adaptive-lifecycle-hooks`~~ (rejected in `8a725e5d`).

## 4. Decision Outcome

Chosen: commands that record and verify. This replaces one clause of `ADR-adaptive-development-and-research`:
"Identifiers and commands use `adaptive-dev`" stays in force for the approach value, the bundle, the entry skill and
the context file, and no longer covers the command group, which is named after the distribution.

The sentence "No adaptive-development runtime or CLI is added" is capability text
(`CAP-DLV-adaptive-development` §4); this decision is the record that replaces it there. In
`ADR-adaptive-development-and-research` the phrases "without another release wheel or runtime service" and "No new
runtime, CLI or distribution mechanism" are decision drivers of the adaptive-dev bundle and of the deep-research
split. They are not decision clauses, they stay as written, and this decision supersedes neither: it adds a command
group and no runtime service, scheduler or process runner.

- The command group is `devkit adaptive`, not `devkit adaptive-dev`. → `CAP-DLV-adaptive-development` rule 18 (MUST).

- Adaptive development has a command group `devkit adaptive assignment` with the verbs `new`, `return`, `verify`,
  `close`, `list` and `show`. → `CAP-DLV-adaptive-assignments` §4 (MUST).
- The commands record and compare. They start no agent, run no declared check, create no worktree and block no
  session. → `CAP-DLV-adaptive-assignments` §2 Scope Excluded.
- Verification compares repository facts with the assignment: the recorded base is an ancestor of the returned
  commit, the worktree HEAD is the returned commit, every changed path lies inside the write scope, and every
  declared check has a recorded passing outcome. → `CAP-DLV-adaptive-assignments` §3 (MUST).
- A failed verification is a negative result with exit code `1` and one stable code per failed check.
  → `CAP-DLV-adaptive-assignments` §4 (MUST).
- The delegating agent runs the commands: the Host for its assignments, a `swarm-worker` lead for its children.
  Assignees, product-support roles and verifier or planner leads run none of them, because their contracts keep Git
  read-only (`ADR-skill-local-swarm-roles`), and no archetype requires them. → `CAP-DLV-adaptive-development` rules
  13 and 19.
- Recording is the Host's standard delegation step and never a gate. The commands ship in the same wheel as the
  guidance, so the guidance states the steps without an availability condition. When a command cannot record (an
  unsupported repository, an unwritable or unreadable ledger, a denied write), the Host keeps the manual board and
  diff reading and reports the assignments as unrecorded. → `CAP-DLV-adaptive-development` rules 13 and 14 (SHOULD).
- Recording validates the governing documents an assignment names (`ADR-adaptive-requires-document-system`).
  → `CAP-DLV-adaptive-assignments` §3 (MUST).
- The Host keeps these judgments: whether a returned result meets its goal, whether a recorded check outcome is
  true, whether an open assignment's agent is still running, capacity and allowance, shared-interface agreement, and
  acceptance of a result whose verification failed.
- The commands apply under either development approach and write no SDD record.

## 5. Consequences

- Positive: resume lists outstanding assignments from recorded state; out-of-scope writes, a moved HEAD and a missing
  check outcome have stable codes.
- Negative: a second place holds resume facts beside `.devkit/adaptive-dev.md`; the guidance states which holds what.
- Risk: a recorded check outcome repeats what the assignee reported. The capability states that verification
  compares outcomes and does not run checks.
- Follow-up: ~~`PROP-adaptive-lifecycle-hooks`~~ (rejected in `8a725e5d`) investigated whether a host gate reads the
  ledger; `ADR-reject-adaptive-lifecycle-hooks` records that no gate is delivered.

## 6. Confirmation

Tests of the `assignment` feature in `devkit-adaptive` for each rule of `CAP-DLV-adaptive-assignments`, the
documented-codes test of the package, and the bundle content tests that assert the recording steps and the fallback
in the guidance.
