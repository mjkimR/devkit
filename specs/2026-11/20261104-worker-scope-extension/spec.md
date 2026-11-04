---
id: SPEC-worker-scope-extension
title: Tiered write boundaries for delegated workers
summary: Splits a delegated worker's write boundary into an extensible estimate and a hard deny list, so a worker records and justifies an adjacent-path extension instead of stopping or having its whole result rejected, in local and cloud runs alike.
status: planned
created: 2026-11-04
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-worker-scope-extension] Tiered write boundaries for delegated workers

## 1. Problem Statement & Motivation

Estimated task boundaries omit necessary adjacent files. Development workers need to record those files while
preserving hard denies and Host acceptance. `ADR-recorded-adjacent-path-extensions-for-development-workers`
authorizes this change; the preserved implementation evidence records the Planning investigation.

## 2. User Stories

- **US-1**: A Development worker completes an existing task and AC through a necessary adjacent file with recorded
  evidence, without adding approval gates or changing sandbox, Git or publication authority.
- **US-2**: A Host verifies structural evidence across worker turns while a reviewer judges semantic adjacency,
  necessity, custom protected paths and test weakening.

## 3. Non-Goals

**Scope Excluded**: Planning-worker extensions, Hub changes or mandatory cloud inspect, ownership registries,
new policy configuration, sealed boundary journals, glob expansion, generic generated/lockfile admission,
new feature edges, unrelated work and changes to sync-output admission or approval gates.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Typed worker evidence
- **Given** an optional list of exact repository-relative files, positive scanner task ordinals, one-line reasons
  without parentheses and nonempty AC ID lists
- **When** authoring a worker with `--scope-extensions-file <file|->` and loading its record
- **Then** path/task/reason/requirements round-trip; malformed, duplicate, absolute, parent, glob, missing and
  other-kind values are refused before writing; existing records without the list remain valid.

### [AC-02] Additive task annotations
- **Given** task boundaries with literal file/directory prefixes and parenthesized notes
- **When** parsing `(scope extension: <reason>)` including commas and colons in its reason
- **Then** the scanner exposes exact-file annotations and task requirements additively, preserves existing values,
  skips fenced/comment examples and flags empty, nested-parenthesis and non-file extension annotations.

### [AC-03] Structural inspection across turns
- **Given** task annotations and applicable committed worker records
- **When** inspection audits a worker range
- **Then** top-level `scope_extensions` and `checks.scope_extensions` compare exact paths, owning task, matching
  reasons and AC ownership; the latest worker sequence wins repeated paths, prior-turn records remain relevant,
  and historical records alone admit no scope without a retained annotation.

### [AC-04] Denied paths and compatibility
- **Given** an unrecorded, mismatched or mechanically protected extension, or an outside-scope change
- **When** inspection runs
- **Then** invalid extension evidence fails with `SPEC_WORKER_SCOPE_EXTENSION_INVALID` and outside-scope changes
  with `SPEC_WORKER_SCOPE_OUTSIDE`; malformed inputs yield not-run evidence with a stable cause. Explicit `--scope`
  and `--scope-file` replace the entire scope, including a narrower override omitting an extension. Existing
  scope/outside_scope shapes, literal directory prefixes and independent sync-output admission remain intact.

### [AC-05] Shared worker and review contract
- **Given** local or cloud Development execution
- **When** an adjacent file is necessary for an existing task and AC
- **Then** the worker commits its exact-file annotation/reason with the first source commit and lists it in its
  sole final/emergency record; review checks annotation/task/AC before that record, and final Host/inspect compare
  them. Explicit denies prevail. Same-feature documented ownership/test mirrors and exact affected existing
  Living Spec documents qualify; other features/packages, new feature edges and protected classes require Host
  authority. Missing evidence is P2; denied/non-adjacent/out-of-goal writes are P1. No tool self-authorizes writes.

## 5. Assumptions & Baseline

Planning premises still hold at Development input `6ff819cec61cec40589b3ed90a8ea6c09a9eb6d9`; later base changes
are independently owned and require no contract change. Feature-owned modules and mirrored test tiers follow
`ARCH-05-2-components`; no new dependency edge is needed. Reasons are single nonempty lines without parentheses.
The parser baseline probe at this input exposes neither annotations nor typed records; the identical head probe
will demonstrate both. No timing or operator-cost outcome is claimed. Current Host write grants remain strict
throughout this implementation; the new feature grants no retroactive authority to this run.
