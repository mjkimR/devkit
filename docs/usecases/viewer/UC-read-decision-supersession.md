---
id: UC-read-decision-supersession
title: Read decision supersession
summary: "A developer inspects applied ADR replacement scope or proposed PADR replacements and follows related decisions while seeing source uncertainty."
area: viewer
primary_actor: Developer reading repository
supporting_actors: []
status: active
capabilities: [CAP-VIEW-repository-viewer]
entrypoints:
  - packages/devkit-viewer/frontend/src/lib/SddViewer.svelte
  - packages/devkit-viewer/frontend/src/lib/features/document/SupersessionSummary.svelte
  - packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.svelte
---

# [UC-read-decision-supersession] Read decision supersession

## 1. Goal

- **Goal**: Judge which clauses remain in force and open a related decision when needed.
- **Scope**: Repository viewer decision reading.
- **Trigger**: A developer opens an ADR or PADR.
- **Preconditions**: A repository is selected in the viewer.

## 2. Main Success Scenario

1. The reader opens an ADR in Read or rendered Files, or a PADR in Files or proposal detail (`CAP-VIEW-repository-viewer`, `UX-view-decision`).
2. The viewer displays the decision title, source context and body without waiting for relations (`CAP-VIEW-repository-viewer`, `UX-view-decision`).
3. The reader inspects applied ADR directions or outgoing proposed PADR replacements (`CAP-VIEW-repository-viewer`, `UX-view-decision`, `UX-decision-supersession`).
4. The reader follows a resolved related decision in the same viewer (`CAP-VIEW-repository-viewer`, `UX-view-decision`, `UX-decision-supersession`).
5. The reader finishes after seeing the replacement scope or source uncertainty (`CAP-VIEW-repository-viewer`, `UX-view-decision`).

## 3. Extensions

- **3a.** Relations are pending or some indexed documents failed: the viewer keeps the body readable, shows loading or incomplete source information and offers reload (`UX-view-decision`, `UX-decision-supersession`); reload resumes at step 3.
- **3b.** A target is missing/ambiguous or replacement scope is absent: the viewer shows the written identity without a broken link and makes missing scope explicit (`UX-view-decision`, `UX-decision-supersession`); reading continues at step 5.
- **4a.** The repository or branch changes: the viewer cancels the old context and presents the selected source without stale relation results (`UX-view-decision`); resumes at step 1.

## 4. Postconditions

- **Success guarantee**: The reader sees source-supported replacement scope and can open resolved targets.
- **Minimal guarantee**: The repository is unchanged and source uncertainty remains visible.

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Applied and proposed replacements

- **Covers**: main success scenario
- **Given**: ADR relations with whole/partial replacement and an outgoing PADR proposal.
- **When**: The reader opens each decision and follows a resolved relation.
- **Then**: ADR pages show both directions; PADR replacements remain proposed; the target opens in the same viewer.

### Scenario 2: Partial reads and retry

- **Covers**: 3a
- **Given**: The selected body is readable while a related source read fails.
- **When**: Relations finish and the reader reloads them after recovery.
- **Then**: The body stays available, failed paths and incompleteness are visible, and retry replaces the relation result.

### Scenario 3: Unavailable target or scope

- **Covers**: 3b
- **Given**: A missing or ambiguous target or an ADR with no replacement statement.
- **When**: The relation summary appears.
- **Then**: Unavailable targets have no link and missing replacement scope is explicit.

### Scenario 4: Source changes

- **Covers**: 4a
- **Given**: Relations for one source are pending.
- **When**: The reader changes repository or branch.
- **Then**: Only the selected source's body and relation result appear.
