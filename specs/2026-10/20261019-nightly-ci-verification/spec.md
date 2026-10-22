---
id: SPEC-nightly-ci-verification
title: Affected tests before merge and changed-head nightly CI
summary: "Use affected tests for local integration and run full CI nightly when the default branch differs from its last successful nightly verification."
status: completed
created: 2026-10-19
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-nightly-ci-verification] Affected tests before merge and changed-head nightly CI

## 1. Problem Statement & Motivation

Repeated full workspace tests slow development. Local integration should reuse affected-test results for the final
merged content; nightly and release CI provide full coverage for dependencies static selection cannot see.

## 2. User Stories

- **US-1**: As a coding agent, I want to verify the final integration content once with affected tests.
- **US-2**: As the maintainer, I want full CI overnight when changes remain unverified and before every release.

## 3. Non-Goals

- **Scope Excluded**: Changing test selection or its full-suite fallback, disabling lint/types/rules, triggering CI
  on every push/PR, publishing a release, or guaranteeing a precise GitHub schedule start time.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Changed-head nightly verification
- **Given** the default branch at the daily 04:17 Asia/Seoul schedule
- **When** no successful nightly workflow exists or its latest successful head differs from the scheduled head
- **Then** the complete reusable CI runs; otherwise its heavy jobs are skipped.

### [AC-02] Retry failures and fail closed
- **Given** the current head has failed or cancelled verification, or the run-history API fails
- **When** the nightly gate evaluates that head
- **Then** only a successful prior head can justify skipping; API errors fail the gate without reporting verification success.

### [AC-03] Explicit full verification
- **Given** a manual nightly run, direct manual CI run, or a release tag
- **When** the workflow executes
- **Then** full CI runs regardless of prior successful verification, and release publication still requires it.

### [AC-04] Verify the final integration content once
- **Given** the local branch is ready for review or integration
- **When** tests are required
- **Then** repository guidance uses test-affected without an additional mandatory full suite; it preserves full fallback
  and frontend checks, reruns affected tests after incorporating a moved base or resolving conflicts, and reuses results
  after a merge of unchanged verified content. Lint, type checks and governance still apply.

## 5. Assumptions

- The daily check uses 19:17 UTC on the previous UTC date, equivalent to 04:17 Asia/Seoul year-round.
- A separate nightly wrapper reuses the existing complete CI, leaving manual CI and release semantics intact.
- Run history is scoped to the wrapper and default branch; a prior skipped heavy job is safe only because the same
  head already had a successful complete wrapper run. Manual wrapper runs always perform full CI.
- Generic shipped skills follow the consuming repository's verification policy; devkit's nightly policy is repository-specific.
