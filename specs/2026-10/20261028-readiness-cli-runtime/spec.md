---
id: SPEC-readiness-cli-runtime
title: Explain the running CLI reference in citation diagnostics
summary: "Clarify the running CLI reference and possible causes of missing commands or options without changing validation or integration behavior."
status: in-progress
created: 2026-10-28
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-readiness-cli-runtime] Explain the running CLI reference in citation diagnostics

## 1. Problem Statement & Motivation

The accepted guidance scope addresses the diagnostic part of `FB-readiness-cli-contract-checks-the-base-runtime`.
It does not deliver the broader integration runtime solution recorded in historical Planning materials.

## 2. Defect Characterization

- **Current behavior**: `RULE-cli-contract` reports an unknown command or option against the running Click tree.
  Its remediation tells the reader to correct the citation without explaining that the running runtime can be older
  than the cited interface. `cli_contract/rule.py` defines this shared remediation.
- **Expected behavior and its basis**: the accepted direction requires remediation to identify the currently
  running CLI as the reference and describe an invalid citation or an older runtime as possible causes.
  Lookup failure alone proves neither cause.
- **Behavior to preserve**: rule ID, severity, citation file/line/column, unknown command or option messages,
  failure and exit behavior, matching, settings, Click-root handling, providers, readiness, digests and authority.
  Existing rule-local tests cover citation extraction, matching, settings and the running root.
- **Reproduction conditions**: add a parameterized rule-local test using the existing Click fixture and a citation
  of either an unknown command or an unknown option. Assert the remediation explains both causes and the running CLI.
  Run that test before changing production code, then rerun it after the fix.

## 3. Non-Goals

- **Scope Excluded**: runtime selection, installation, launch or build; fingerprints, subprocesses, caches,
  root fail-closed behavior, integration behavior, whole-runtime wheel tests, consumer upgrades and cleanup tests.
- **Scope Excluded**: changing rule matching, options, lookup failures, settings, providers, readiness, digest or authority.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Missing interface guidance

- **Given** a citation of an unknown command or option in the running CLI fixture
- **When** `RULE-cli-contract` evaluates the citation
- **Then** its remediation identifies the currently running CLI as the reference, names an invalid citation or
  an older runtime as possible causes, and directs the reader to compare help with the intended interface.
  It does not claim that a runtime mismatch is proven.

### [AC-02] Preserve validation and consistent guidance

- **Given** the existing rule fixtures and the unknown command and option regression cases
- **When** the rule tests run
- **Then** existing validation results remain unchanged, each regression retains its rule ID, location, error
  severity and unknown command or option message, and the rule guide agrees with the remediation.

## 5. Assumptions & Source Feedback

- The current rule still uses the running Click tree, matching the accepted premise at the handoff base.
- Baseline measurement uses the head with the remediation change disabled: the narrow regression fails before
  the fix and passes after it. No runtime performance measurement applies to this text change.
- `FB-readiness-cli-contract-checks-the-base-runtime` is already promoted; this scope fully delivers diagnostic
  guidance and does not claim the underlying runtime mismatch is fixed.
