---
id: SPEC-feedback-guidance-clarifications
title: Clarify feedback-driven authoring guidance
summary: "Clarify existing review evidence, commit timing, UX closure and project style-source procedures without adding verdicts or CLI mechanisms."
status: planned
created: 2026-11-13
related_capabilities: [CAP-DLV-delivery-workflows, CAP-DLV-workflow-envelopes]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-guidance-clarifications] Clarify feedback-driven authoring guidance

## 1. Problem Statement & Motivation

Agents have workable review and authoring mechanisms, but the guidance omits concrete closure, evidence and commit
examples. The five Source feedback observations can be addressed without changing those mechanisms.

## 2. User Stories

- **US-1**: As an author, I want an executable sequence for draft review and commits so that task coverage passes.
- **US-2**: As a reviewer, I want check provenance and finding closure examples so that evidence stays attributable.
- **US-3**: As a UX author, I want a scoped project style source so that style decisions have one owner.

## 3. Non-Goals

1. **Scope Excluded**: Runtime, CLI, schema, check-verdict, stage, gate and review-round-count changes.
2. **Scope Excluded**: Mandatory or seeded style files, new presets, unrelated feedback and new feature edges.
3. **Scope Excluded**: Live model/host trials as a completion gate; empirical use is best effort.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Existing reconcile closure is actionable
- **Given** a reconcile-check with findings
- **When** the author reads the envelope and review-loop guidance
- **Then** an example uses a new reconcile-check, names the earlier record, records resolved/waived outcomes with waiver reasons, and preserves whole-round verification and non-waivable required contract mismatches.

### [AC-02] Check evidence keeps its executor and source
- **Given** passing caller evidence at an exact SHA that the reviewer did not rerun
- **When** the reviewer records its checks
- **Then** the guidance records SKIP with the source envelope and exact SHA, distinguishes supplied input from executed checks, and retains PASS/FAIL/SKIP only.

### [AC-03] Screens review precedes a covered combined commit
- **Given** uncommitted Screens and skeleton plan/tasks at specify
- **When** optional UX review runs
- **Then** the guidance names the last committed HEAD and uncommitted-draft assumption, folds findings before plan/tasks, and commits the spec, plan, tasks and associated review record together after task coverage passes.

### [AC-04] UX closure names build-verify
- **Given** at most two independent UX review rounds, including findings folded into drafts
- **When** Development verifies implementation
- **Then** the implementer records every last-round finding as resolved or waived at build-verify, including draft-fixed findings; the closure is not another independent review round and optional review remains optional.

### [AC-05] Missing style guidance respects project ownership
- **Given** a change deciding visual style with no steering style file
- **When** the UX author chooses a style source
- **Then** the guidance first uses an existing project style/token source or drafts a shared project-owned source within agreed scope, cites it from UX drafts, and requires no seeded file, fixed filename or out-of-scope write.

## 5. Assumptions and measurement

The accepted base already supports finding resolution/waiver, PASS/FAIL/SKIP and build-verify. Guidance fixes retain
those contracts, so no ADR is needed. This change has no operated screen of its own.

Baseline: accepted HEAD 021ad3c06c5ac0b3fffd8dad2fe931c2687db48e. Compare a deterministic five-scenario guidance
probe against file contents read with git show at that SHA and against the final source files, without checking out
the base. Record the failing baseline scenarios and passing head results in the final report. Native bundle tests
verify instruction contracts; live consumer/model trials remain unverified and best effort.

## Agreed scope

Clarify existing procedures for the five named sources. Preserve PASS/FAIL/SKIP, current task-coverage and commit boundaries, optional UX review and its two independent review rounds. Name build-verify for implementer closure and show how draft-fixed findings are reported there. Add no CLI, schema, new mandatory style file or preset. Explain existing resolved/waived finding fields in a new reconcile-check, preserving whole-round verification and non-waivable contract mismatches. Show source envelope and exact SHA for checks the reviewer did not rerun.

## Source feedback

- `FB-reconcile-check-no-per-finding-closure`: closing-record example using existing fields.
- `FB-envelope-check-status-vocabulary`: SKIP provenance example without a new verdict.
- `FB-specify-task-coverage-before-tasks`: complete Screens-to-plan/tasks commit sequence.
- `FB-ux-review-closure-stage-unnamed`: closing stage and previously folded findings.
- `FB-ux-writing-missing-style-file`: project-owned style source fallback within authorized scope.

The user selected direct fixes through spec/feedback-hygiene. Resolve only these five sources after implementation and verification; do not alter terminal or unrelated feedback. No dependencies on another active Unit are declared.
