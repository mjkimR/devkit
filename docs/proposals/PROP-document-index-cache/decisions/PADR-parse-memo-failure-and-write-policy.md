---
id: PADR-parse-memo-failure-and-write-policy
title: Parse memo failure and write policy
summary: For corrupt, stale or concurrent memos, we treat any unreadable or mismatched memo as empty, rebuild silently, write by atomic replace only from changed working-tree loads, with no lock, to keep every result a fresh build's, accepting lost updates between writers.
proposal: PROP-document-index-cache
status: draft
created_at: 2026-10-22
---

# [PADR-parse-memo-failure-and-write-policy] Parse memo failure and write policy

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

Agents run lookups and rule checks in parallel in the same worktree, a process can be killed while writing, and the
memo file can be truncated, hand-edited or written by another devkit version. None of this may change a command's
result, exit code or advisories: the memo is an optimization the agent never acts on (`ARCH-08-1-agent-output`).
Writing about 1 MB on every call would also cost more than the lookups it serves.

## 2. Decision Drivers

- Every result equals a fresh build, whatever state the memo file is in.
- No new advisory, code or exit status; diagnostics only under `-v`.
- No lock wait on the lookup path and no deadlock between readers and writers.
- No write when nothing changed; rule runs write nothing beyond their fixes.

## 3. Considered Options

- **Lock-protected read-modify-write** (`devkit_core.core.file_lock`): serializes writers, but every lookup takes a
  lock, and a read-only file system or a stuck holder needs extra handling.
- **Lock-free atomic replace, last writer wins**: each writer replaces the file in one rename; a reader sees the old or
  the new memo, never a partial one. Two concurrent writers lose one update, which costs a parse later.
- **Per-entry files**: no lost updates, but hundreds of small files to read per load.
- **Report a corrupt memo as a notice**: visible, but tells the agent nothing it must act on.

## 4. Decision Outcome

Chosen option: **lock-free atomic replace, last writer wins**, with a memo trusted only after validation, because it
meets the identity, silence and no-wait drivers; a lost update only costs a later parse.

- **Discard rules**: a memo that is missing, unreadable, not valid UTF-8 JSON, not the expected shape, of another
  `version` or of another `fingerprint` is treated as empty. An entry whose stored result cannot be rebuilt is a miss.
  In both cases the load parses those files as a fresh build would, and the memo is rewritten.
- **Silence**: discarding or failing to write the memo emits no advisory or notice and never changes the exit status;
  each case logs one `logging` line, visible under `-v`.
- **Writers**: only a load that walks the workspace itself (no caller-supplied file list or reader) writes, and only
  when its entries differ from what it read (a new, changed or removed file, or a discarded memo). Its entries are
  exactly the files that load saw, so deleted and renamed files are pruned. Loads with a supplied file list or reader,
  which the spec rules and Git snapshot runs use, read the memo and never write it.
- **Write**: `devkit_core.core.atomic_write_bytes` (temporary file, then rename). An `OSError` (read-only file system,
  permissions, full disk) is logged under `-v` and ignored.
- **Concurrency**: no lock. Concurrent writers each write a complete memo of entries that matched the text they read;
  whichever lands last is kept, and an entry that no longer matches its file is a miss on the next load.

## 5. Consequences

- Positive: a lookup never waits, never fails because of the memo, and writes nothing in the steady state.
- Positive: rule runs gain the parse reuse without writing to the workspace.
- Negative: concurrent writers can drop each other's new entries; the next load parses those files again and writes.
- Negative: a process killed between the temporary write and the rename leaves a temporary file in
  `.devkit/transient/spec/`, ignored by Git; `atomic_write_bytes` removes it on every error it sees.

## 6. Confirmation

- Tests: a truncated file, invalid JSON, a wrong `version` or `fingerprint`, a malformed entry and a directory in
  place of the file each give results equal to a fresh build, the same exit code, no advisory without `-v` and a
  rewritten memo; an unwritable `.devkit/transient/spec/` gives a fresh build's result.
- Tests: a load with no changed file leaves the memo's bytes and modification time unchanged; a load with a supplied
  file list never creates or changes it.
- Test: several processes loading and writing at once all return a fresh build's result.
