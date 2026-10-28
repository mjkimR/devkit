---
id: PLAN-readiness-cli-runtime
spec: SPEC-readiness-cli-runtime
summary: "Clarify shared CLI citation remediation and verify preserved rule behavior with focused regressions."
---

# [PLAN-readiness-cli-runtime] CLI citation diagnostic guidance

## 1. Constitution & Invariant Review

No invariant changes. `SPEC-readiness-cli-runtime` changes diagnostic explanation only.
Existing Click-root, settings, matching and integration contracts remain intact. No ADR is required.

## 2. Architecture Overview & Impact

Update only `REMEDIATION` in the built-in CLI-contract rule and its existing guide.
Keep unknown-command/option messages unchanged so callers retain their lookup facts.
Use the shared remediation because both failure kinds have the same possible causes.
The integration capability and operational reference describe separate runtime-import failures;
their existing guidance remains accurate and needs no edit.

## 6. Verification & Test Plan

Add one parameterized rule-local regression for missing command and option remediation before the fix.
Retain exact rule ID, location, severity and failure-message assertions (AC-01, AC-02).
Measure Red on the unchanged remediation and Green with the same test after the fix.
Run all CLI-contract tests, `just lint-check devkit`, `just check devkit`, and `just test-affected`
with its full fallback. Run `uv run devkit rules check --ci --base main` on committed content.
The author performs review and reconcile at low effort because the direction is fully settled.
