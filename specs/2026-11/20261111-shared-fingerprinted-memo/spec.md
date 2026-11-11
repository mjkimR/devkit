---
id: SPEC-shared-fingerprinted-memo
title: One fingerprinted memo store for docs parse and rule facts
summary: Moves the safe memo path check and the memo envelope shape check of the devkit-docs parse memo and the devkit-agt rule facts memo into one devkit-core helper, so path safety and envelope validation live once.
status: in-progress
created: 2026-11-11
related_capabilities: [CAP-DOCS-document-model, CAP-GOV-rules-engine]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-shared-fingerprinted-memo] One fingerprinted memo store for docs parse and rule facts

## 1. Problem Statement & Motivation

Handed off from proposal PROP-shared-fingerprinted-memo on 2026-11-11.
- **Preserved Materials**: `docs/materials/2026-11/20261111-shared-fingerprinted-memo`

Two fingerprinted memos, the devkit-docs parse memo (`CAP-DOCS-document-model` 3.4.3-3.4.5) and the devkit-agt rule
facts memo (`CAP-GOV-rules-engine` section 5), each implement the safe memo path check and the envelope shape check,
with different strictness: the facts memo checks every path component from `.devkit/` down and tolerates extra
top-level keys; the docs memo checks only `transient/`, `docs/` and the file and requires the exact key set. Every
hardening must be repeated in both. Source: `docs/materials/2026-11/20261111-review-refactor-code-pass/report.md` X-9;
the comparison is in `docs/materials/2026-11/20261111-shared-fingerprinted-memo/memo-comparison.md`.

## 2. User Stories

- **US-1**: As a maintainer, I want the memo path safety and envelope shape rules implemented once in
  `devkit_core.core`, so a hardening applies to both memos at once.
- **US-2**: As an agent running `devkit docs` or `devkit rules`, I want both memos to follow one documented path rule,
  so a memo is used under the same conditions in both.

## 3. Design

- New module `devkit_core.core.memo` (standard library only, beside `files.py` and `paths.py`; imported by its module
  path, not re-exported from `devkit_core.core`):
  - `safe_memo_path(root, parts, *, create) -> Path | PathRefusal`: `root` is the resolved workspace root, `parts` the
    path parts below `.devkit/transient/` ending in the file name. It returns `PathRefusal.NO_TRANSIENT` unless
    `.devkit/` and `.devkit/transient/` are existing directories that are not symbolic links and resolve to
    themselves; for each later directory component it returns `SYMLINK`, `NOT_DIRECTORY` or `MOVED` (resolves
    elsewhere), and `MISSING` for an absent one unless `create` is set, in which case it creates it; for the file it
    returns `SYMLINK` or `NOT_REGULAR` when one is there, else the path (the file need not exist). It never logs;
    an `OSError` from creating a directory or reading a component's status propagates.
  - `envelope_problem(loaded, version, fingerprint) -> EnvelopeProblem | None`: `None` for a mapping of exactly
    `version`, `fingerprint` and `entries` with an `int` (not `bool`) version equal to `version`, the fingerprint equal
    to `fingerprint` and a mapping of entries; else `SHAPE`, `VERSION` or `FINGERPRINT`, checked in that order (the
    entries type last, as `SHAPE`).
- docs memo: `ParseMemo.open` computes the fingerprint first, then calls `safe_memo_path` with `create` set for a
  writing load, and logs a refusal at `info` in its existing wording: `NO_TRANSIENT` and `MISSING` are silent,
  `SYMLINK` keeps "a symbolic link at <memo>", `MOVED` keeps "<memo> resolves outside <root>", `NOT_REGULAR` and
  `NOT_DIRECTORY` log "document memo <memo> not used: <reason>". An `OSError` from the call logs one "not used" line.
  `_read` uses `envelope_problem` and maps `FINGERPRINT` to its "another parser fingerprint" wording. Its parser
  fingerprint module list does not change.
- facts memo: `memo_path` keeps the rule-ID check and returns `None` for any refusal; `FactsStore` uses
  `envelope_problem` (a problem stays a silent miss). `_FRAMEWORK` adds the `devkit_core.core.memo` source.
- Kept local (Planning): fingerprints and their inputs, JSON parsing, entry shapes and codecs, serialization, writes,
  pruning, writer authority and logging levels and wording.

## 4. Non-Goals

1. **Scope Excluded**: sharing reads, serialization, writes, fingerprints or entry validation between the memos; any
   change to the memo locations, file formats, format versions or writer policy (`ADR-document-system`,
   `ADR-rules-run-workspace-cache`).
2. **Scope Excluded**: the non-finite JSON constant difference (the docs memo refuses `NaN`, the facts memo accepts it);
   it stays local with each JSON parse.
3. **Scope Excluded**: strictness parameters on the helper (decision D1: one rule for both memos).

## 5. Acceptance Criteria & Behavioral Contracts

### [AC-01] The path helper refuses every unsafe layout and creates only below transient
- **Given** a resolved root and the parts `("docs", "document-index.json")` or `("rules", "facts", "<id>.json")`
- **When** `safe_memo_path` runs against each layout: valid; missing, symbolic-link, non-directory `.devkit/` or
  `transient/`; a symbolic link, a non-directory or a missing directory below `transient/` (with and without
  `create`); a symbolic link or a directory at the file
- **Then** it returns the memo path for the valid layout (also when the file is absent) and exactly one `PathRefusal`
  per other layout (`NO_TRANSIENT`, `SYMLINK`, `NOT_DIRECTORY`, `MISSING`, `NOT_REGULAR`); with `create` it creates
  missing directories below `transient/` and never `.devkit/` or `transient/`; no log record is emitted
  (`packages/devkit-core/tests/unit/core/test_memo.py`).

### [AC-02] The envelope check accepts only the exact envelope
- **Given** parsed objects: the exact envelope, a non-mapping, a missing key, an extra top-level key, a `bool` or other
  version, another fingerprint and a non-mapping `entries`
- **When** `envelope_problem(loaded, 1, "<fp>")` checks each
- **Then** it returns `None` only for the exact envelope, `SHAPE` for the non-mapping, missing key, extra key and
  non-mapping `entries`, `VERSION` for the `bool` and other version and `FINGERPRINT` for another fingerprint
  (`packages/devkit-core/tests/unit/core/test_memo.py`).

### [AC-03] The docs memo keeps its outcomes except the converged path cases
- **Given** the fixture harness `evidence/memo_harness.py` and its table `evidence/before.md` recorded on the handoff
  head before any source edit
- **When** the harness runs on the changed head
- **Then** every docs row (writing load and file-list load) equals `before.md` in memo use, file effect and log
  records, except `symlink-devkit` (used before, not used after, no log line) and `non-directory-below` (one
  "not used" line instead of the "discarded" and "not written" lines); the existing `test_memo.py` and
  `test_memo_index.py` pass.

### [AC-04] The facts memo keeps its outcomes except extra top-level keys
- **Given** the same harness and table
- **When** the harness runs on the changed head
- **Then** every facts row (writer and reader) equals `before.md`, except `extra-key` (used before; not used after,
  and the writer rewrites the file); the existing `test_file_facts.py` passes, its `_FRAMEWORK` patch still
  controlling the facts fingerprint.

### [AC-05] Fingerprint coverage follows the moved checks
- **Given** the changed head
- **When** `_FRAMEWORK` and the docs `fingerprint_modules()` are read
- **Then** `_FRAMEWORK` names the `devkit_core.core.memo` source and `fingerprint_modules()` is unchanged; each memo
  written before the change is discarded once on the first run after it (a cold run).

### [AC-06] The contracts state the converged path rule
- **Given** `CAP-DOCS-document-model` 3.4.3 and `CAP-GOV-rules-engine` 5.3
- **When** they are read after the change
- **Then** both state that the memo is used only under an existing `.devkit/transient/` with no symbolic link,
  non-directory or relocated directory at any component from `.devkit/` down and a regular file (or none) at the memo
  path, and that a memo with any top-level key besides `version`, `fingerprint` and `entries` is discarded;
  `uv run devkit rules check --ci --base main` reports no violation.

## 6. Assumptions

- The docs memo's refusal of a non-directory component below `transient/` (fixture `non-directory-below`) is part of
  the converged rule D1 adopts ("a non-directory at every component"); it is listed beside the two D1 cases the
  proposal names.
- The docs `NOT_REGULAR` line moves from the first read to `ParseMemo.open`; for a file-list load that reads no
  document the line now appears where it did not. The harness rows match.
- Creating the docs `docs/` directory at open of a writing load replaces creation by `atomic_write_bytes` at save; a
  writing load with a missing file always writes, so the visible result is the same.
- The harness lives in the Unit's `evidence/` like earlier Units' measurement scripts, and runs each fixture in two
  child processes because the document index keeps parse results in process.
