---
id: PADR-inspected-state-identity
title: Inspected-state identity for maintenance runs
summary: "For runs that inspect uncommitted changes, we identify the inspected state by the source SHA, the dirty path list, a temporary-index tree hash and a local diff digest, to make a record reproducible without exposing the diff, accepting that only a retained local diff verifies the digest."
proposal: PROP-maintenance-history
status: draft
created_at: 2026-11-04
---

# [PADR-inspected-state-identity] Inspected-state identity for maintenance runs

- **Status**: Draft
- **Date**: 2026-11-04
- **Deciders**: repository owner
- **Involved Components/Capabilities**: `capabilities/delivery/`, the maintenance playbooks, `packages/devkit/src/devkit_agt/features/`

---

## 1. Context & Problem Statement

Every maintenance playbook records HEAD and the dirty path list at intake, and `CAP-DLV-weekly-report` requires a
preserved diff or artifact reference for selected uncommitted content. A commit SHA alone does not identify a run
that inspected uncommitted changes, and two different dirty contents give the same path list. `source_sha` is
defined as a commit (`CAP-COLL-shared-artifacts`), so a tree hash must not take its place. The run record needs an
identity that a later run can compare and that keeps possibly sensitive diff bytes local.

---

## 2. Decision Drivers

- Driver 1: the same inspected content yields the same identity; different content yields a different one.
- Driver 2: the identity is computed without changing the index, HEAD, refs or working tree.
- Driver 3: the diff bytes stay local unless the run selects them, because they may hold secrets.
- Driver 4: `source_sha` keeps its meaning as a commit for every consumer.

---

## 3. Considered Options

### Option 1: Source SHA, dirty paths, temporary-index tree hash and local diff digest (Selected)
- **Overview**: `source_sha` is HEAD; `dirty_paths` comes from `git status --porcelain`; `inspected_tree` is the
  `write-tree` of a per-run temporary index after `read-tree HEAD` and `add -A` with the exclusion pathspec (the
  `spec-delegate` snapshot procedure); the retained diff file holds `git -c diff.noprefix=false
  -c core.quotepath=false diff --no-ext-diff --no-textconv --no-renames --no-color --binary HEAD` with the same
  pathspec, followed by one entry per untracked path in byte order (8-byte big-endian length and path, 8-byte
  big-endian length and bytes), and `diff_digest` is its SHA-256.
- **Pros**: `inspected_tree` is a content identity that is the same for the same content under the same ignore
  rules and clean filters (Driver 1) with no local Git change (Driver 2); the digest travels, the diff stays (Driver 3); `source_sha` is untouched (Driver 4).
- **Cons**: ignored files are outside `add -A`; `diff_digest` depends on the machine's remaining diff settings, so
  it is reproducible from the retained file, not across machines; a remote reader verifies it only where the diff
  is retained.

### Option 2: Source SHA and the dirty path list only
- **Overview**: what the playbooks record today.
- **Pros**: no new computation.
- **Cons**: fails Driver 1; a rerun cannot prove it inspected the same state.

### Option 3: `git stash create` as a commit-shaped identity
- **Overview**: a dangling commit for the working tree.
- **Cons**: tracked changes only; needs retention of a dangling object; a commit-shaped value invites misuse as
  `source_sha` (Driver 4). Unverified in repository evidence.

---

## 4. Decision Outcome

We decided to adopt **Option 1**.

- A run record identifies its inspected state by `source_sha`, `dirty`, `dirty_paths`, `inspected_tree` and, for a
  dirty run, `diff_digest` with the retained local diff path.
- The comparison set is fixed at `start` and reused at `finish`: it excludes the run directory (where the retained
  diff lives) and the report path required at `start`, through one pathspec applied to both the temporary index and the diff and only for paths inside
  the worktree, so a run's own output never counts as dirty content or as drift.
- `inspected_tree` is the content identity: the same content under the same ignore rules and clean filters gives
  the same tree; its consumer is the start-versus-finish comparison in one checkout, and a comparison across
  checkouts holds only under the same ignore rules and filters.
- The retained diff file is the digest input, produced with the pinned diff options above and the length-prefixed
  untracked entries; `diff_digest` binds the record to that file and a reader with the file recomputes it. The
  digest makes no cross-machine claim.
- A clean run records `inspected_tree` equal to `HEAD^{tree}` and null diff fields.
- The identity is computed through a per-run temporary index file in the Git directory that is deleted after
  `write-tree`; the real index, HEAD, refs and working tree are unchanged, and loose objects the snapshot adds to
  the object store are accepted. A failing clean filter stops the command with `HISTORY_SNAPSHOT_FAILED` and no
  record.
- The diff bytes are published only when the run selects the diff as a published file.
- `source_sha` always names a commit; no tree hash or stash object is placed there.
- Option 1 satisfies all four drivers; Option 2 fails Driver 1 and Option 3 fails Drivers 3 and 4.

---

## 5. Consequences

- **Positive**: later runs compare inspected states exactly; the weekly report's preserved-reference rule is met
  by the digest and the retained diff.
- **Negative / Risks**: ignored files are not part of the identity; a diff retained locally can be lost with the
  checkout, after which the digest is unverifiable.
- **Follow-ups**: none until a consumer needs remote verification of dirty content, which would require publishing
  the diff or its objects.

---

## 6. Confirmation

Tests of `devkit maintenance history start` on a temporary repository: identical content gives identical
`inspected_tree` under different `diff.algorithm` and `diff.noprefix` settings and under the same global excludes
file, a global excludes file that hides an untracked path changes it, `diff_digest` is recomputed from the
retained file alone, a changed file changes both, the run directory and the report path never count as drift
inside or outside the worktree, and `git for-each-ref`, the index checksum and `git status --porcelain` outside the
run directory are unchanged after the command. Restated by the new delivery capability `maintenance-history` (ID assigned at spec-sync).
