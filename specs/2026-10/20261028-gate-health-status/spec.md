---
id: SPEC-gate-health-status
title: Expose gate hook warnings in project status
summary: "Include existing gate hook diagnostics in general project status through optional checks without a distribution dependency on the harness."
status: completed
created: 2026-10-28
related_capabilities: [CAP-DIST-sync-and-transactions, CAP-GATE-commit-gates]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-gate-health-status] Expose gate hook warnings in project status

## 1. Problem Statement & Motivation

General `devkit status` does not inspect Git gate hooks. Enabled gates can stop running after a dispatcher or
its entry is removed, while only `devkit gate status` reports `GATE_HOOK_ENTRY_MISSING`.
Existing gate inspection owns the diagnostic and its remediation. Distribution must stay usable without the harness.

## 2. User Stories

- **US-1**: As an agent inspecting a project, I want general status to include existing gate hook warnings so I can repair a silently disabled gate.
- **US-2**: As a distribution-only consumer, I want status to work without installing a harness.

## 3. Non-Goals

- **Scope Excluded**: executing gate rules, installing or repairing hooks, combining host hooks with Git hooks,
  changing gate diagnostics, or introducing a general health framework.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Existing diagnostics reach general status

- **Given** the harness is installed and enabled gates have a missing dispatcher, missing executable entry, or redirected `core.hooksPath`.
- **When** general project status runs.
- **Then** its `notices` includes exactly the diagnostics returned by existing gate hook inspection, retaining codes, levels, action and details; it executes no gate and changes no hook.

### [AC-02] Healthy and inapplicable projects

- **Given** healthy hook entries, all gates disabled, a directory outside Git, or no installed status-check provider.
- **When** general project status runs.
- **Then** no gate hook warning is added and distribution remains importable without the harness.

### [AC-03] Optional extension isolation

- **Given** providers registered in `devkit.status_checks`.
- **When** status runs.
- **Then** it calls each provider once in `(name, value)` order with the resolved project root, accepts only a list or tuple of `AdvisoryError` values at `WARNING` or `NOTICE`, and rejects a provider's entire result on invalid output.
- **Then** discovery, load, execution (including `SystemExit`) or validation failure adds an actionable `STATUS_CHECK_EXTENSION_FAILED` warning and preserves core status and other checks; `KeyboardInterrupt` propagates.

### [AC-04] CLI boundary semantics

- **Given** a gate or extension warning and no core status error.
- **When** general status runs normally or with `--strict`.
- **Then** it emits one JSON result and no stderr, exits `0` normally and `1` with `--strict`; existing core status errors still exit `1`.
- **Then** `devkit gate status` keeps its existing text/JSON behavior.

## 5. Baseline & Outcome

Compare the same disposable Git fixture at head with status-check discovery disabled and enabled. Record the
number of `GATE_HOOK_ENTRY_MISSING` notices for an overwritten hook, their equality to gate inspection, and
unchanged hook/config bytes. No checkout of the base is needed.

## Source feedback

`FB-gate-hook-problems-invisible-to-status`: expose existing gate hook problems in routine general status.
