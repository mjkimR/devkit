---
id: SPEC-worker-inspection-fixes
title: Inspect partial worker turns with independent audit and governance bases
summary: Fixes scope inference before reconciliation exists and separates the accepted-turn write audit from cumulative feature governance without weakening either check.
status: planned
created: 2026-10-28
related_capabilities: [CAP-DLV-delivery-workflows]
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-worker-inspection-fixes] Inspect partial worker turns with independent audit and governance bases

## 1. Problem Statement & Motivation

Worker inspection loses usable scope before reconciliation exists and compares cumulative governance against the previous accepted turn. Hosts need both a narrow returned-turn audit and an accurate cumulative rules result.

## 2. Defect Characterization

- **Current behavior**: absent reconcile makes scope not-run; a second worker uses the first worker commit for both changed paths and rules, hiding an earlier-created reconciliation target from cumulative governance.
- **Expected behavior and its basis**: `CAP-DLV-delivery-workflows` describes task-derived write scope and cumulative rules evidence. Optional absent reconciliation adds no scope. Rules comparison remains cumulative while write auditing remains per-turn.
- **Behavior to preserve**: malformed present records remain not-run; required anchor/tasks remain required; dirty, stale head, outside-scope, blocked envelope and explicit audit-base behavior retain existing checks.
- **Reproduction conditions**: the worker inspector integration fixture commits two worker turns, with a contract created before worker one. Run the permanent regression tests before production changes.

## 3. Non-Goals

**Scope Excluded**: workflow completion gates, write-scope widening, rule weakening, unrelated feedback, archive behavior and repository tooling changes.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Inspect a partial turn without reconciliation
- **Given** a committed spec and tasks with no reconcile document
- **When** a worker turn is inspected
- **Then** scope runs using the unit, task boundaries and materials; outside-scope changes still fail.

### [AC-02] Preserve invalid and required input diagnostics
- **Given** malformed present reconciliation or absent required tasks
- **When** scope is derived
- **Then** scope is not-run with its cause and no successful scope result is fabricated.

### [AC-03] Keep accepted-turn auditing independent from cumulative rules
- **Given** two accepted worker turns on a branch with a recorded base
- **When** the second turn is inspected
- **Then** base, ancestry and changed paths use the previous worker commit while rules use the branch merge base and include the earlier-created target.

### [AC-04] Expose deterministic overrides and provenance
- **Given** explicit --rules-base, or a manual inspection with explicit --base and no recorded base
- **When** inspection runs
- **Then** rules use the resolved override or labelled audit-base fallback; invalid overrides exit 2; text and compact/full JSON retain the same resolved rules_base and value/source evidence.

### [AC-05] Preserve neighboring inspection checks
- **Given** dirty documents, a stale returned head or outside-scope edits
- **When** inspection runs
- **Then** existing failure and not-run statuses remain intact and no scope is broadened.

## 5. Baseline and Assumptions

Baseline is d5a74bd7cc977d30f7fe68cc765f64a9b5ba8ba1 with the fix disabled; permanent Red tests measure both defects before production changes. Existing merge-base resolution is reused without previous-worker handling. Manual fallback is used only when no recorded base branch is available, never to mask an invalid recorded reference.

## Source feedback

- `FB-worker-inspect-partial-turn-scope`: infer declared unit/task scope before optional reconcile exists; retain malformed-record diagnostics and stage requirements.
- `FB-worker-inspect-scoped-reconcile-base`: keep last-accepted turn write auditing distinct from cumulative feature rules comparison, with explicit input/provenance and tests.
