---
id: SPEC-test-host-preflight
title: Check selected test host prerequisites before pytest
summary: "Checks local loopback availability for selected server tests before pytest and explains conditional wheel-build network requirements."
status: in-progress
created: 2026-11-04
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-test-host-preflight] Check selected test host prerequisites before pytest

## 1. Problem Statement & Motivation

`FB-full-suite-host-capabilities` records a restricted full run that spent 155 seconds before loopback binding and
isolated build dependency failures. The existing socketpair preflight cannot detect loopback binding denial.
The baseline is input commit e91c47ba: controlled denial of TCP bind does not affect that preflight.

## 2. User Stories

- **US-1**: As an agent running verification, I want a coded loopback failure before pytest when selected tests need
  a local HTTP server, and accurate guidance about build dependencies, so I can choose a permitted execution host.

## 3. Non-Goals

1. **Scope Excluded**: Internet connectivity probes, automatic approval or retry, skipped tests, dependency-cache
   management and a generalized host-capability registry.
2. **Scope Excluded**: Parsing pytest expressions or ignore flags to prove a narrower requirement. Unknown broad
   selections conservatively retain the full-suite preflight.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Loopback failure is early and actionable
- **Given** a full selection or a selection containing the viewer server or CLI tests and denied TCP bind
- **When** the recipe runs its preflight
- **Then** it exits 2 with `TEST_LOOPBACK_BLOCKED`, the exact quoted retry command, and no pytest invocation.

### [AC-02] Selected paths bound the additional check
- **Given** selected tests outside the known loopback consumers
- **When** `module.sh` launches the preflight
- **Then** socketpair validation remains active, but no TCP socket is created; module-relative, repository-relative,
  directory, node-id and full-fallback selections preserve the effective coverage.

### [AC-03] Supported hosts and existing errors remain compatible
- **Given** a permitted host or a blocked socketpair
- **When** the preflight runs
- **Then** success remains silent with exit 0 and closes its sockets, while socketpair denial retains
  `ASYNC_WAKEUP_BLOCKED` and exit 2; the script grants no permission and starts no retry.

### [AC-04] Build prerequisites are conditional and full fallback is preserved
- **Given** affected-test full fallback or isolated installed-consumer wheel builds
- **When** an agent reads the verification contract and the affected runner selects tests
- **Then** guidance explains dependency network access may be needed on a cold cache, no unconditional internet
  probe is introduced, and `test-affected` continues handing its full or selected paths to the recipe unchanged.

## Source feedback

- `FB-full-suite-host-capabilities`: direct fix of missing early loopback validation and prerequisite guidance.
