---
id: PADR-admit-change-sync-outputs
title: Admit sync outputs of the change by procedure
summary: For delegated bundle-source changes, we admit every tracked path devkit sync writes from the change as a standing write-scope class recorded in _Boundary, to stop no worker on an unnamed seeded path without new code, accepting a Host check against the installation receipt.
proposal: PROP-seeded-paths-in-boundaries
status: draft
created_at: 2026-10-27
---

# [PADR-admit-change-sync-outputs] Admit sync outputs of the change by procedure

- **Status**: Draft
- **Date**: 2026-10-27

---

## 1. Context & Problem Statement

A delegated Development worker writes only its payload's write scope. For a change to a bundle source the project
selects, `spec-delegate`'s payload reference tells the Host to add "the tracked files `devkit sync --check` lists for
that change", and the `development-worker` contract treats a tracked sync output the write scope omits as a problem.
The Host builds the payload before the change exists, so `devkit sync --check` on the accepted head lists nothing
for a seed the change adds. A new seed path in a selected preset, such as `docs/ux/README.md` from
`SPEC-ux-documentation`, is therefore always outside the named scope, and the worker stops until the Host admits it.
A worker told up front that such outputs are admitted completed without stopping.

## 2. Decision Drivers

- No Development stop on a path that follows mechanically from the agreed change.
- No new code, command or rule mode when procedure suffices.
- The Host can still tell an admitted sync output from an unrelated out-of-scope write.

## 3. Considered Options

- **Keep the current state**: the Host admits each new seeded path by hand after a worker problem; one stop per new
  seed, as observed.
- **Derive the outputs in code (Q1)**: a command lists the change's sync outputs for the payload; it can run only
  after the change exists, so it serves the Host's validation, not the payload, and duplicates `devkit sync --check`.
- **Declare the outputs in Planning (Q2)**: `RULE-proposal-boundaries` accepts a not-yet-existing seeded target named
  with its seed source; new rule syntax and code for a path the receipt already records after sync.
- **Standing procedure (Q3)**: the write scope admits, as a class, every tracked path `devkit sync` writes from the
  change; the worker records each in `_Boundary:` and the Host checks it against `.devkit/installation.json`.

## 4. Decision Outcome

Chosen: the standing procedure (Q3), because it removes the stop with wording only and keeps the Host's check
deterministic.

- The class is "the tracked paths `devkit sync` writes in the worktree after the change, when `devkit sync --check`
  exits `0` on the accepted head"; a clean starting sync makes every later output a consequence of the change. The
  worker runs that check before its first edit and records it as `sync_start`; a nonzero exit is a problem.
- The worker commits each such path, names it in the owning task's `_Boundary:` with the note `(sync output)`, and
  reports it in its `worker` envelope summary.
- The Host checks each `(sync output)` entry `tasks.md` gained itself, because `devkit spec worker inspect` reads
  `_Boundary:` at the returned head: it passes when `sync_start` is `0`, `devkit sync --check` exits `0` on the
  returned head, and the path is under `seeded` or `files` in `.devkit/installation.json`, is the receipt itself, or
  is the file that holds the managed guidance block.

## 5. Consequences

- Positive: a new seed or projection no longer needs a Host decision per path; `devkit spec worker inspect` derives
  the recorded path from `_Boundary:` with no code change.
- Negative: the Host check is a review step against the receipt, not an automated scope check.
- Follow-up: if a worker records a `(sync output)` path the receipt does not hold, or the class proves ambiguous
  twice, revisit the derivation option (Q1) as a `worker inspect` check.

## 6. Confirmation

`packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py` pins the payload and
`development-worker` wording; the Host's receipt check is Review only.
