---
id: SPEC-document-index-cache
title: Reuse the document index between commands
summary: Persists each Living Spec document's parse result on disk, keyed by its path and a digest of its parsed text, so lookups such as devkit spec resolve and list stop re-parsing every document on each call.
status: planned
created: 2026-10-22
related_capabilities:
  - CAP-DOCS-document-model
  - CAP-DOCS-document-lookup
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-document-index-cache] Reuse the document index between commands

## 1. Problem Statement & Motivation

Handed off from proposal PROP-document-index-cache on 2026-10-22.
- **Preserved Materials**: `docs/materials/2026-10/20261022-document-index-cache`
- **Decisions**: `ADR-content-keyed-document-parse-memo`, `ADR-parse-memo-location-and-format`,
  `ADR-parse-memo-failure-and-write-policy`.

### 1.1 Background

`devkit spec resolve <ID>` takes about 430 ms and `devkit spec list feedback` about 440 ms on this repository
(`docs/materials/2026-10/20261022-document-index-cache/baseline-profile.md`: 693 candidate files, 637 documents).
Both build the full `DocumentIndex` in a new process, and about 300 ms of each call is parsing: YAML frontmatter
through the strict pure-Python loader and the prose reference scan, for every document, even to resolve one ID.
Walking the tree takes 12 to 16 ms and reading every file 8 to 53 ms. Agents call these lookups many times per task.

### 1.2 Hypothesis

A persisted parse memo, keyed by each file's path and a digest of the text parsed, makes the common call a walk, a
read, a hash and a memo decode (about 55 ms instead of 300 ms in the prototype), with results identical to a fresh
build by construction.

## 2. User Stories

- **US-1**: As an agent that runs `devkit spec resolve`, `list`, `search` and `refs` many times per task, I want a
  lookup in an unchanged workspace to skip re-parsing every document, so that each call costs a fraction of today's
  time.
- **US-2**: As a developer, I want the results, exit codes and advisories of every command to stay exactly those of
  a fresh build whatever the state of the memo file, so that I never have to think about it or delete it.

## 3. Design

The design is decided in the three ADRs above; this section states what the implementation delivers.

- **Load**: `DocumentIndex.load` keeps its signature and its walk. For each file it reads the text as today, computes
  the BLAKE2b digest of the UTF-8 encoding of that exact text and takes the stored parse result on an exact path and
  digest match; otherwise it parses as today. A stored result is a document, "no document", the
  `SPEC_DOCUMENT_INVALID` reason of a malformed frontmatter, or an "unstorable" marker (parsed again on every load).
  A file that cannot be read or decoded is reported as today and has no entry. ID and alias maps, `historical`,
  problems and ordering are rebuilt from the entries on every load.
- **Location**: `<root>/.devkit/transient/spec/document-index.json`, used only when `<root>/.devkit/transient/` is a
  directory, neither it, `spec/` nor the memo path is a symbolic link, and the memo path resolves inside `<root>`.
- **Format**: one JSON object with `version`, the parser `fingerprint` and the entries. Strings, booleans, integers,
  finite floats and null stay plain; every list, mapping, `datetime` and `date` is a one-key tagged object (a mapping
  as a list of key-value pairs). Any other value makes the entry unstorable.
- **Fingerprint**: a format version, the source bytes of every module in `devkit_spec.features.documents.models`
  and `devkit_spec.features.documents.repositories` (the memo codec included), `devkit_core.core.frontmatter` and
  `devkit_core.base.errors`, the PyYAML version, libyaml presence and the Python version. When a module's source
  cannot be read, the memo is not used.
- **Failure and writes**: an unreadable, malformed, other-version or other-fingerprint memo is treated as empty, and
  an entry that cannot be rebuilt is a miss. Only a load that walks the workspace itself (no supplied file list or
  reader) writes, only when its entries differ from what it read, by `devkit_core.core.atomic_write_bytes`, without a
  lock. A non-regular file at the memo path is never removed or written. Every discard and failed write is one
  `logging` line, visible under `-v`; none is an advisory.
- **In-process reuse**: the in-process memo stays, so loads within one process parse a text once.
- **Interfaces**: no command, option, output, code or exit status changes.

## 4. Non-Goals

1. **Scope Excluded**: `WorkspaceCache.get_catalog` and the rules workspace cache in devkit-agt. Rationale: a generic
   catalog without the document model, which devkit-agt cannot share with devkit-spec.
2. **Scope Excluded**: a faster strict YAML loader in `devkit_core.core.frontmatter`
   (`FB-strict-frontmatter-loader-without-libyaml` stays open), a stat-signature fast path, and caching the search
   ranking or embeddings of `devkit spec search`.
3. **Scope Excluded**: `devkit-viewer`, which reads documents from Git commits, not through `DocumentIndex`.
4. **Scope Excluded**: interpreter start-up and plugin import time (about 190 ms of `devkit --help`).
5. **Scope Excluded**: a lock, a cleanup command or any option to disable the memo; deleting the file is the reset.

## 5. Acceptance Criteria & Behavioral Contracts

### [AC-01] Identity after workspace changes
- **Given** a workspace with `.devkit/transient/` and a warm memo
- **When** it changes by any of: a content edit (including a same-size edit whose mtime is restored), a new file, a
  deletion, a rename, an alias added, changed or removed, an ID change, a frontmatter turned malformed and back, a
  file turned non-UTF-8, a Git branch switch to a branch with other documents and back, or a changed parser
  fingerprint
- **Then** `DocumentIndex.load` returns documents, `by_id`, `by_alias`, problems and `historical` equal to a load
  without a memo, and `devkit spec list`, `search`, `resolve` and `refs` print the same stdout with the same exit
  code as without a memo

### [AC-02] Identity across readers and line endings
- **Given** CRLF, lone-CR and BOM documents with references and aliases
- **When** they are loaded by a walk and by a rules-style supplied reader that keeps CR, in both orders, with a memo
- **Then** each load equals the same load without a memo, and `devkit rules check` reports and `devkit rules fix`
  results equal those without a memo

### [AC-03] Codec round trip
- **Given** frontmatter with a date, a naive `datetime`, aware `datetime` values (`Z` and `+09:00`), nested integer,
  boolean and null keys and a literal mapping shaped like a tag
- **When** it is encoded and decoded
- **Then** the decoded value equals the original, with the same types and key order; a frontmatter holding a
  non-finite float, a set, bytes or a tuple is stored as an unstorable marker and parsed again on each load

### [AC-04] Corrupt or foreign memo
- **Given** a memo that is truncated, invalid JSON, of another `version` or `fingerprint`, or holding a malformed
  entry
- **When** a command or a walk load runs
- **Then** the result equals a fresh build, the exit code is the same, stderr carries no advisory without `-v`, and
  the memo is rewritten as a valid memo

### [AC-05] Memo path that cannot be used
- **Given** a directory at the memo path, or an unwritable `.devkit/transient/spec/`
- **When** a walk load runs
- **Then** the result equals a fresh build, no exception escapes, and the path is left as it was (the directory
  still exists, the unwritable directory's listing is unchanged)

### [AC-06] Concurrent writers
- **Given** a workspace with `.devkit/transient/` and documents being loaded
- **When** several processes load and write the memo at once
- **Then** every process returns a fresh build's result and the memo left behind decodes with the current
  fingerprint

### [AC-07] No memo where none belongs
- **Given** a workspace without `.devkit/transient/`, or one where `.devkit/transient/`, `spec/` or the memo path is
  a symbolic link
- **When** a walk load runs
- **Then** it returns a fresh build's result, creates no file or directory, and writes nothing through the link

### [AC-08] Writers and unchanged workspaces
- **Given** a workspace with a warm memo, including an unstorable document and an unreadable file
- **When** a walk load runs with no file changed, or any load runs with a supplied file list or reader
- **Then** the memo's bytes and modification time are unchanged, and a supplied-list load never creates a memo

### [AC-09] Fingerprint coverage
- **Given** the fingerprint module list
- **When** a document is read, parsed, encoded and decoded under a tracer
- **Then** every `devkit_spec` and `devkit_core` source file whose code runs is in the fingerprint, and a missing
  module fails the unit test

### [AC-10] Speed
- **Given** this repository with a warm memo, in one process environment
- **When** seven interleaved in-process `DocumentIndex.load` runs (one discarded warm-up) are timed against an
  identical copy of `docs/` and `specs/` without `.devkit/transient/`
- **Then** the warm median is at most 35% of the fresh median, and the Unit's `materials/speed.md` records both
  medians and the medians of seven `devkit spec resolve CAP-DOCS-document-model` and `devkit spec list feedback`
  runs with a warm memo next to the baseline, with the commit, Python and PyYAML versions

### [AC-11] Living Spec and boundaries
- **Given** the delivered change
- **When** `devkit rules check` runs
- **Then** it reports no violation, `CAP-DOCS-document-model` states the memo (key, location, silence, deletion is
  safe) and restates its Non-Goal as "a persistent source of truth", and `CAP-DOCS-document-lookup` notes that
  lookups reuse it

## 6. Assumptions

1. The speed evidence goes to the Unit's own `materials/speed.md`, not to
   `docs/materials/2026-10/20261022-document-index-cache/baseline-profile.md`, because the preserved proposal
   materials are outside this Development's write scope; the file quotes the baseline figures it compares against.
2. The multi-process check of AC-06 runs as a recorded script in `materials/speed.md` plus an in-process threaded
   integration test, because the write scope covers the unit and integration tiers and the e2e tier is outside it.
3. `CAP-DIST-workspace-ownership` is not changed: its `.devkit/transient/` listing names devkit-dist's own files and
   already omits other packages' entries.

## 7. Source feedback

- None addressed. `FB-strict-frontmatter-loader-without-libyaml` was recorded during Planning and stays open, out
  of scope (Non-Goal 2).
