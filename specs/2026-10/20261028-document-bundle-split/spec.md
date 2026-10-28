---
id: SPEC-document-bundle-split
title: Install the document system without SDD
summary: Ships document formats, authoring guidance, templates and document rules in a docs bundle, independently of the spec bundle's SDD lifecycle assets.
status: planned
created: 2026-10-28
decomposed_from: PROP-document-layer-package
related_capabilities:
  - CAP-DOCS-document-model
  - CAP-DLV-delivery-workflows
  - CAP-GOV-spec-rules
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-document-bundle-split] Install the document system without SDD

## 1. Problem Statement & Motivation

Document implementations live in devkit-docs, but their distributable assets still require the spec bundle.
`ADR-document-and-sdd-bundles` selects independent docs and spec bundles so a document-only consumer does not
receive SDD lifecycle instructions. Existing SDD consumers retain their default behavior.

## 2. User Stories

- **US-1**: As a document consumer, I can install document formats, rules and guidance without SDD.
- **US-2**: As an SDD consumer, I retain lifecycle guidance and document checks through the default selection.

## 3. Non-Goals

- **Scope Excluded**: runtime lifecycle policy bypasses, incubation entry/support skills and SDD baseline transition.
- **Scope Excluded**: changing rule judgments, document vocabulary, generic distribution semantics or adding migration shims.
- **Scope Excluded**: automatically rewriting project-owned seeded files.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] document-only installation

- **Given** an isolated consumer environment with devkit-docs and its dependencies but no devkit-spec distribution.
- **When** sync and `get-context docs` run.
- **Then** docs core assets, its steering listing and pointer are installed, the nine document rules load, `devkit docs list|resolve|refs|search` remain available (lexical search requires no optional embedding runtime), and no spec asset, `/spec` skill, SDD workflow, SDD subagent or spec pointer is installed. Assert installed distributions and receipt ownership.

### [AC-02] existing SDD selection

- **Given** devkit-spec and default core selections.
- **When** sync runs.
- **Then** docs and spec core install together without duplicate asset or projection ownership. Shared formats and lifecycle workflows resolve all their template/instruction references. Original SDD gates, ADR retention and completed artifact preservation remain explicit in spec guidance. Existing proposal and lifecycle tests pass.

### [AC-03] steering and citations

- **Given** each selection.
- **When** contexts and rule explanations are read.
- **Then** steering documents are listed by docs exactly once and rule `related` references resolve to installed owning instructions. All shipped and projected references to moved assets point at docs; inventory assertions guard known lifecycle markers and review verifies semantics of neutral instructions/templates/seeded READMEs.

### [AC-04] optional skeleton

- **Given** docs core alone.
- **When** sync runs.
- **Then** no skeleton is seeded. When the user adds `docs:docs-skeleton`, absent document skeleton files are seeded with document-only guidance. A pre-existing seeded file keeps its bytes through reselection and sync. No old preset alias or migration reader is added.

### [AC-05] explicit selection

- **Given** both packages and defaults.
- **When** the user removes spec.
- **Then** spec's managed/projected assets and pointer are removed and docs remains usable. The guides explicitly distinguish selected assets from installed command extensions. Re-adding spec restores SDD guidance; no project setting or runtime policy bypass is inferred from asset removal.

### [AC-06] packaging and repository

- **Given** built wheels and this repository.
- **When** packages and assets are verified.
- **Then** Built wheels contain the assets they own and discover the correct bundle entrypoints. This repository selects both core bundles, syncs its tracked outputs and passes `devkit sync --check`, affected tests, lint, type checks and the cumulative governance check.
