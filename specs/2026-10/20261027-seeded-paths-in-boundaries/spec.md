---
id: SPEC-seeded-paths-in-boundaries
title: Seeded and synced paths in proposal boundaries
summary: Lets a proposal's write scope cover the tracked files devkit sync writes because of the agreed change, such as a new seed in a selected preset, so Development does not stop on a path Planning could not name.
status: in-progress
created: 2026-10-27
related_capabilities: [CAP-DLV-delivery-workflows]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-seeded-paths-in-boundaries] Seeded and synced paths in proposal boundaries

## 1. Problem Statement & Motivation

Handed off from proposal PROP-seeded-paths-in-boundaries on 2026-10-27; the decision is
`ADR-admit-change-sync-outputs`.

A proposal's `boundaries.owns` becomes Development's write scope, and `RULE-proposal-boundaries` admits only paths
that exist at Planning (or their nearest parent). A change that adds a seed to a preset the repository selects makes
`devkit sync` write a new tracked file, such as `docs/ux/README.md` from the `docs-skeleton` seed in
`SPEC-ux-documentation`, that Planning could not name. The Host builds the payload before the change exists, so
`devkit sync --check` on the accepted head lists no new seed, and the `development-worker` contract treats the omitted
output as a problem. The worker then stops until the Host admits the path by hand.

The stop comes from two sentences: the `spec-delegate` payload reference's "tracked files `devkit sync --check` lists
for that change" and the `development-worker` contract's "A tracked sync output the write scope omits is a problem".
This change replaces them with a standing class of admitted sync outputs, a recorded clean starting sync and a Host
check against the installation receipt. It is wording only.

## 2. User Stories

- **US-1**: As a Host delegating a bundle-source change, I want the write scope to admit every tracked path
  `devkit sync` writes from the change, so that a worker does not stop on a seeded path Planning could not name.
- **US-2**: As a Host validating a returned worker, I want each admitted sync output recorded in `_Boundary:` and
  checkable against `.devkit/installation.json`, so that I can tell it from an unrelated out-of-scope write.

## 3. Non-Goals

1. **Scope Excluded**: no change to `RULE-proposal-boundaries`, `devkit spec worker inspect`, `devkit sync` or any
   CLI; no derivation command (Q1) and no declaration syntax for not-yet-existing paths (Q2).
   - **When to Reconsider**: a worker records a `(sync output)` path the receipt does not hold, or the class proves
     ambiguous twice (`ADR-admit-change-sync-outputs`, Follow-up).
2. **Scope Excluded**: `.devkit/managed/` stays ignored and never a write path.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The payload admits the change's sync outputs as a class
- **Given** the rendered `spec-delegate` `references/payload.md` for the `local` and `cloud` environments
- **When** the Host reads the bundle-source bullet
- **Then** it states that the write scope admits every tracked path `devkit sync` writes in the worktree after the
  change (seeded files, projected files, `.devkit/installation.json` and the managed `AGENTS.md` block), not only the
  files `devkit sync --check` lists before the change, and that `.devkit/managed/` is ignored and never a write path;
  the sentence "add the tracked files `devkit sync --check` lists for that change" is gone

### [AC-02] The worker records a clean start and each unlisted output
- **Given** the rendered `development-worker` contract for both environments
- **When** the worker edits a bundle source the project selects
- **Then** step 5 tells it to run `devkit sync --check` before the first edit and record its exit as the `sync_start`
  check of the `worker` envelope, with a nonzero exit a problem and never a `(sync output)`; to run `devkit sync` and
  commit every tracked file it writes; and to name each one the payload did not list in the owning task's
  `_Boundary:` with the note `(sync output)` and in the `worker` envelope summary
- **And** the Write boundaries' `.devkit/` denial excepts these sync outputs, and the sentence "A tracked sync output
  the write scope omits is a problem" is gone

### [AC-03] The Host checks each recorded sync output against the receipt
- **Given** the `spec-delegate` `references/worker.md` Validate section
- **When** `tasks.md` gained a `(sync output)` entry between `<accepted>` and `<returned>`
- **Then** it states that `devkit spec worker inspect`'s scope pass is no evidence for that entry, and that the path
  passes only when all of these hold: the worker's `sync_start` check is `0`; `devkit sync --check` exits `0` on the
  returned head; and the path is under `seeded` or `files` in the returned head's `.devkit/installation.json`, is
  `.devkit/installation.json` itself, or is the file that holds the managed guidance block (`AGENTS.md`)

### [AC-04] The Living Spec states the rule
- **Given** `CAP-DLV-delivery-workflows`
- **When** a reader looks up delegated bundle-source changes
- **Then** the sentence states the admitted class, the `sync_start` check, the `(sync output)` record and the Host's
  receipt check, citing `ADR-admit-change-sync-outputs`

### [AC-05] The guidance test pins the new wording
- **Given** `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`
- **When** `just test devkit-spec` runs it
- **Then** it asserts the new payload, worker-contract and Validate sentences for both environments and exits `0`

## 5. Assumptions

- The `sync_start` check is recorded with the existing `--check` option as `sync_start=PASS exit 0` (or `FAIL`
  with the exit code); no record schema changes.
- `AGENTS.md` is named as the file holding the managed guidance block because the receipt records that block only as
  a hash.

## 6. Source feedback

- `FB-new-seed-sync-output-outside-boundaries`: the whole observation, a seeded path outside the handed-off write
  scope that stopped Development. It is already `promoted`; this change leaves it as is.
