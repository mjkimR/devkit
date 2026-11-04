---
id: SPEC-namespace-steering-registers
title: Use global and selected namespace steering registers together
summary: "Places namespace glossaries and UX object registers beside namespace steering, retaining shared global context and namespace-scoped search synonyms."
status: completed
created: 2026-11-04
related_capabilities: [CAP-DOCS-namespaces, CAP-DOCS-document-search, CAP-GOV-spec-rules]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-namespace-steering-registers] Use global and selected namespace steering registers together

## 1. Problem Statement & Motivation

Namespace UX and steering documents are already separate, but their vocabulary consumers still name root-only
registers. The namespace steering rule rejects glossary files and keeps a second glossary layout outside steering.
Use the existing global-plus-selected-namespace convention consistently.

## 2. User Stories

- **US-1**: As an agent authoring namespace documents, I read shared definitions and local vocabulary together.
- **US-2**: As an agent searching a namespace, I use its synonyms without unrelated package synonyms leaking in.

## 3. Non-Goals

1. **Scope Excluded**: changing globally unique document IDs or cross-namespace reference resolution.
2. **Scope Excluded**: automatically moving or generating project glossary or UX register files.
3. **Scope Excluded**: adding a semantic UX-object checker; existing UX rules validate links and coverage, while
   object vocabulary is checked by agent review.
4. **Scope Excluded**: Viewer changes and reopening the completed namespace milestone.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Namespace steering accepts optional registers
- **Given** a registered namespace with glossary.md, glossary.yaml and ux-objects.md directly under steering/
- **When** steering validation and context discovery run
- **Then** Markdown registers follow the root frontmatter/count/size rules, YAML is accepted without counting as
  Markdown, and context lists root and selected namespace Markdown files only; an unregistered directory is unchanged.

### [AC-02] Namespace search includes shared and local synonyms
- **Given** global, api and web synonym files with shared-token clusters
- **When** search selects api explicitly or through its working directory
- **Then** expansion uses global followed by api synonyms, merges token collisions deterministically, and excludes web.

### [AC-03] Global and all-namespace search remain distinct
- **Given** registered api and web namespaces and optional synonym files
- **When** search selects global or every namespace
- **Then** global reads only root, every namespace reads root then registered namespaces sorted by name, absent
  files contribute nothing, and an unregistered directory contributes nothing.

### [AC-04] Invalid selected synonyms identify their actual file
- **Given** an invalid selected namespace glossary.yaml and valid unrelated files
- **When** search expands the query
- **Then** it exits 2 with DOCS_GLOSSARY_INVALID naming that namespace file in the target and fix; an invalid
  unselected namespace does not fail the search.

### [AC-05] Namespace glossary references and migration are explicit
- **Given** a registered namespace glossary and a legacy docs/packages/<name>/glossary.md
- **When** reference validation or steering validation targets the applicable file
- **Then** canonical glossary Owner references are validated and aliases fixed with the same behavior as root;
  the legacy path receives a non-fixable migration finding naming steering/glossary.md and no file is moved.

### [AC-06] Agents use shared and selected local registers together
- **Given** namespace glossary or UX register files exist
- **When** writing, drafting, reviewing or reconciling namespace UX and vocabulary
- **Then** docs and spec guidance reads root plus the selected namespace, writes local rows to the local file,
  applies local glossary definitions only to that namespace, and creates registers only when needed.

## 5. Source feedback

- `FB-namespace-ux-objects-copy`: namespace-local UX vocabulary and all actual agent consumers.
- `FB-package-glossary-asymmetry`: canonical glossary placement, reference checks and selected search synonyms.

## 6. Baseline and assumptions

Baseline is main commit 700c339bba8e89b4d70f63c5628d14d25bd3ffdd. Record focused RED tests before the
implementation and GREEN afterward; no base checkout is needed. No screen changes are part of this task.
The previous namespace steering decision requires partial supersession. No new feature edge is needed.
