---
id: SPEC-feedback-handoff-references
title: Preserve generic and historical references during proposal handoff
summary: Keep generic materials directory mentions intact and retain deleted envelope citations as Git-pinned historical references.
status: planned
created: 2026-10-20
related_capabilities: [CAP-DLV-proposal-incubation]
related_stories: []
workflow: sdd-spec-bugfix
---
# [SPEC-feedback-handoff-references] Preserve generic and historical references during proposal handoff

## 1. Problem Statement & Motivation

Handoff changes generic directory prose and leaves citations to deleted workflow envelopes dangling in promoted ADRs.

## 2. Defect Characterization

- **Current behavior**: a bundle-relative `materials/` span becomes a proposal-specific archive directory; an
  `envelopes/answer-01.yaml` citation remains after that workflow record is deleted.
- **Expected behavior and its basis**: `CAP-DLV-proposal-incubation` reference relocation preserves the meaning of
  carried documents. Generic directory spans stay generic, and deleted record citations identify recoverable Git
  evidence rather than a current file.
- **Behavior to preserve**: concrete material file spans, PADR IDs, Markdown links, record deletion, carried gates,
  fenced examples and frontmatter. Existing proposal handoff tests cover those paths.
- **Reproduction conditions**: pytest handoff tests with a nonempty materials directory and an accepted proposal
  with a committed answer envelope cited by its PADR.
- **Assumption**: pin only record bytes present unchanged at handoff HEAD. Without that evidence, leave the citation
  unchanged and report it unresolved; do not invent a historical source or broaden archival policy.

## 3. Non-Goals

1. **Scope Excluded**: changing approval decisions, preserving workflow records in materials, remote URLs, Git
   writes during handoff, general Markdown parser changes, unrelated feedback or ADR edits.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Preserve directory prose
- **Given** a proposal with material files and generic directory code spans
- **When** handoff carries its text and promotes its PADR
- **Then** directory-only spans remain unchanged, with no directory path rewrite reported.

### [AC-02] Preserve deleted record evidence
- **Given** a committed proposal envelope cited in a carried document by an inline path or relative Markdown link
- **When** handoff deletes the envelope
- **Then** the citation identifies historical Git evidence using the full HEAD commit and repository-relative path;
  the pinned bytes equal the deleted file, and the rewrite is reported.

### [AC-03] Keep surrounding behavior
- **Given** material file spans and links, PADR references, fenced examples and gate records
- **When** handoff runs
- **Then** concrete material references and IDs relocate, fenced examples remain unchanged, and records are dropped
  while existing gate carry behavior remains intact.

### [AC-04] Report unavailable history
- **Given** a cited envelope absent from HEAD or modified since HEAD, or no Git history
- **When** handoff runs
- **Then** the citation stays unchanged and is reported unresolved without a false historical pin.

### [AC-05] Repair existing citations
- **Given** the two accepted ADRs identified by the source feedback
- **When** their citations are corrected
- **Then** only the answer-envelope citations change to a full historical commit and path, with decisions unchanged.

## Source feedback

- `FB-handoff-rewrites-generic-materials-span`: directory prose preservation.
- `FB-promoted-adr-cites-deleted-proposal-envelope`: historical references and the two identified ADR citations.
