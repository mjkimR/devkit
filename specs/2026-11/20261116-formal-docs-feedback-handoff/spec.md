---
id: SPEC-formal-docs-feedback-handoff
title: Feedback lifecycle domain and proposal handoff design documents
summary: Add DOMAIN-feedback-lifecycle and DESIGN-proposal-handoff, the two medium-priority formal documents the coverage review found missing, written from current behavior.
status: completed
created: 2026-11-16
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-formal-docs-feedback-handoff] Feedback lifecycle domain and proposal handoff design documents

## 1. Problem Statement & Motivation

Two reader questions have no formal document. Their answers are spread across several owners, which each state their
own rule and none of which explains how the rules combine:

- **Feedback status.** The five feedback statuses (`open`, `promoted`, `resolved`, `dismissed`, `forwarded`) are
  defined in `CAP-DOCS-document-model` (Feedback lifecycle). Who changes them, and when, is spread over
  `CAP-DLV-proposal-planning` §3.1, `CAP-DLV-delivery-workflows` (Source feedback at completion),
  `CAP-HARN-agent-guidance` (Feedback capture policy) and the spec bundle's `spec-feedback` skill,
  `feedback-hygiene` playbook and `source-feedback.md` reference. Readers confuse `promoted` with `resolved` (both
  are terminal, only one claims a fix) and `dismissed` with `resolved`, and do not know when `forwarded` applies.
- **Proposal handoff.** `devkit spec proposal handoff` is specified rule by rule in `CAP-DLV-proposal-lifecycle` §4
  and the Host-authorized proposal lifecycle CLI section. No document walks the mechanism in source order on one real
  handoff, so a reader cannot see which check runs before the first write, what is rolled back and what is only
  reported afterwards.

`CAP-DOCS-documentation-ownership` §3.3 gives each reader question its own formal document that cites its owners and
moves no normative statement. The previous coverage unit `SPEC-formal-document-coverage` added six formal documents
and touched no index or README, since formal documents are found by ID and kind.

## 2. User Stories

- **US-1**: As an agent or maintainer, I want one domain entry that separates the feedback statuses and names who
  changes each, so that I set or read a status without reading five owners.
- **US-2**: As an agent or maintainer, I want one design that walks a real proposal handoff in source order, so that I
  can predict what a handoff writes, refuses, rolls back and reports.

## 3. Non-Goals

1. **Scope Excluded**: no code, capability, ADR, reference, steering, skill or playbook change; over-detail or a gap
   found in an owner is recorded as feedback, never trimmed or moved in this unit.
2. **Scope Excluded**: no index or README edit; formal documents are discovered by ID and kind.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Template structure
- **Given** `DOMAIN-feedback-lifecycle` and `DESIGN-proposal-handoff` at their canonical paths
- **When** each is read against its kind's template and writing instruction
- **Then** each has the required frontmatter (`id`, quoted `title`, `status`, quoted English `summary` of at most 300
  characters, `area`), a problem-first lead paragraph with at most one question sentence and no question section,
  `## Authority boundary` and `## Maintenance and next action` as its last two sections and 0 template HTML
  comments; the domain entry has `## Relationship overview` with a `Concept or relationship | Distinction |
  Authoritative owner` table and no `entrypoints`

### [AC-02] Feedback lifecycle content
- **Given** `DOMAIN-feedback-lifecycle`
- **When** it is read
- **Then** it covers the five statuses; distinguishes promoted from resolved, dismissed from resolved, and forwarded;
  names who changes a status and when (capture writes only `open`; Backlog triage through `feedback-hygiene`; a
  fixing spec or session at completion; promotion with its Disposition line); covers `recurring` and the recording
  lookup action per matched status; and has a relationship table and a worked example

### [AC-03] Proposal handoff content
- **Given** `DESIGN-proposal-handoff`
- **When** it is read
- **Then** it covers, in source order, the composed worktree creation, the preflight including the projected
  dependency graph check, bundle creation, body carry and heading classification, PADR to ADR promotion, the
  feedback and materials moves, ID-reference rewriting with `SPEC_PROPOSAL_REFS_REWRITTEN`, record carry, scope
  registration, the commit and rollback on failure, and has one worked example of a real handoff commit

### [AC-04] No restated authority
- **Given** each document
- **When** it is searched for RFC 2119 keywords, recovery text and term definitions
- **Then** 0 RFC 2119 keywords are its own rule, 0 advisory FIX/ACTION texts are copied, 0 glossary terms are
  defined, and every rule it relies on is cited by full ID and section; the authority boundary names
  `CAP-DOCS-document-model`, `CAP-DLV-proposal-planning`, `CAP-DLV-delivery-workflows` and `CAP-HARN-agent-guidance`
  for the domain entry, and `CAP-DLV-proposal-lifecycle` and `CAP-DLV-proposal-planning` for the design

### [AC-05] Current facts
- **Given** the Development head
- **When** each behavior claim (status, code, field, order, path) is compared with the current source, skill or
  capability, and the worked example with its commit
- **Then** every claim matches, and every cited source path and ID exists

### [AC-06] Checks and boundary
- **Given** the final diff against `cdbcdf224`
- **When** `uv run devkit rules check --ci --base cdbcdf224`, `just lint-check` and `git diff --check` run
- **Then** all exit 0, and no file outside the two documents and this unit directory changes

## 5. Assumptions

- `DOMAIN-feedback-lifecycle` is placed under `docs/domain/delivery/`: feedback statuses are changed by delivery
  activities (capture, Backlog triage, completion, handoff) owned by the delivery and harness capabilities; only the
  status vocabulary sits in the documents area. `docs/domain/documents/` does not exist yet, and
  `DOMAIN-delivery-relationships` already holds the neighbouring delivery concepts.
- The design's worked example uses the real handoff commit `93e72152c` that created `SPEC-formal-document-templates`, which
  exercises PADR promotion, a partial-supersession pointer, an open-feedback move, materials, a dropped-record
  citation and ID rewrites. It predates the own-path boundary omission (`cc42066c8`); the design states that
  difference instead of choosing a later handoff without a PADR.
