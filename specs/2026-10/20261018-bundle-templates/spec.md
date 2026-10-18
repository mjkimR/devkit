---
id: SPEC-bundle-templates
title: Configurable bundle templates
summary: "Render Markdown templates using typed bundle variables without loading Jinja for ordinary commands."
status: completed
created: 2026-10-18
related_capabilities: [CAP-DIST-manifest-spec, CAP-DIST-sync-and-transactions]
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-bundle-templates] Configurable bundle templates

## Problem and user story

Projects need configurable response instructions without maintaining complete overrides. As a bundle author,
I want explicit template sources and declared variables so consumers can configure language reproducibly.

## Assumptions and boundaries

The first release supports Markdown instruction, guidance and document assets. Templates are identified only by
`.md.jinja`; ordinary files retain literal bytes. Bundle variables use identifier names and exact string, boolean
or integer types. Project values override optional manifest defaults. Missing required or unknown variables fail.
Overrides remain raw source files; templates render into managed files so consumers never read Jinja source.
The response-style catalog bundle is opt-in, independently written from user requirements, with language default auto.

## Non-Goals

- **Scope Excluded**: templated executable assets, native host configurations, skill/playbook/workflow entrypoints,
  constitution files, filenames, arbitrary config access, environment access, loaders, includes and custom functions.
- **Scope Excluded**: copying or translating third-party output-style text, publishing, or merging without approval.

## Acceptance Criteria

### [AC-01] Explicit template output
- **Given** an instruction, guidance or document with a .md.jinja source
- **When** the project synchronizes
- **Then** only the final .jinja suffix is stripped, rendered content is validated, and destination collisions fail before writes.

### [AC-02] Declared typed variables
- **Given** manifest variables and project bundles.<name>.variables values
- **When** inventory is planned
- **Then** only declared, correctly typed vars are exposed; defaults apply and invalid configuration fails before writes.

### [AC-03] Transaction and overrides
- **Given** a synchronized template with an optional raw override
- **When** variables or template source change
- **Then** dry-run and check detect final-byte changes, locked sync refuses receipt changes, repeated sync is unchanged,
  raw override digests remain tracked and context paths point to rendered managed files.

### [AC-04] Lazy restricted rendering
- **Given** ordinary commands or non-template sync
- **When** they execute in a fresh process
- **Then** jinja2 is absent from sys.modules; templates use StrictUndefined, no loaders, no globals, and restricted scalar access.

### [AC-05] Configurable response style
- **Given** the opt-in response-style catalog bundle
- **When** selected with language ko or its default auto
- **Then** its root guidance points to deployed concise-response instructions with the selected default conversation language.
