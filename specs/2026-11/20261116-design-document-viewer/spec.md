---
id: SPEC-design-document-viewer
title: First-class formal documentation in the repository viewer
summary: "Makes formal design, domain and operations directly readable through canonical and alias links, reference context, source-safe artifacts and shipped viewer output."
status: in-progress
created: 2026-11-16
depends_on: [SPEC-formal-document-kinds]
related_capabilities: [CAP-VIEW-repository-viewer, CAP-DLV-release-handbook]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-design-document-viewer] First-class formal documentation in the repository viewer

## 1. Problem Statement & Motivation

The delivered formal core supplies identities and ownership. The browser viewer still lacks formal groups,
alias links, retirement controls, current reference context and byte-safe supporting files. Generic loading
alone does not establish support. The accepted blueprint `PROP-design-document-viewer-target` and its
[complete matrix](../../../docs/materials/2026-11/20261116-design-document-viewer/support-matrix.md) control V1–V4.

## 2. User Stories

- **US-1**: As a reader, I find each formal kind and follow canonical, alias and incoming/outgoing references.
- **US-2**: As a reader, I inspect a linked detail, image or datasheet and return to its exact source context.
- **US-3**: As a host, I consume the public library and shipped page with existing source callbacks.

## 3. Non-Goals

1. **Scope Excluded**: Core schema/governance or lifecycle changes; the core and lifecycle units own them.
2. **Scope Excluded**: Editors, recovery actions, new required host callbacks or Python document-engine dependency.
3. **Scope Excluded**: Handbook refresh/publication or automatic pages for every formal document.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Identity and navigation
- **Given** DESIGN, DOMAIN and OPS nodes in global and structural package roots, aliases and independent details
- **When** a reader browses, searches or follows a prose, code or direct reference
- **Then** explicit Domain/Designs/Operations groups and canonical/alias resolution work with core permissive IDs; ambiguous/missing targets stay unavailable and artifacts stay outside canonical navigation.

### [AC-02] Current and historical reading
- **Given** active and retired formal nodes, filters and namespace selection
- **When** normal browsing or a direct canonical/alias/reference link opens a node
- **Then** normal navigation hides retired nodes, Include retired exposes them, and a hidden direct target alone is materialized with its status and source context.

### [AC-03] Reference context and cold Files
- **Given** any indexed source with current typed/prose references and separately labelled provenance
- **When** a formal node opens in Read or cold rendered Files
- **Then** one shared panel shows metadata, incoming/outgoing canonical references, unresolved/ambiguous and incomplete/error/retry states; raw/artifact/handbook reads do not trigger an identity scan.

### [AC-04] Source-safe supporting files
- **Given** relative Markdown, image, CSV/diagram text or unsupported links from a document
- **When** they are read through the existing data source
- **Then** URI/path/source/abort context and bytes are preserved, safe images display, URLs are disposed, missing/unsupported states retain path and Back, and Planning never falls back to checkout.

### [AC-05] Source controls and maintenance routes
- **Given** a formal node and artifact after rename/root move/split/reclassification or retirement
- **When** a reader follows an alias or ordinary path and toggles raw/rendered or Back
- **Then** aliases find current identities, ordinary obsolete paths remain missing, source coordinates remain labelled, and parent context is retained without changing permissions.

### [AC-06] Backend, public and packaged parity
- **Given** the generic tree/blob backend and public RepositoryDataSource interface
- **When** actual formal/namespace/artifact fixtures, frontend checks, library packaging and wheel inspection run
- **Then** guards and bytes remain correct, public callbacks remain compatible, generated static output matches source and all required checks pass.

### [AC-07] Handbook and UX
- **Given** formal canonical IDs/aliases cited by a handbook author and the accepted screen drafts
- **When** source lookup/staleness and implemented reading interactions are checked
- **Then** all prefixes are recognized while CAP/UC required coverage and ADR/SPEC generated membership remain unchanged; use cases, UX register and current viewer contracts agree.

## 5. Screens and baseline

The three screen drafts and two completed pre-code UX rounds are retained in
`PROP-design-document-viewer-target`: UX-browse-formal-documents, UX-formal-document-relations and
UX-read-supporting-artifact. Implementation closes their retained findings against actual behavior.
The selected Read/book arrangement preserves existing style and handbook-first loading. No further direction
choice is needed. Baseline 5d1cb2661871cd3fe12cf806b58ac2515a3ffaf4 has zero explicit formal groups and no
formal relation panel; measure the head's three groups and shared Read/Files coverage, not performance.
