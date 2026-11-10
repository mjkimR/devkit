---
id: ADR-adaptive-assignment-ledger-storage
title: Assignment ledger in the shared Git directory
summary: For assignment state that the Host and role leads in other worktrees read and write, we keep an append-only JSON Lines ledger under the shared Git directory, to give every linked worktree one untracked record, accepting that another clone starts without it and sandboxes may ask approval.
proposal: SPEC-adaptive-assignment-cli
status: accepted
created_at: 2026-11-10
---

# [ADR-adaptive-assignment-ledger-storage] Assignment ledger in the shared Git directory

- **Status**: Accepted
- **Date**: 2026-11-10

---

## 1. Context & Problem Statement

The assignment commands (`ADR-adaptive-assignment-commands`) need one record that the Host reads and writes from its
checkout and a role lead from another worktree. Parallel writers each own a worktree on its own branch, so a file in
the working tree is either tracked, and differs per branch, or ignored, and exists per checkout. A later consumer
(`PROP-adaptive-lifecycle-hooks`) reads the same record from whichever checkout a host session runs in.

## 2. Decision Drivers

- Every linked worktree of the repository reads and writes the same record.
- Recording changes no tracked file and no `git status` result, because verification reads `git status`.
- The record survives an interrupted write and concurrent writers.
- The record keeps the order and time of transitions for resume.
- Location and format follow an existing precedent where one exists.

## 3. Considered Options

- **Tracked project file**: visible in review, but each branch holds its own copy, every write dirties the Host
  checkout, and history gains a per-change record that adaptive development excludes.
- **`.devkit/transient/` of the main worktree**: writable inside the Host's sandbox, but the directory is defined as
  checkout-local, a lead must resolve another checkout to reach it, and `git clean -fdx` removes it.
- **Shared Git directory** (chosen): one record for all worktrees with the precedent of `devkit exec` and the spec
  scope registry; another clone has no record, and a sandboxed host may ask approval for the write.

Format options, compared in the proposal's `docs/materials/2026-11/20261110-adaptive-assignment-cli/planning-evidence.md` §5: one JSON document, one JSON file per
assignment, or an append-only JSON Lines event log (chosen).

## 4. Decision Outcome

Chosen: an append-only event log under the shared Git directory.

- The ledger is `<git common dir>/devkit/adaptive/ledger.jsonl`, found with
  `git rev-parse --path-format=absolute --git-common-dir`. → CAP-DLV-adaptive-assignments §4 (MUST).
- Each line is one JSON event with a schema number, a UTC timestamp, an event type and the assignment ID. Commands
  append and never rewrite a line. The state of an assignment is the fold of its events.
  → CAP-DLV-adaptive-assignments §4 (MUST).
- Every write holds an exclusive lock on `<git common dir>/devkit/adaptive/lock` while it reads, validates and
  appends. → CAP-DLV-adaptive-assignments §3 (MUST).
- Bytes after the last newline are a fragment of an interrupted append, not an event. A reader skips the fragment and
  reports a warning; a writer truncates it under the lock before appending. A newline-terminated line that cannot be
  parsed, or an unknown schema number, stops the command. → CAP-DLV-adaptive-assignments §3 (MUST).
- The file layout is private to the `assignment` feature. Other code and later hook handlers read assignments through
  `devkit adaptive assignment list --format json` or the feature's list use case.
- `.devkit/adaptive-dev.md` stays Host-authored Markdown. No command reads or writes it.

## 5. Consequences

- Positive: a lead and the Host see the same assignments; the working tree and index never change; an interrupted
  append leaves at most one fragment, which the next write removes.
- Negative: the ledger does not travel with a clone, a push or a copy of the working tree. Current context then names
  assignment IDs that the ledger lacks, and the Host recovers from the implementation as for stale context.
- Negative: on a host whose sandbox protects the shared Git directory, each recording command needs approval. A
  write the file system refuses is `ADAPTIVE_LEDGER_UNWRITABLE`; a write the host denies never reaches the command.
  In both cases the Host falls back to the manual board and does not reroute the write.
- Risk: the ledger grows with every event. No pruning command is added; a follow-up is triggered when a real ledger
  makes `list` slow.

## 6. Confirmation

Integration tests that record from a linked worktree and list from the main worktree, that leave `git status`
unchanged after each command, that append concurrently under the lock, and that read a ledger with an unterminated
final fragment before and after the next write.
