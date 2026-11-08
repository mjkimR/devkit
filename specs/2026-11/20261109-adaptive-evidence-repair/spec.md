---
id: SPEC-adaptive-evidence-repair
title: Adaptive failure verification and bounded repair
summary: "Guides risk-based failure verification and evidence-driven recovery in adaptive development."
status: planned
created: 2026-11-09
related_capabilities: [CAP-DLV-adaptive-development]
related_usecases: [UC-advance-an-idea]
workflow: sdd-spec-feature
---

# [SPEC-adaptive-evidence-repair] Adaptive failure verification and bounded repair

## 1. Problem Statement & Motivation

The coordinator needs proportionate failure probes and useful recovery facts to advance `UC-advance-an-idea` without repeating unproductive repairs or claiming unverified behavior passed.

## 2. User Stories

- As a coordinator, I select probes from changed behavior and record actual evidence.
- As a resumed coordinator, I use retained recovery facts to choose a safe next action.

## 3. Non-Goals

- **Scope Excluded**: universal adversarial matrices, fixed QA pipelines, mandatory screenshots or scores, a new state store, transcript retention, automatic deletion, runtime retry engines and new feature edges.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Relevant verification

- **Given** a changed stateful operation,
- **When** the coordinator selects verification,
- **Then** it selects a normal path and relevant failure and integration probes and records expected signal, actual interaction, source identity, outcome and limitation.

### [AC-02] Probe classification

- **Given** a probe fails before valid product execution,
- **When** the coordinator assesses its cause,
- **Then** it identifies a harness or environment failure only on evidence, otherwise retains an unknown cause, and leaves product behavior unverified until a valid product probe passes.

### [AC-03] No-progress recovery

- **Given** repeated failures without material new evidence,
- **When** the assignment bound applies or two consecutive attempts have the same symptom without such evidence and no bound was supplied,
- **Then** the coordinator changes diagnostic strategy before another equivalent attempt or reports an unresolved blocker and next action if necessary work is unavailable.

### [AC-04] Resumable failed work

- **Given** a failed attempt affects the next action before interruption,
- **When** the Host checkpoints and later resumes,
- **Then** it retains the failed approach and reason, source identity, ownership, surviving hypothesis, retry condition and recovery action and rechecks applicability on resume.

### [AC-05] Proportionate evidence

- **Given** a low-impact stateless change,
- **When** choosing probes and notes,
- **Then** irrelevant failure scenarios and obsolete history may be omitted while existing context and active, dirty and unmerged work remain preserved.

## 5. Assumptions and Evidence

Material evidence changes or tests a causal hypothesis, isolates a dependency or identifies a distinct failure. The fallback is a diagnostic trigger, not a cap on authorized work or a completion condition. Walkthroughs test the guidance contract, not actual model behavior; unavailable live execution remains unverified.
