---
id: PADR-content-keyed-document-parse-memo
title: Content-keyed document parse memo
summary: For repeated document lookups, we persist each document's parse result keyed by its path and a digest of its bytes under a parser fingerprint, to stay identical to a fresh build across edits, branch switches and clock skew, accepting a read and hash of every document per load.
proposal: PROP-document-index-cache
status: draft
created_at: 2026-10-22
---

# [PADR-content-keyed-document-parse-memo] Content-keyed document parse memo

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

Every `DocumentIndex.load` walks `docs/` and `specs/`, reads each Markdown file and parses its frontmatter and prose.
On this repository (693 candidate files, 637 documents) the load takes about 300 ms of the 430 ms that `devkit spec
resolve` needs; YAML loading and prose scanning are most of it, while the walk takes 12 to 16 ms and reading the files
8 to 53 ms (`materials/baseline-profile.md`). Each command is a new process, so the in-process memo that `index.py`
keeps, keyed by path and text, never survives between agent calls.

`CAP-DOCS-document-model` lists "a persistent cache or database of documents" as a Non-Goal because a second source of
truth can go stale. A persisted result has to keep that guarantee: a load must return what a fresh build returns.

## 2. Decision Drivers

- Results identical to a fresh build after edits, renames, deletions, alias changes and branch switches, in any
  worktree, independent of file timestamps and clocks.
- No second source of truth: the files stay the only input to what a load returns.
- Lookup latency in the common case, where no document changed since the last call.
- A parser change invalidates every persisted result without a manual version bump.

## 3. Considered Options

- **Keep rebuilding per load**: always correct, about 300 ms per call on this repository.
- **Stat signature (size, mtime, ctime, inode)**: skips reading unchanged files (10 to 50 ms more per call), but a
  write within one timestamp tick after the stat goes unnoticed on coarse-timestamp file systems, and guarding that
  race needs clock comparisons that clock skew on network file systems breaks.
- **Content digest per file**: every load still walks and reads every file and hashes its bytes (BLAKE2b, about
  2.5 ms here), then reuses the stored parse result when the path and digest match. Correct by construction: the
  parse result is a function of the path and the text, the identity the in-process memo already uses.
- **Persist the whole index under one tree key**: any edit rebuilds everything, and computing the tree key still
  needs per-file identity.

## 4. Decision Outcome

Chosen option: **content digest per file**, because it meets the identity and no-second-source drivers without any
timestamp or clock assumption, and the prototype cut the index load from about 310 ms to about 55 ms.

- **Entry key**: the workspace-relative path and the BLAKE2b digest of the file's bytes. A load reads every file the
  walk (or the caller's file list) yields, computes the digest and reuses the stored result only on an exact match;
  any other file is parsed again. A renamed file is a new path and is parsed again.
- **Stored result**: what parsing yields for that path and text: the `Document`, "no document" (no well-formed ID), or
  the `SPEC_DOCUMENT_INVALID` reason of a malformed frontmatter or a file that is not UTF-8. A read failure (`OSError`)
  is never stored.
- **Parser fingerprint**: one value for the whole memo, from a format version, the bytes of the parsing modules
  (`devkit_spec.features.documents.models` and `devkit_core.core.frontmatter`), the PyYAML version and whether libyaml
  is present, and the Python version. A different fingerprint discards the memo.
- **Derived state stays per load**: ID and alias maps, `historical`, ordering and problems are built from the entries
  on every load, exactly as today; only the per-file parse result is reused.
- **Scope of reuse**: every `DocumentIndex.load` reads the memo of its root, including loads with a caller-supplied
  file list and reader (the spec rules), because a content key is valid for any source of the text. Which loads write
  it is `PADR-parse-memo-failure-and-write-policy`.
- `WorkspaceCache.get_catalog` (devkit-agt) is not changed: it is a generic catalog without the document model, and
  `devkit-agt` cannot depend on `devkit-spec`.

## 5. Consequences

- Positive: a lookup in an unchanged workspace drops from about 430 ms to about 170 ms on this repository, and spec
  rule runs in a workspace with a memo skip parsing unchanged documents.
- Positive: branch switches, `git checkout` of old content, copies that keep timestamps and clock skew cannot produce
  a stale result; at worst a file is parsed again.
- Negative: every load still reads every document (8 to 53 ms here), which a stat signature would skip.
- Follow-up: if measurement on larger workspaces shows the read dominating, a stat signature can be added in front of
  the digest as a pure optimization, under a new decision.
- The Non-Goal in `CAP-DOCS-document-model` changes from "no persistent cache" to "no persistent source of truth": the
  memo holds derived parse results only and never decides which files exist.

## 6. Confirmation

- Tests in `packages/devkit-spec/tests/integration/features/documents/` compare loads with and without a memo after
  edits (including a same-size edit with a restored mtime), renames, deletions, alias and ID changes, malformed and
  non-UTF-8 files, a Git branch switch and back, and a changed fingerprint.
- A unit test fails when a module the parser imports is missing from the fingerprint.
