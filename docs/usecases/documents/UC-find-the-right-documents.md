---
id: UC-find-the-right-documents
title: Find the Right Documents
summary: "An AI coding agent finds the Living Spec documents relevant to a task, by exact ID, by reference, by owned code path or by meaning, within the right monorepo package, before it changes anything."
area: documents
primary_actor: AI coding agent
supporting_actors: []
status: active
capabilities:
  - CAP-DOCS-document-model
  - CAP-DOCS-document-lookup
  - CAP-DOCS-document-search
  - CAP-DOCS-namespaces
created_at: 2026-10-13
---

# [UC-find-the-right-documents] Find the Right Documents

## 1. Goal

- **Goal**: find the capabilities, use cases, decisions and specs that govern the code and the intent in front of the
  agent, and follow their references, without reading the whole `docs/` tree, so that the agent changes code against
  the current contract, cites documents by their exact IDs and spends its context budget only on documents that
  matter
- **Scope**: `devkit spec resolve`, `refs`, `list` and `search` over the document index
- **Trigger**: the agent starts or continues development work holding one handle: an ID quoted in a task or a review,
  a code path it is about to change, a free-text description of the intent, or a document it already has open
- **Preconditions**: the project uses the `spec` bundle with devkit-spec installed; the Living Spec documents may be
  written in any language and spread over several packages of a monorepo

---

## 2. Main Success Scenario

1. The agent resolves the cited ID (`CAP-DOCS-document-lookup`).
2. The system reports the document's kind, status and workspace-relative path, resolving the ID repository-wide
   whatever namespace is selected and an alias to its canonical document (`CAP-DOCS-document-lookup`,
   `CAP-DOCS-namespaces`).
3. The agent asks for the documents that reference the document, or that it references (`CAP-DOCS-document-lookup`).
4. The system lists each document on the other side with the fields that hold the references, one page at a time
   (`CAP-DOCS-document-lookup`, `CAP-DOCS-document-model`).
5. The agent reads the documents it needs and changes code against them, citing each by its exact ID
   (`CAP-DOCS-document-model`).

---

## 3. Extensions

- **1a.** The agent knows only the intent: it searches by meaning; the system ranks the current documents by ID and
  English summary, and by title, area and body lexically, and pins a document whose ID, alias, path or file name
  equals the query first; resumes at step 3 with the chosen hit (`CAP-DOCS-document-search`).
- **1b.** The agent holds a code path it is about to change: it lists the documents whose `entrypoints` equal the
  path, lie under it or contain it, which works for a deleted file too; resumes at step 3 with the listed document
  (`CAP-DOCS-document-lookup`).
- **1c.** The code path in 1b is absolute, a glob or has a `..` segment: the system refuses with
  `SPEC_ENTRYPOINTS_PATH_INVALID` before reading any document; the agent passes the workspace-relative path; resumes
  at 1b.
- **1d.** The agent works inside a registered package of a monorepo and browses: the system lists the current
  directory's namespace plus the global documents, each line with its namespace; resumes at step 1 with an ID from
  the listing (`CAP-DOCS-namespaces`).
- **1e.** The agent names a namespace that is not registered, or combines a namespace with all namespaces: the system
  refuses with `ARGUMENT_INVALID`, listing the valid names; resumes at 1d.
- **2a.** No document declares the ID: the system reports the resolved IDs first, then fails with
  `SPEC_ID_UNRESOLVED`; the agent searches by meaning; resumes at 1a.
- **2b.** Several documents declare the ID: the system fails with `SPEC_ID_DUPLICATE` and lists them; the use case
  ends, because a duplicate ID is fixed by hand.

---

## 4. Postconditions

- **Success guarantee**: the agent holds the exact IDs and workspace-relative paths of the governing documents and of
  the documents linked to them; completed spec bundles stayed out of the results unless the agent asked for history.
- **Minimal guarantee**: every lookup reads only and changes no file; a file the index cannot read is left out with a
  `SPEC_DOCUMENT_INVALID` warning while every other document stays usable; an unresolved or duplicated ID is reported
  by code, never guessed.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Resolves a cited ID and follows its references
- **Covers**: main success scenario
- **Given**: a review comment cites a capability by its full ID
- **When**: the agent runs `devkit spec resolve <ID>` and then `devkit spec refs <ID> --direction in`
- **Then**: it receives one `[DOCUMENT: ...]` line with the workspace-relative path, then one `[REF: ...]` line per
  document that references the capability, ending with `[PAGE: ...]`, and exits `0`

### Scenario 2: Finds documents by meaning across languages
- **Covers**: 1a
- **Given**: the agent knows only the intent ("keep references between documents valid"), and the documents carry
  English summaries while their titles and bodies are in another language
- **When**: it runs `devkit spec search "<intent>"`
- **Then**: the documents whose ID and summary match the intent rank among the top hits as `[HIT: ...]` lines, and an
  exact ID, path or file name in the query is pinned first with `score=-`

### Scenario 3: Finds the documents that own a code path
- **Covers**: 1b
- **Given**: the agent is about to change `src/<package>/engine.py`, and a capability declares `src/<package>/` in
  its `entrypoints`
- **When**: it runs `devkit spec list capability --file src/<package>/engine.py`
- **Then**: the capability is listed, even when the file has since been deleted

### Scenario 4: Refuses a code path outside the path contract
- **Covers**: 1c
- **Given**: any workspace
- **When**: the agent runs `devkit spec list --file '../src/*.py'`
- **Then**: the command fails with `SPEC_ENTRYPOINTS_PATH_INVALID`, exits `2` and prints nothing on stdout

### Scenario 5: Stays within a package without losing cross-package identity
- **Covers**: 1d
- **Given**: a monorepo registers the namespaces `api` and `web`, and the agent works under `services/api`
- **When**: it runs `devkit spec list` and then `devkit spec resolve` on an ID of the `web` package
- **Then**: `list` shows the `api` and global documents only, each line with `namespace=`, while `resolve` finds the
  `web` document, because IDs are repository-wide

### Scenario 6: Refuses an unknown namespace
- **Covers**: 1e
- **Given**: a monorepo that registers the namespaces `api` and `web`
- **When**: the agent runs `devkit spec list --namespace mobile`
- **Then**: the command fails with `ARGUMENT_INVALID` listing the valid names and exits `2`

### Scenario 7: Reports an ID no document declares
- **Covers**: 2a
- **Given**: a task cites one existing capability ID and one ID no document declares
- **When**: the agent runs `devkit spec resolve <existing> <missing>`
- **Then**: it prints the `[DOCUMENT: ...]` line of the existing ID, then fails with `SPEC_ID_UNRESOLVED` for the
  missing one and exits `2`

### Scenario 8: Reports an ID several documents declare
- **Covers**: 2b
- **Given**: two documents declare the same ID
- **When**: the agent runs `devkit spec resolve <ID>`
- **Then**: the command fails with `SPEC_ID_DUPLICATE`, its `[TARGET]` lists both documents, and it exits `2`
