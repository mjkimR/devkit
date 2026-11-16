---
id: UC-read-formal-document
title: Read a formal document and its supporting context
summary: "A developer finds a design, domain or operations document, follows current or historical context and reads supporting files without losing the selected source."
area: viewer
primary_actor: Developer reading repository
supporting_actors: []
status: active
capabilities: [CAP-VIEW-repository-viewer]
entrypoints:
  - packages/devkit-viewer/frontend/src/SddViewer.svelte
  - packages/devkit-viewer/frontend/src/features/knowledge/KnowledgeViews.svelte
---

# [UC-read-formal-document] Read a formal document and its supporting context

## 1. Goal

- **Goal**: Reach the intended formal node or support file and understand its authority and source.
- **Scope**: Repository viewer reading.
- **Trigger**: A developer needs implementation, conceptual or operational context.
- **Preconditions**: A repository is selected.

## 2. Main Success Scenario

1. The reader requests the Living Spec book (`CAP-VIEW-repository-viewer`, `UX-browse-formal-documents`).
2. The reader selects a namespace/group, browses its area groups or searches for the needed context (`CAP-VIEW-repository-viewer`, `UX-browse-formal-documents`).
3. The viewer displays the selected canonical document and source context (`CAP-VIEW-repository-viewer`, `UX-browse-formal-documents`).
4. The reader inspects current references and historical origin, following a useful target (`CAP-VIEW-repository-viewer`, `UX-formal-document-relations`, `UX-browse-formal-documents`).
5. The reader opens an independent detail or selects a parent-linked supporting file from its inventory or body (`UX-formal-document-relations`, `CAP-VIEW-repository-viewer`, `UX-browse-formal-documents`, `UX-read-supporting-artifact`).
6. The reader returns to the prior reading context (`CAP-VIEW-repository-viewer`, `UX-browse-formal-documents`, `UX-formal-document-relations`, `UX-read-supporting-artifact`).

## 3. Extensions

- **2a.** No entries match: the viewer keeps filters visible; the reader clears or changes them and resumes at step 2 (`UX-browse-formal-documents`).
- **3a.** The target is retired or filtered: the viewer opens that explicit target with status without enabling unrelated history; resumes at step 3 (`UX-browse-formal-documents`).
- **3b.** A target is missing or ambiguous: the written identity remains unavailable; the reader reloads or returns to the list at step 2 (`UX-browse-formal-documents`).
- **4a.** Index reads or known metadata are incomplete: the body and successful rows remain readable; reload resumes at step 4 (`UX-formal-document-relations`).
- **4b.** A related identity cannot resolve: the written target has no arbitrary link; reading continues at step 3 (`UX-formal-document-relations`).
- **5a.** A file is missing or unsupported: the viewer retains path/source and explanation, with available raw/download and Retry/Back; Retry resumes at step 5 and Back at step 3 (`UX-read-supporting-artifact`).
- ***a.** The source changes: old reads and assets are cancelled/disposed; the selected source is shown under the existing request lifetime and the reader resumes at step 1 (`UX-browse-formal-documents`, `UX-read-supporting-artifact`).

## 4. Postconditions

- **Success guarantee**: The reader reaches the intended identified node/file with source and authority context.
- **Minimal guarantee**: The repository is unchanged and missing or incomplete evidence remains explicit.

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Three formal roles and details

- **Covers**: main success scenario
- **Given**: Global/package DESIGN, DOMAIN and OPS entries, aliases, detail and a supporting datasheet.
- **When**: The reader searches, inspects references, opens the file and returns.
- **Then**: The canonical context, file bytes and prior reading context remain available.

### Scenario 2: Search and direct history

- **Covers**: 2a, 3a
- **Given**: A query with no matches and a retired target hidden by normal navigation.
- **When**: The reader changes filters or opens the target explicitly.
- **Then**: Empty results retain filters; the selected historical target appears alone among hidden history.

### Scenario 3: Missing and ambiguous identities

- **Covers**: 3b, 4b
- **Given**: A missing or ambiguous canonical/alias target.
- **When**: A direct request or relation is inspected.
- **Then**: Its written ID remains visible without arbitrary navigation and the reader can return/reload.

### Scenario 4: Incomplete source and reload

- **Covers**: 4a
- **Given**: A readable subject and a failed peer read or malformed known metadata.
- **When**: Reference context is shown and reloaded after recovery.
- **Then**: Body/partial rows remain readable, uncertainty is explicit and retry replaces peer context.

### Scenario 5: Supporting file failures

- **Covers**: 5a
- **Given**: Missing or unsupported bytes beside a supported image/CSV/Markdown example.
- **When**: The reader opens each file.
- **Then**: Safe supported content appears; other states retain source/path, supported actions and Back.

### Scenario 6: Source replacement

- **Covers**: *a
- **Given**: A pending old-source artifact or index read.
- **When**: The repository/branch changes.
- **Then**: Old results cannot publish and old object URLs are disposed.


### Scenario 7: Delivered bundle support and area navigation

- **Covers**: Main success scenario 2–6.
- **Given**: DESIGN bundles and DOMAIN files in multiple areas, with nested parent-owned support and a peer bundle.
- **When**: The reader selects the canonical bundle entry and a supporting-list file.
- **Then**: Area groups and the canonical ID identify the parent; support opens in the same source and Back restores
  the parent. Support, nested stray identities and orphan files never appear as canonical documents.
