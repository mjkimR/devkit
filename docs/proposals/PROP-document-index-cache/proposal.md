---
id: PROP-document-index-cache
title: Reuse the document index between commands
summary: "Persists each Living Spec document's parse result on disk, keyed by its path and content digest, so lookups such as devkit spec resolve and list stop re-parsing every document on each call."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: documents/
priority: medium                       # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/documents/
    - packages/devkit-spec/tests/unit/features/documents/
    - packages/devkit-spec/tests/integration/features/documents/
    - docs/capabilities/documents/
  excludes:
    - docs/decisions/
    - packages/devkit/
    - packages/devkit-core/
    - packages/devkit-viewer/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-document-index-cache] Reuse the document index between commands

## 1. Background & Hypothesis

`devkit spec resolve <ID>` takes about 430 ms and `devkit spec list feedback` about 440 ms on this repository
(`materials/baseline-profile.md`: 693 candidate files, 637 documents). Both build the full `DocumentIndex`
(`features/documents/repositories/index.py`) in a new process, and about 300 ms of each call is parsing: YAML
frontmatter through the strict pure-Python loader and the prose reference scan, for every document, even to resolve
one ID. Walking the tree takes 12 to 16 ms and reading every file 8 to 53 ms. Agents call these lookups many times per
task.

Hypothesis: a persisted parse memo, keyed by each file's path and content digest, makes the common call a walk, a
read, a hash and a memo decode (about 55 ms instead of 300 ms in the prototype), with results identical to a fresh
build by construction.

## 2. Technical Spike Questions

- **Q1**: Which key is safe across checkouts, worktrees, branch switches and clock skew (mtime+size versus content
  hash), and where does the cache live (an ignored path inside the workspace, per worktree)?
  - **Answer**: the workspace-relative path plus a BLAKE2b digest of the file's bytes, under a parser fingerprint
    (`PADR-content-keyed-document-parse-memo`). It never consults timestamps, so clock skew, branch switches and
    timestamp-preserving copies cannot produce a stale result; it costs a read and a 2.5 ms hash per load, which a
    stat signature would skip at the price of a same-tick write race. The memo lives in
    `.devkit/transient/spec/document-index.json` of each worktree, the existing Git-ignored per-checkout state
    directory, as JSON with tagged dates rather than pickle (`PADR-parse-memo-location-and-format`).
- **Q2**: What happens on a corrupt, stale or concurrently written cache, and how does the index guarantee results
  identical to a fresh build?
  - **Answer**: any unreadable, malformed, other-version or other-fingerprint memo is treated as empty and any entry
    that cannot be rebuilt is a miss; the load parses as a fresh build would, silently (a `-v` log line), and rewrites
    the memo by atomic replace. Writers take no lock and the last one wins; a lost update costs a later parse
    (`PADR-parse-memo-failure-and-write-policy`). Identity holds because an entry is reused only for the exact path
    and bytes it was parsed from, and everything derived (ID and alias maps, `historical`, problems, ordering) is
    rebuilt on every load.

## 3. Proposed Design & Impact

### 3.1 Design

- `DocumentIndex.load` keeps its signature and its walk. For each file it reads the bytes, computes the digest and
  takes the stored parse result on an exact path and digest match; otherwise it decodes and parses as today. The
  stored result covers a document, "no document" and a `SPEC_DOCUMENT_INVALID` reason (malformed frontmatter or
  non-UTF-8); an `OSError` while reading is reported as today and never stored.
- The memo is `<root>/.devkit/transient/spec/document-index.json`, read and written only when
  `<root>/.devkit/transient/` is a real directory. It holds `version`, the parser `fingerprint` (format version,
  bytes of the `documents.models` modules and `devkit_core.core.frontmatter`, PyYAML version, libyaml presence,
  Python version) and the entries.
- Every load reads the memo; only a load that walks the workspace itself writes it, and only when an entry changed or
  the memo was discarded. Loads with a caller-supplied file list or reader (the spec rules, Git snapshots) read it
  and never write it.
- The in-process memo stays, so loads within one process (the rules of one run) still parse a text once.
- No command, option, output, code or exit status changes. The `CAP-DOCS-document-model` Non-Goal "a persistent cache
  or database of documents" becomes "a persistent source of truth", and its section 3.4 states the memo, its key,
  its location and that deleting it is safe; `CAP-DOCS-document-lookup` notes that lookups reuse it.

### 3.2 Acceptance outcomes

1. **Identity**: for `list`, `search`, `resolve` and `refs` and for `DocumentIndex.load` itself, the results with a
   memo equal the results of a load without one after each of: a content edit (including a same-size edit whose
   mtime is restored), a new file, a deletion, a rename, an alias added, changed or removed, an ID change, a
   frontmatter turned malformed and back, a file turned non-UTF-8, a Git branch switch to a branch with other
   documents and back, and a changed parser fingerprint.
2. **Corruption**: a truncated memo, invalid JSON, another `version` or `fingerprint`, a malformed entry, a directory
   in place of the file and an unwritable `.devkit/transient/spec/` each give a fresh build's result, the same exit
   code and no advisory without `-v`; where writable, the memo is rewritten valid.
3. **Concurrency**: several processes loading and writing at once in one worktree all return a fresh build's result
   and leave a memo that decodes.
4. **No memo where none belongs**: a workspace without `.devkit/transient/` behaves as today and gets no file or
   directory; a load with a supplied file list never creates or changes the memo; an unchanged workspace leaves the
   memo's bytes and modification time unchanged.
5. **Speed**: on this repository with an unchanged workspace, the median wall time of `devkit spec resolve
   CAP-DOCS-document-model` and `devkit spec list feedback` over seven runs is at most 60% of the same command
   without a memo, measured and recorded in the Unit's materials.
6. **Boundaries**: `devkit rules check` reports nothing new; `RULE-proposal-boundaries` is clean for this proposal.

### 3.3 Non-Goals

- `WorkspaceCache.get_catalog` and the rules workspace cache (devkit-agt): a generic catalog without the document
  model, which devkit-agt cannot share with devkit-spec.
- A faster strict YAML loader in `devkit_core.core.frontmatter`, a stat-signature fast path, and caching the search
  ranking or embeddings of `devkit spec search`.
- `devkit-viewer`, which reads documents from Git commits, not through `DocumentIndex`.
- Interpreter start-up and plugin import time (about 190 ms of `devkit --help`).

### 3.4 Planning decisions

- `PADR-content-keyed-document-parse-memo`: key, stored result, fingerprint and reuse by every load.
- `PADR-parse-memo-location-and-format`: `.devkit/transient/spec/document-index.json`, JSON with tagged dates.
- `PADR-parse-memo-failure-and-write-policy`: discard rules, silence, writers, atomic replace without a lock.
- `dev_effort` stays `medium`: one package and its capability area, a local file that can always be deleted, no
  external contract change.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr document-index-cache "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept document-index-cache --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff document-index-cache.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
