---
id: PLAN-adaptive-orchestration
spec: SPEC-adaptive-orchestration
---

# Technical Plan: `SPEC-adaptive-orchestration`

## 1. Constitution & Invariant Review

`CAP-DLV-adaptive-development` rule 13 and `CAP-DLV-adaptive-assignments` rule 5 encode the old depth cap.
`ADR-coordinator-led-adaptive-delegation` replaces that cap while retaining narrowed authority and child closure.
No package, feature edge or host-setting change is needed.

## 2. Architecture Overview & Impact

One bounded package change: adaptive guidance and assignment validation. The main agent owns orchestration;
subagents execute separable work. Direct execution remains appropriate where delegation adds no value.

## 3. Component & Interface Design

Remove fixed-depth/budget clauses from the entry, references and swarm contracts. Remove the CLI parent-depth guard.
Overlap validation exempts every ancestor in the selected parent's chain, while immediate-parent narrowing remains.
Existing assignment schemas, command flags and lifecycle are unchanged. Keep the legacy error class if needed for
import compatibility; stop emitting its obsolete depth refusal.

## 4. Error Handling & Edge Cases

A descendant cannot regain a commit grant or paths removed by its parent. Ancestor exemptions do not cover siblings,
unrelated assignments or out-of-scope writes. Existing direct-child completion checks apply recursively.

## 6. Verification & Test Plan

- AC-01/02: bundle validation, projection/instruction contract tests and targeted source review.
- AC-03/04: integration tests for a chain beyond the former limit, ancestor overlap, narrower grants, sibling overlap
  and bottom-up completion.
- Run lint/type checks, `just test-affected`, package build and applicable document/governance checks.
- Model adherence is unverified; no paid model experiment is required for this source/CLI change.
