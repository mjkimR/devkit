---
id: SPEC-delete-resolved-feedback
title: Retire resolved feedback by deletion
summary: "Delete eligible resolved feedback during compaction while retaining other terminal outcomes as compact records."
status: completed
created: 2026-10-31
related_capabilities: [CAP-HARN-agent-guidance, CAP-DLV-delivery-workflows]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-delete-resolved-feedback] Retire resolved feedback by deletion

## 1. Problem Statement & Motivation

Resolved feedback accumulates after its fix is delivered. Git history retains its evidence; compaction can retire it without aliases.

## 2. User Stories

- As an agent, I can retire eligible resolved feedback while preserving the disposition of other terminal feedback.

## 3. Non-Goals

**Scope Excluded**: Automatic compaction, deletion of open or other terminal feedback without a compact record, and deletion of feedback protected by active work or references.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Delete eligible resolved feedback

- **Given** eligible resolved feedback, including an existing resolved compact record and its aliases
- **When** the user invokes feedback compaction
- **Then** the playbook deletes it without creating a summary or alias and retains the eligibility protections for active work and references.

### [AC-02] Preserve other outcomes

- **Given** eligible promoted, dismissed or forwarded feedback
- **When** feedback compaction runs
- **Then** it retains each outcome in a same-status compact record with aliases and verifies fidelity.

### [AC-03] Validate references

- **Given** an unresolved feedback ID in an explicitly checked document
- **When** the document reference rule runs
- **Then** it permits the reference in historical documents and reports it in active documents, including misspelled IDs.

### [AC-04] Record recurrence

- **Given** a recurring observation whose resolved feedback has been deleted
- **When** an agent records feedback
- **Then** the guidance directs it to record a fresh observation; existing resolved hits remain searchable until deleted.
