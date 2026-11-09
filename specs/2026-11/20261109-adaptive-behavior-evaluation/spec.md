---
id: SPEC-adaptive-behavior-evaluation
title: Adaptive agent behavior evaluation
summary: Evaluate adaptive agent decisions with bounded execution scenarios and observable evidence, separately from asset packaging and projection checks.
status: planned
created: 2026-11-09
related_capabilities: [CAP-DLV-adaptive-development]
related_usecases: [UC-advance-an-idea]
workflow: sdd-spec-feature
---

# [SPEC-adaptive-behavior-evaluation] Adaptive agent behavior evaluation

## 1. Problem Statement & Motivation

Handed off from proposal PROP-adaptive-behavior-evaluation on 2026-11-09.

### 1. Background & Hypothesis

CAP-DLV-adaptive-development explicitly distinguishes semantic agent contracts from distribution checks.
`packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py` checks selection, projection, metadata,
context preservation and instruction content. These tests do not establish that an agent chooses sensible fanout,
respects recovery ownership in practice or refuses unsupported completion claims.

The hypothesis is that a small set of executable, evidence-scored scenarios can expose instruction regressions
without making ordinary deterministic package checks depend on hosted model availability.

#### Scope and exclusions

Design and deliver bounded behavioral evaluations for existing adaptive contracts and the proposed guidance in
PROP-adaptive-task-contracts and PROP-adaptive-evidence-repair. Exclude a new evaluation service or wheel,
mandatory hosted-model calls in ordinary tests, live credentials in fixtures, performance claims from packaging
checks, a runtime scheduler, production writes and new feature dependency edges.

## 2. User Stories

- **US-1**: As a maintainer, I want bounded, evidence-scored agent scenarios so that I can distinguish observed behavior from packaging checks and unavailable execution.

## 3. Non-Goals

1. **Scope Excluded**: A new evaluation service or wheel, mandatory model calls in ordinary tests, production writes, credentials in fixtures, a runtime scheduler, and new feature dependency edges.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Evidence-scoring entry
- **Given** a bounded scenario and its evidence supplied to the evaluation entry
- **When** the entry assesses that evidence
- **Then** it records scenario and source identity, observations, outcome and coverage limits, and never presents synthetic evidence as an observed agent run.

### [AC-02] Combined failure and missing evidence
- **Given** a trace in which child checks pass and the combined check fails or is missing
- **When** the scorer evaluates completion
- **Then** it reports fail for completion based only on child passes and inconclusive for a missing combined result.

### [AC-03] Interrupted writer
- **Given** an interrupted writer and its available artifacts
- **When** the evaluator assesses recovery
- **Then** it checks retained work, ownership and recovery from artifacts, marks incomplete evidence inconclusive, and preserves dirty work until retention or separately authorized removal.

### [AC-04] Unavailable execution
- **Given** host or model execution is unavailable
- **When** the evaluation runs
- **Then** it reports unavailable coverage and does not report a skipped run or scripted replay as a behavioral pass.

### [AC-05] Deterministic scorer checks
- **Given** compliant and violating fixtures without model credentials
- **When** ordinary package checks run
- **Then** they validate the scorer without model calls, and the scorer entry documents its inputs and limits.

## 5. Scope decision

The user directs completion without paid model calls or a live model feasibility prerequisite. Deliver deterministic evidence scoring and unavailable reporting in this unit. A scripted fixture validates the scorer only; it is not evidence of live agent behavior. No live runner or live execution claim is required. The earlier proposal notes below describe the original direction; where they conflict, this decision and the acceptance criteria govern.

