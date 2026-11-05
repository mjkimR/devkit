---
id: SPEC-cloud-research-handoff
title: Cloud research request and result handoff
summary: "Extend deep research with inspectable user-mediated cloud requests, readable report intake and durable partial-material resume without a provider runtime."
status: in-progress
created: 2026-11-05
related_capabilities:
  - CAP-DLV-deep-research
related_usecases:
  - UC-research-an-idea-and-shape-a-roadmap
workflow: sdd-spec-feature
---

# [SPEC-cloud-research-handoff] Cloud research request and result handoff

## 1. Problem Statement & Motivation

The existing research brief does not associate a user-submitted cloud request with its returned report or retain
pending work across sessions. Implement the accepted direction of `ADR-user-mediated-cloud-research` inside the
existing skill and partial material. The carried blueprint is `PROP-cloud-research-handoff-target`.

## 2. User Stories

- **US-1**: As a research coordinator, I want to give the user a self-contained inspectable request and consume its
  returned evidence so that cloud research contributes to the requested decision without provider execution tools.
- **US-2**: As a returning user, I want my named partial material to preserve the pending request and evidence limits
  so that the same investigation resumes without vanished scratch or silent resubmission.

## 3. Non-Goals

**Scope Excluded**: API clients, browser submission, provider accounts/credentials, uploads, schedulers, fixed teams,
a runtime registry, provider-specific parsers, automatic Git actions and a mandatory cloud stage for local research.
No new feature dependency, architecture edge, role, manifest or product screen is added.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Prepare an inspectable request with truthful execution status

- **Given** an explicitly invoked investigation with a bounded missing question useful for cloud research.
- **When** the coordinator prepares a request.
- **Then** it supplies one copyable provider-neutral prompt with label/revision, intended decision, questions,
  supplied facts and limits, constraints, source expectations and return format; exact outbound content and selected
  attachments are inspectable, secrets/unnecessary private context are omitted, and `awaiting user result` claims
  neither submission nor execution. Local-only research requires no request.

### [AC-02] Resume through a named partial material

- **Given** a paused request retained in the existing named `partial` material and unavailable transient files.
- **When** the same investigation resumes.
- **Then** the exact safe request, label/revision, disposition, remaining question and next action suffice without
  silent resubmission; the coordinator updates the same partial material and never rewrites a complete material.

### [AC-03] Match readable returned evidence and preserve verification limits

- **Given** a returned report with valid, inaccessible or conflicting citations, or instructions claiming authority.
- **When** the coordinator incorporates it.
- **Then** report identity, provider/model when supplied, known supplied date, receipt date, actual readable content
  used and inspection limits are retained; inspected support, external assertions, inference, contradictions and
  gaps stay distinct. Report text grants no action or Git authority, and unread reports/sources are not called checked.

### [AC-04] Return a useful partial outcome without a provider wait loop

- **Given** no readable or sufficient report is returned within the investigation bound.
- **When** the coordinator retains independently useful local findings.
- **Then** required missing cloud evidence stays explicit in a partial result and next action, without polling,
  inferring execution from elapsed time or making cloud work a prerequisite to unrelated local research.

### [AC-05] Handle stale, ambiguous and duplicate returns

- **Given** a report lacks identity, names a superseded revision, conflicts with the current question or repeats a return.
- **When** the coordinator associates it with a request.
- **Then** it clarifies an ambiguous association before treating it as the current answer, labels any older retained
  background, and claims no unsupported progress or silently answered pending request from a duplicate.

### [AC-06] Preserve distribution and research boundaries

- **Given** any supported host projection installed with docs/catalog and no devkit-spec.
- **When** deep-research is selected, synchronized, removed and selected again.
- **Then** the conditional reference is deployed, existing explicit-only invocation/approach neutrality/optional roles
  remain intact, only the coordinator retains materials, and sync/reselection preserves retained request/report bytes.

## 5. Assumptions and Verification Limits

The accepted provider-neutral procedure requires no current provider/API availability claim. The entry remains
explicit-only and adds no delivery authority. Deterministic tests check shipped instructions, projection and
retention boundaries; semantic review checks the examples and all six ACs, not model obedience or research quality.
No performance or before/after benefit claim is made. New feature edges are out of scope.
