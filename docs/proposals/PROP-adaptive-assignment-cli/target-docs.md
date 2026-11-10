---
id: PROP-adaptive-assignment-cli-target
title: Target Living Spec Structure for PROP-adaptive-assignment-cli
status: draft
proposal: PROP-adaptive-assignment-cli
created_at: 2026-11-10
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md
  - file: docs/usecases/delivery/UC-advance-an-idea.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/development/reference/adaptive.md
  - file: docs/development/reference/README.md
---

# [Blueprint] PROP-adaptive-assignment-cli: Target Living Spec Structure for Assignment ledger and return verification commands for adaptive delegation

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-adaptive-assignment-cli is accepted. It represents a hypothesis plan subject to adjustment during implementation. Upon handoff, it is copied into specs/ to serve as a baseline for plan.md boundaries and reconcile.md targets.

---

## 1. System Capabilities Plan (docs/capabilities/)

- New CAP-DLV-adaptive-assignments (`docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md`): the contract of
  `devkit adaptive assignment`.
  - Scope: recording, return, verification, closing and listing of delegated assignments. Scope Excluded: starting
    agents, running declared checks, creating worktrees, blocking a session, pruning, an MCP service, glob scopes.
  - Rules, one EARS sentence each with its test path: the ledger location and append-only writes under the lock;
    the unterminated final fragment; the write-scope prefix rule; overlap refusal and its two exemptions; nesting depth
    and narrowed authority; each verification check with its code; the changed-path definition; `close` with
    `--reason` and `ADAPTIVE_CLOSED_UNVERIFIED`; the facts `list` observes; no change to any tracked file or
    `git status` result; approach independence.
  - Interfaces: the command synopsis, sentinels, JSON objects, the assignment fields, the code table with level and
    exit code, and the stated limits of verification (proposal §3.2 to §3.6).
  - Frontmatter `entrypoints`: the feature's CLI module; `usecases`: `UC-advance-an-idea`.
- `CAP-DLV-adaptive-development`:
  - Rule 13 and 13a: WHERE the assignment commands are available, the coordinator SHOULD record each delegated
    deliverable and verify its return with them (CAP-DLV-adaptive-assignments); otherwise the existing manual
    obligations apply unchanged.
  - Rule 14: WHERE the commands are in use, current context names outstanding assignments by ledger ID, and the
    ledger retains their ownership, base and scope.
  - Rule 18: the approach value, bundle, entry skill and context file use `adaptive-dev`; the command group is
    `devkit adaptive` (pending q2).
  - Rule 19: archetypes state no command prerequisite.
  - §2 Scope Excluded and §4 "Distribution and entry": replace "No adaptive-development runtime or CLI is added" by
    a pointer to CAP-DLV-adaptive-assignments; the scheduler, agent bus and model routing exclusions stay.
  - "Integration and final verification": "No implicit Unit or verification ledger is created" becomes a statement
    that integration creates no Unit and that the assignment ledger is explicit, optional and untracked.
  - "Product notes and resume": the relation between `.devkit/adaptive-dev.md` and the ledger.
  - "Evidence-scoring test support" is unchanged.
- `CAP-HARN-command-mount` is unchanged: its exit-code statement names `devkit spec` and `devkit docs` only.

---

## 2. Use Cases Plan (docs/usecases/)

- `UC-advance-an-idea`:
  - 5b: where the commands are available, the Host records the assignment before dispatch and verifies the return.
  - 5b1: a lead records its children under its own assignment and closes them before returning.
  - 5c: a return whose verification fails is rejected with its codes.
  - 7b: on interruption the outstanding assignments stay in the ledger; current context names their IDs.
  - 3a: on resume the Host lists outstanding assignments and treats each open one as interrupted.
  - Scenario "Reject an out-of-scope return" (covers 5b, 5c) and scenario "Resume from recorded assignments"
    (covers 3a, 7b); both state the fallback when the commands are unavailable.
  - `capabilities` gains CAP-DLV-adaptive-assignments.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- `ARCH-05-2-components`: the `assignment` feature of `devkit-adaptive`, its single feature edge to
  `devkit_dist.features.project` and its public list use case.
- Decisions promoted at handoff: `PADR-adaptive-assignment-commands` (supersedes in part
  `ADR-adaptive-development-and-research`) and `PADR-adaptive-assignment-ledger-storage`.
- `ADR-adaptive-development-and-research` gains the partial-supersession line for one clause, "Identifiers and
  commands use `adaptive-dev`", which no longer covers the command group. Under the other answer to q2 the PADR's
  `supersedes` is removed and the ADR does not change.
- The base dependency of `devkit-adaptive` is decided in `PROP-adaptive-package-extraction` (q1).

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- New reference page `docs/development/reference/adaptive.md` with the sections Usage, Output, Error codes and
  Library, modelled on `docs/development/reference/worktree.md`; a row in `docs/development/reference/README.md`.
- `.devkit/architecture.toml`: the feature, its `feature_dependencies` entry and the public module.
- Package README of `devkit-adaptive`: the feature and its modules.
- Bundle guidance: `delegation.md`, `orchestration.md`, `current-context.md`, the current-context template, the
  three archetypes and the bundle constitution (proposal §3.7); a bundle version increase.

---

## 5. System Before & After Comparison (Before & After)

| Aspect | Before | After |
| --- | --- | --- |
| Assignment board | Host context | Ledger under the shared Git directory, written at each event |
| Return check | Host reads the diff | `verify` compares ancestry, HEAD, changed paths and declared checks with the assignment |
| Resume after interruption | `.devkit/adaptive-dev.md` if it was updated | `list` reports outstanding assignments with worktree facts; the Markdown names their IDs |
| Nesting | Stated in the payload | Depth and narrowed authority refused at `new`; open children fail the parent's verification |
| Commands unavailable | Not applicable | The manual procedure, unchanged |
| Scheduler, runner, hooks | None | None |
