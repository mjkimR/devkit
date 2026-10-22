---
id: SPEC-document-index-cache
title: Reuse the document index between commands
summary: Persists each Living Spec document's parse result on disk, keyed by its path and a digest of its parsed text, so lookups such as devkit spec resolve and list stop re-parsing every document on each call.
status: planned
created: 2026-10-22
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-document-index-cache] Reuse the document index between commands

## 1. Problem Statement & Motivation

Handed off from proposal PROP-document-index-cache on 2026-10-22.
- **Preserved Materials**: `docs/materials/2026-10/20261022-document-index-cache`

### 1. Background & Hypothesis

`devkit spec resolve <ID>` takes about 430 ms and `devkit spec list feedback` about 440 ms on this repository
(`docs/materials/2026-10/20261022-document-index-cache/baseline-profile.md`: 693 candidate files, 637 documents). Both build the full `DocumentIndex`
(`features/documents/repositories/index.py`) in a new process, and about 300 ms of each call is parsing: YAML
frontmatter through the strict pure-Python loader and the prose reference scan, for every document, even to resolve
one ID. Walking the tree takes 12 to 16 ms and reading every file 8 to 53 ms. Agents call these lookups many times per
task.

Hypothesis: a persisted parse memo, keyed by each file's path and a digest of the text parsed, makes the common call a walk, a
read, a hash and a memo decode (about 55 ms instead of 300 ms in the prototype), with results identical to a fresh
build by construction.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Reuse the document index between commands so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Which key is safe across checkouts, worktrees, branch switches and clock skew (mtime+size versus content
  hash), and where does the cache live (an ignored path inside the workspace, per worktree)?
  - **Answer**: the workspace-relative path plus a BLAKE2b digest of the exact text handed to the parser (after the
    reader's decoding and newline handling, since the walk and the rules reader turn CRLF bytes into different texts),
    under a parser fingerprint (`ADR-content-keyed-document-parse-memo`). It never consults timestamps, so clock
    skew, branch switches and timestamp-preserving copies cannot produce a stale result; it costs a read and a 2.5 ms
    hash per load, which a stat signature would skip at the price of a same-tick write race. The memo lives in
    `.devkit/transient/spec/document-index.json` of each worktree, the existing Git-ignored per-checkout state
    directory, as JSON with every container tagged rather than pickle (`ADR-parse-memo-location-and-format`).
- **Q2**: What happens on a corrupt, stale or concurrently written cache, and how does the index guarantee results
  identical to a fresh build?
  - **Answer**: any unreadable, malformed, other-version or other-fingerprint memo is treated as empty and any entry
    that cannot be rebuilt is a miss; the load parses as a fresh build would, silently (a `-v` log line), and rewrites
    the memo by atomic replace, never removing a non-regular file in its place. Writers take no lock and the last one wins; a lost update costs a later parse
    (`ADR-parse-memo-failure-and-write-policy`). Identity holds because an entry is reused only for the exact path
    and text it was parsed from, and everything derived (ID and alias maps, `historical`, problems, ordering) is
    rebuilt on every load.

### 3. Proposed Design & Impact

#### 3.1 Design

- `DocumentIndex.load` keeps its signature and its walk. For each file it reads the text as today, computes the
  digest of that exact text and takes the stored parse result on an exact path and digest match; otherwise it parses
  as today. The stored result covers a document, "no document", a malformed-frontmatter `SPEC_DOCUMENT_INVALID`
  reason and an "unstorable" marker; a file that cannot be read or decoded is reported as today and has no entry.
- The memo is `<root>/.devkit/transient/spec/document-index.json`, used only when `<root>/.devkit/transient/` is a
  real directory and no symbolic link leads the memo path out of `<root>`. It holds `version`, the parser
  `fingerprint` (format version, source bytes of the read, parse and codec modules in `documents.models`,
  `documents.repositories`, `devkit_core.core.frontmatter` and `devkit_core.base.errors`, PyYAML version, libyaml
  presence, Python version) and the entries, in JSON with every list, mapping, `date` and `datetime` tagged.
- Every load reads the memo; only a load that walks the workspace itself writes it, and only when an entry changed or
  the memo was discarded. Loads with a caller-supplied file list or reader (the spec rules, Git snapshots) read it
  and never write it.
- The in-process memo stays, so loads within one process (the rules of one run) still parse a text once.
- No command, option, output, code or exit status changes. In `CAP-DOCS-document-model` the Non-Goal "a persistent
  cache or database of documents" becomes "a persistent source of truth", the section 1 sentence "rebuilt from the
  files on every load" and the `index.py` module docstring are restated, and section 3.4 states the memo, its key,
  its location, its silence and that deleting it is safe; `CAP-DOCS-document-lookup` notes that lookups reuse it.
  `CAP-DIST-workspace-ownership` is not changed: its `.devkit/transient/` listing names devkit-dist's own files and
  already omits other packages' entries (`work/`, `mcp/`).

#### 3.2 Acceptance outcomes

1. **Identity**: for `list`, `search`, `resolve` and `refs` and for `DocumentIndex.load` itself, the results with a
   memo equal the results of a load without one after each of: a content edit (including a same-size edit whose
   mtime is restored), a new file, a deletion, a rename, an alias added, changed or removed, an ID change, a
   frontmatter turned malformed and back, a file turned non-UTF-8, a Git branch switch to a branch with other
   documents and back, and a changed parser fingerprint. CRLF, lone-CR and BOM documents loaded by a walk and by a
   rules-style supplied reader, in both orders, give the same `devkit rules check` reports and `devkit rules fix`
   results as without a memo. Frontmatter with dates, naive and aware datetimes, nested non-string keys and a
   tag-shaped mapping round-trips equal.
2. **Corruption**: a truncated memo, invalid JSON, another `version` or `fingerprint` and a malformed entry each give
   a fresh build's result, the same exit code, no advisory without `-v` and a rewritten valid memo; a directory at
   the memo path and an unwritable `.devkit/transient/spec/` give a fresh build's result and leave the path as it
   was.
3. **Concurrency**: several processes loading and writing at once in one worktree all return a fresh build's result
   and leave a memo that decodes.
4. **No memo where none belongs**: a workspace without `.devkit/transient/` behaves as today and gets no file or
   directory; a symbolic link at `.devkit/transient/`, `spec/` or the memo path is not followed; a load with a
   supplied file list never creates or changes the memo; an unchanged workspace leaves the memo's bytes and
   modification time unchanged, also with an unstorable document and an unreadable file present.
5. **Speed**: on this repository, in one process environment, the median of seven interleaved in-process
   `DocumentIndex.load` runs with a warm memo (one discarded warm-up) is at most 35% of the median for an identical
   copy of `docs/` and `specs/` without `.devkit/transient/` (prototype: 18%). The Unit's materials also record the
   medians of seven `devkit spec resolve CAP-DOCS-document-model` and `devkit spec list feedback` runs with a warm
   memo next to the baseline in `docs/materials/2026-10/20261022-document-index-cache/baseline-profile.md`, with the commit, Python and PyYAML versions.
6. **Boundaries**: `devkit rules check` reports nothing new; `RULE-proposal-boundaries` is clean for this proposal.

#### 3.3 Non-Goals

- `WorkspaceCache.get_catalog` and the rules workspace cache (devkit-agt): a generic catalog without the document
  model, which devkit-agt cannot share with devkit-spec.
- A faster strict YAML loader in `devkit_core.core.frontmatter`, a stat-signature fast path, and caching the search
  ranking or embeddings of `devkit spec search`.
- `devkit-viewer`, which reads documents from Git commits, not through `DocumentIndex`.
- Interpreter start-up and plugin import time (about 190 ms of `devkit --help`).

#### 3.4 Planning decisions

- `ADR-content-keyed-document-parse-memo`: key, stored result, fingerprint and reuse by every load.
- `ADR-parse-memo-location-and-format`: `.devkit/transient/spec/document-index.json`, JSON with tagged dates.
- `ADR-parse-memo-failure-and-write-policy`: discard rules, silence, writers, atomic replace without a lock.
- The challenger round (historical Git `1c1530663c983beed178b602a7b6be25dcffa08d:docs/proposals/PROP-document-index-cache/envelopes/challenger-01.yaml`) changed the key from a bytes digest to a digest of the
  parsed text, widened the fingerprint, replaced tagged dates with a fully tagged codec, added an "unstorable" marker
  and the non-regular-file and symbolic-link rules, defined the speed baseline and named the Living Spec edits.
- `dev_effort` stays `medium`: one package and its capability area, a local file that can always be deleted, no
  external contract change.

### 4. Lifecycle & Retirement Criteria

<!--
- Preliminary decisions: devkit spec proposal padr document-index-cache "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept document-index-cache --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff document-index-cache.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->

